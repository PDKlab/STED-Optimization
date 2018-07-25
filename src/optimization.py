
"""The module :mod:`optimization` contains the class :class:`optimization.Optimizer`
that allows the user to create the optimization routine.
"""

import shutil
import os
import functools
import warnings
import sys

import numpy

import skimage.io

import yaml

import algorithms
import customio
import microscope
import objectives
import user
import utils

from virtual import QualityNet, PrefNet


def sort_objectives(obj):
    """Sorts the objectives in a predefined order so that some objectives have a
    priority on the x axis.

    :param obj: A list of objectives name.

    :returns : The list of objectives name in the priority order.
    """
    priority = ['Quality', 'Quality_Last', 'Bleach', 'Autocorrelation', 'FRC', 'FWHM', 'Signal_Ratio']
    return [item for item in priority if item in obj]


class Optimizer:
    """This is the :class:`Optimizer` to run an optimization of the given parameters
    for the given objectives. The optimization uses the :class:`Kernel_TS` from
    the :mod:`algorithms` module.

    :param config: Dict of the configuration settings
    :param config_conf: The microscope configuration of the confocal image
    :param config_sted: The microscope configuration of the sted image
    :param autoquality: Boolean wheter or not to use the QualityNet to automatically
                        rate the images (default : false)
    :param autopref: Boolean wheter or not to use the PrefNet to use the auto preference
                     (default : false)
    :param thrash_data: Boolean wheter or not the user wants the opportunity to
                        thrash the data each imaging session (default : false)
    """

    def __init__(self, config, config_conf, config_sted, autoquality=False, autopref=False, thrash_data=False):
        # configuration
        self.config = config
        self.config_conf = config_conf
        self.config_sted = config_sted
        self.autoquality = autoquality
        self.autopref = autopref
        self.thrash_data = thrash_data
        self.t = 0

        self.params_name = [key for key in self.config["params"] if self.config["params"][key]]
        self.objectives_name = sort_objectives([key for key in self.config["objectives"] if self.config["objectives"][key]])
        self.params_space = self.create_params_space()
        self.params_set = self.create_params_set()
        self.avail_objectives = self.create_avail_objectives()
        self.noise_ub_objectives = self.config["noise_ub_objectives"]
        self.with_time = self.config["with_time"]
        self.pseudo_points = self.config["pseudo_points"]
        self.previous = self.config["output"]["previous"]
        self.output = self.create_output_dir()

        # initialize objectives, parameters space, and pre-train algorithms on previous knowledge
        self.objectives, self.space, self.algos = self.configure_optimization()
        
        if len(self.objectives) > 2 and self.with_time:
            print("WARNING: Disabling time objective because you have more than two objectives!")
            self.with_time = False

        if self.autopref:
            self.prefnet = PrefNet(self.config["autopref"]["IP"], self.config["autopref"]["port"])

    def run(self, readjust):
        """Runs the optimization routine. The user is asked to select
        a number of regions with the :mod:`matplotlib` figure. The algorithms samples
        the parameter space and the user is asked to decide on the tradeoff to make
        in the :mod:`matplotlib` figure. The parameters are selected and a STED image
        is taken. The objectives are evaluated on the images and the algorithms
        are updated with the new knowledge. A regression of the current data is
        done and the images are saved in the output folder.

        :param readjust: Boolean, wheter or not to readjust focus between the first
                         confocal and the STED image.
        """
        linestep = microscope.get_linestep(self.config_sted, self.config["params_set"]["Line_Step"])
        if self.with_time:
            idx = self.params_name.index("Dwelltime")
            timesperpixel = linestep * self.space[:, idx]
        else:
            timesperpixel = linestep * microscope.get_dwelltime(self.config_sted)

        regions = user.get_regions()
        for (x, y) in regions:
            microscope.set_offsets(self.config_conf, x, y)
            microscope.set_offsets(self.config_sted, x, y)

            # acquire a confocal image
            stacks, _ = microscope.acquire(self.config_conf)
            cimg1 = stacks[0][0]
            if len(stacks) > 1:
                cimg1_others = [stack[0] for stack in stacks[1:]]
            else:
                cimg1_others = []

            # readjust focus is needed
            if readjust:
                input("Manually adjust the focus in the overview window then press enter.")
                # reacquire the confocal image
                stacks, _ = microscope.acquire(self.config_conf)
                cimg1 = stacks[0][0]
            readjust = False

            o_t = [algo.sample(self.space) for algo in self.algos]

            if self.autopref:
                if self.with_time:
                    i_t = self.prefnet.predict(numpy.hstack((numpy.array(o_t).T, timesperpixel[:, None])))
                else:
                    i_t = self.prefnet.predict(numpy.array(o_t).T)
                i_t_fla = -1
                # i_t_fla = user.select(o_t, self.objectives, self.with_time, timesperpixel) # for debug
            else:
                if len(self.objectives) > 1:
                    i_t = user.select(o_t, self.objectives, self.with_time, timesperpixel)
                else:
                    i_t = self.objectives[0].select_optimal(o_t)
                i_t_fla = i_t

            p_t = self.space[i_t]
            print("Selected parameters", p_t)

            # acquire a STED stack using the selected parameter(s)
            for label, value in zip(self.params_name, p_t):
               # using .item() to convert from Numpy type to standard Python type
                self.params_set[label](self.config_sted, value.item())
            stacks, _ = microscope.acquire(self.config_sted)
            sted_stack = stacks[0]
            if len(stacks) > 1:
                sted_stack_others = stacks[1:]
            else:
                sted_stack_others = []

            # foreground on confocal image
            fg_c = utils.get_foreground(cimg1)
            # foreground on sted image
            fg_s = utils.get_foreground(sted_stack[0])
            # remove STED foreground points not in confocal foreground, if any
            fg_s *= fg_c

            # acquire a confocal in the end
            stacks, _ = microscope.acquire(self.config_conf)
            cimg2 = stacks[0][0]
            if len(stacks) > 1:
                cimg2_others = [stack[0] for stack in stacks[1:]]
            else:
                cimg2_others = []

            if self.thrash_data:
                answer = input("Do you want to keep data? (y/n)")
                while answer not in ["y", "n"]:
                    print("Sorry, what did you say?")
                    answer = input("Do you want to keep data? (y/n)")
                if answer == "n":
                    print("TRASHING DATA")
                    continue

            # evaluating the objectives
            r_t = [obj.evaluate(sted_stack, cimg1, cimg2, fg_s, fg_c) for obj in self.objectives]
            if None in r_t:
                print("TRASHING DATA: None value in rewards!", r_t)
                continue

            for algo, reward in zip(self.algos, r_t):
                algo.update([p_t], [reward])

            with warnings.catch_warnings():
                # ignore low-contrast image warnings
                warnings.simplefilter("ignore")
                skimage.io.imsave(os.path.join(self.output, "Confocal1", "{}.tiff".format(self.t)), cimg1)
                skimage.io.imsave(os.path.join(self.output, "Confocal2", "{}.tiff".format(self.t)), cimg2)
                if len(sted_stack) > 1:
                    for i, img, in enumerate(sted_stack):
                        skimage.io.imsave(os.path.join(self.output, "STED", "{}_{}.tiff".format(i, self.t)), img)
                else:
                    skimage.io.imsave(os.path.join(self.output, "STED", "{}.tiff".format(self.t)), sted_stack[0])

                for i, img in enumerate(cimg1_others):
                    skimage.io.imsave(os.path.join(self.output, "Confocal1_Others", "{}_{}.tiff".format(i, self.t)), img)
                for i, img in enumerate(cimg2_others):
                    skimage.io.imsave(os.path.join(self.output, "Confocal2_Others", "{}_{}.tiff".format(i, self.t)), img)
                for i, stack in enumerate(sted_stack_others):
                    if len(stack) > 1:
                        for j, img, in enumerate(stack):
                            skimage.io.imsave(os.path.join(self.output, "STED_Others", "{}_{}_{}.tiff".format(i, j, self.t)), img)
                    else:
                        skimage.io.imsave(os.path.join(self.output, "STED_Others", "{}_{}.tiff".format(i, self.t)), stack[0])

            # for plotting regression in multi-parameters optimization
            if len(self.params_name) > 1:
                for i, param_label in enumerate(self.params_name):
                    X_pred = numpy.empty((len(self.params_space[param_label]), len(self.params_name)))
                    X_pred[:, i] = self.params_space[param_label]
                    for j, value in enumerate(p_t):
                        if j != i:
                            X_pred[:, j] = value
                    utils.plot_regression(self.objectives, self.algos, X_pred, i, param_label, self.output, self.t)
            else:
                utils.plot_regression(self.objectives, self.algos, self.space, 0, self.params_name[0], self.outptut, self.t)

            with open(os.path.join(self.output, "X"), "a") as f:
                f.write("{},{}\n".format(self.t, ",".join(map(str, p_t))))
            with open(os.path.join(self.output, "y"), "a") as f:
                f.write("{},{}\n".format(self.t, ",".join(map(str, r_t))))
            with open(os.path.join(self.output, "Options", "choices"), "a") as f:
                f.write("{},{},{}\n".format(self.t, i_t, i_t_fla))
            if self.with_time:
                options = numpy.hstack((numpy.array(o_t).T, timesperpixel[:, None]))
            else:
                options = numpy.array(o_t).T
            numpy.savetxt(os.path.join(self.output, "Options", str(self.t)), options, delimiter=",")

            self.t += 1

    def create_output_dir(self):
        """Creates every saving folder and also saves the important configuration
        for future reference.

        :return: The output directory path
        """
        output = os.path.join(
            self.config["output"]["saving_dir"], self.config["output"]["folder"])
        # creates every folders to save the future results
        try:
            os.makedirs(output, exist_ok=False)
            os.makedirs(os.path.join(output, "Confocal1"), exist_ok=False)
            os.makedirs(os.path.join(output, "Confocal2"), exist_ok=False)
            os.makedirs(os.path.join(output, "STED"), exist_ok=False)
            os.makedirs(os.path.join(output, "Confocal1_Others"), exist_ok=False)
            os.makedirs(os.path.join(output, "Confocal2_Others"), exist_ok=False)
            os.makedirs(os.path.join(output, "STED_Others"), exist_ok=False)
            os.makedirs(os.path.join(output, "Regression"), exist_ok=False)
            # for storing options (tradeoffs) presented to the user
            os.makedirs(os.path.join(output, "Options"), exist_ok=False)
        # to avoid overwriting previous optimization
        except OSError as err:
            print("The folder already exists. Consider changing the name of the saving directory.")
            print("OSError:", err)
            exit()
        print("Results will be in", output)

        # copy optimize.py to results folder
        shutil.copyfile(os.path.realpath(__file__), os.path.join(
            output, os.path.basename(__file__)))

        # saving the configuration parameters
        with open(os.path.join(output, "config"), "w") as f:
            config = {"script": os.path.basename(__file__),
                      "params": self.params_name,
                      "space": {p: self.params_space[p].tolist() for p in self.params_name},
                      "objectives": self.objectives_name,
                      "with_time": self.with_time,
                      "pseudo_points": self.pseudo_points}
            yaml.dump(config, f)

        # saving the microscope confocal configuration
        with open(os.path.join(output, "imspector_config_confocal"), "w") as f:
            config = self.config_conf.parameters("")
            yaml.dump(config, f)

        # saving the microscope sted configuration
        with open(os.path.join(output, "imspector_config_sted"), "w") as f:
            config = self.config_sted.parameters("")
            yaml.dump(config, f)

        return output

    def create_params_space(self):
        """Creates the parameters space with the values from the configuration dict.

        :return: A dict of the parameter space.
        """
        params_space = {}
        c = self.config["params_space"]
        for key in c:
            if key in ["Line_Step", "Rescue/Signal_Level"]:
                params_space[key] = numpy.arange(c[key][0], c[key][1], c[key][2])
            else:
                params_space[key] = numpy.linspace(c[key][0], c[key][1], c[key][2])
        return params_space

    def create_params_set(self):
        """Creates the functions to change the microscope parameters from the
        configuration dict.

        :return: A dict of the parameters set.
        """
        c = self.config["params_set"]
        params_set = {"Dwelltime": microscope.set_dwelltime,
                      "Exc/Power": functools.partial(microscope.set_power, laser_id=c["Exc/Power"]),
                      "STED/Power": functools.partial(microscope.set_power, laser_id=c["STED/Power"]),
                      "Line_Step": functools.partial(microscope.set_linestep, step_id=c["Line_Step"]),
                      "Rescue/Signal_Level": functools.partial(microscope.set_rescue_signal_level, channel_id=c["Rescue/Signal_Level"]),
                      "Rescue/Strength": functools.partial(microscope.set_rescue_strength, channel_id=c["Rescue/Strength"])}
        return params_set

    def create_avail_objectives(self):
        """Creates the available objectives.

        :return: A dict of the available objectives
        """
        c = self.config["objectives_values"]
        avail_objectives = {"Signal_Ratio": objectives.Signal_Ratio(c["Signal_Ratio"]),
                            "Autocorrelation": objectives.Autocorrelation(),
                            "FWHM": objectives.FWHM(microscope.get_pixelsize(self.config_sted)[0]),
                            "Bleach": objectives.Bleach(),
                            "FRC": objectives.FRC(c["FRC"])}
        if self.autoquality:
            avail_objectives["Quality"] = objectives.ScoreNet("Quality", QualityNet(self.config["autoquality"]["IP"], self.config["autoquality"]["port"]))
            avail_objectives["Quality_Last"] = objectives.ScoreNet("Quality", QualityNet(self.config["autoquality"]["IP"], self.config["autoquality"]["port"]))
        else:
            avail_objectives["Quality"] = objectives.Score("Quality")
            avail_objectives["Quality_Last"] = objectives.Score("Quality", -1)
        return avail_objectives

    def configure_optimization(self):
        """Configures the optimization with the given parameters and the objectives.
        It creates the dedicated algorithm for every objective and trains the algorithms
        if previous knowledge is given

        :return: The objectives to optimize, the parameter space and the dedicated algorithms
        """
        objectives = [self.avail_objectives[obj] for obj in self.objectives_name]

        # create the parameter space
        grid = numpy.meshgrid(*[self.params_space[p] for p in self.params_name])
        space = numpy.vstack(map(numpy.ravel, grid)).T

        # set bandwidth with rule of thumb
        ratio = len(self.params_name) / 3
        bandwidth = [(self.params_space[p][-1] - self.params_space[p][0]) * ratio
                     for p in self.params_name]
        if self.pseudo_points:
            # for adding pseudo-actions
            space_bounds = [(self.params_space[p][0], self.params_space[p][-1])
                            for p in self.params_name]
            algos = [algorithms.Kernel_TS_PseudoActions(bandwidth, 1e-3, self.noise_ub_objectives[obj], space_bounds)
                     for obj in self.objectives_name]
        else:
            algos = [algorithms.Kernel_TS(bandwidth, 1e-3, self.noise_ub_objectives[obj])
                     for obj in self.objectives_name]

        # add previous knowledge
        for path in self.previous:
            if path != None:
                prev_X, prev_y = customio.read_previous_results(path, self.params_name, self.objectives_name)
                # to handle pseudo-observations around borders
                with open(os.path.join(path, "config"), "r") as f:
                    prev_config = yaml.load(f)
                    prev_bounds = [(prev_config["space"][p][0], prev_config["space"][p][-1])
                                   for p in prev_config["params"]]
                for i, algo in enumerate(algos):
                    try:
                        algo.update(prev_X, prev_y[:, i], prev_bounds)
                    except:
                        print("Error occured while trying to add previous from", path)
                        exit()
                self.t += prev_X.shape[0]
        return objectives, space, algos
