"""This script is intended to launch the optmization routine from the command
line. There are two options for the user.

The first option is to launch the script with a default configuration parameters
and change the parameters of optimization by answering the few questions.
USAGE : python launch_cmd.py

The second option is to launch the script with a given configuration parameters
that has been changed before the experiment. To do so, the user should use the
parser -c with the given configuration parameters filename.
USAGE : python launch_cmd.py -c config

"""

import yaml
import os
import argparse

import matplotlib
matplotlib.use("TkAgg")

from optimization import Optimizer
import create_config
import microscope


def yesno_input(question):
    answer = input(question)
    while answer not in ["y", "n"]:
        print("Sorry, what did you say? ")
        answer = input(question)
    return answer


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", type=str,
                        help = "name of the file or path to the configuration parameters")
    args = parser.parse_args()

    # setting the confocal and the sted configuration of the microscope
    config_conf = microscope.get_config("Setting confocal configuration.")
    config_sted = microscope.get_config("Setting STED configuration.")
    # verify that confocal and STED configurations can be used together
    assert microscope.get_imagesize(config_conf) == microscope.get_imagesize(config_sted),\
        "Confocal and STED images must have the same size!"

    if args.config:
        with open(args.config, "r") as f:
            config = yaml.load(f)
    else:
        config = create_config.create_config()
        saving_dir = input("Where should the results be saved? ")
        config["output"]["saving_dir"] = saving_dir

        folder = input("What should be the name of the folder? ")
        config["output"]["folder"] = folder

        previous = input("Do you have any previous results? If NO press enter. ")
        if previous:
            config["output"]["previous"] = previous.split(", ")

        params = input("What parameters should be used? Here is the list : \n {} \n".format("\n ".join([str(key) for key in config["params"]])))
        for key in config["params"]:
            if key in params.split(" "):
                config["params"][key] = True
            else:
                config["params"][key] = False

        params_space = yesno_input("Do you want to modify the parameter space? (y/n) ")
        if params_space == "y":
            for key in config["params"]:
                if config["params"][key]:
                    pmin = input("What should be the minimum value of {}? ".format(key))
                    pmax = input("What should be the maximum value of {}? ".format(key))
                    pinc = input("What should be the number of points in {}? ".format(key))
                    config["params_space"][key][0] = float(pmin)
                    config["params_space"][key][1] = float(pmax)
                    config["params_space"][key][2] = float(pinc)

        params_set = yesno_input("Do you want to modify the setting of the parameters (laser_id, step_id, channel_id)? (y/n) ")
        if params_set == "y":
            for key in config["params"]:
                if config["params"][key]:
                    try:
                        config["params_set"][key]
                        id = input("What should be the new id of {}? ".format(key))
                        config["params_set"][key] = int(id)
                    except KeyError:
                        pass

        objectives = input("What objectives should be optimized? Here is the list : \n {} \n".format("\n ".join([str(key) for key in config["objectives"]])))
        for key in config["objectives"]:
            if key in objectives.split(" "):
                config["objectives"][key] = True
            else:
                config["objectives"][key] = False

        objectives_values = yesno_input("Do you want to modify the objectives values? (y/n) ")
        if objectives_values == "y":
            for key in config["objectives"]:
                if config["objectives"][key]:
                    val = input("What should be the value of {}? ".format(key))
                    config["objectives_values"][key] = float(val)

        noise_ub_objectives = yesno_input("Do you want to modify the noise upper bound values? (y/n) ")
        if noise_ub_objectives == "y":
            for key in config["objectives"]:
                if config["objectives"][key]:
                    val = input("What should be the value of {}? ".format(key))
                    config["noise_ub_objectives"][key] = float(val)

        with_time = yesno_input("Do you want to consider imaging time as an objective when making decisions? (y/n) ")
        config["with_time"] = (with_time == "y")

        pseudo_points = yesno_input("Do you want to simulate points in the regression model (e.g. to counter border effect)? (y/n) ")
        config["pseudo_points"] = (pseudo_points == "y")


    # CONFIGURES THE OPTIMIZATION ROUTINE WITH THE GIVEN CONFIGURATION
    answer = yesno_input("Do you want to be able to thrash the data every region that is scanned? (y/n) ")
    thrash_data = (answer == "y")

    optimizationScheme = input("What version of the optimization routine do you want? Normal (0), Automatic quality rating (1), Fully automated (2) ")
    while optimizationScheme not in ["0", "1", "2"]:
        print("Sorry, what did you say? ")
        optimizationScheme = input("What version of the optimization routine do you want? Normal (0), Automatic quality rating (1), Fully automated (2) ")
    if optimizationScheme == "0":
        OPT = Optimizer(config, config_conf, config_sted, thrash_data=thrash_data)
    elif optimizationScheme == "1":
        autoquality = yesno_input("Do you want to change the parameters of the QualityNet? (y/n) ")
        if autoquality == "y":
            for key in config["autoquality"]:
                val = input("What should be the {}? ".format(key))
                if key == "IP":
                    config["autoquality"][key] = val
                else:
                    config["autoquality"][key] = int(val)
        OPT = Optimizer(config, config_conf, config_sted, autoquality=True, thrash_data=thrash_data)
    elif optimizationScheme == "2":
        autoquality = yesno_input("Do you want to change the parameters of the QualityNet? (y/n) ")
        if autoquality == "y":
            for key in config["autoquality"]:
                val = input("What should be the {}? ".format(key))
                if key == "IP":
                    config["autoquality"][key] = val
                else:
                    config["autoquality"][key] = int(val)
                config["autoquality"][key] = val
        autopref = yesno_input("Do you want to change the parameters of the PrefNet? (y/n) ")
        if autopref == "y":
            for key in config["autopref"]:
                val = input("What should be the {}? ".format(key))
                if key == "IP":
                    config["autoquality"][key] = val
                else:
                    config["autoquality"][key] = int(val)
                config["autopref"][key] = val
        OPT = Optimizer(config, config_conf, config_sted, autoquality=True, autopref=True, thrash_data=thrash_data)

    with open(os.path.join(config["output"]["saving_dir"], config["output"]["folder"], "optimization_config"), "w") as f:
        yaml.dump(config, f)

    # RUNS THE OPTIMIZATION ROUTINE
    more_regions = True
    readjust = False
    while more_regions:
        OPT.run(readjust)
        answer = yesno_input("Do you want to select more regions and continue? (y/n) ")
        more_regions = (answer == "y")
        if more_regions:
            answer = yesno_input("Do you want to readjust focus parameters? (y/n) ")
            readjust = (answer == "y")
