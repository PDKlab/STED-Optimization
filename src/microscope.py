
"""
This module implements wrapper functions to access and modify easily the Imspector
parameters through SpecPy [Imspector2016].

This module can be adapted to any microscope by redefining the following functions.

.. [Impsector2016] Max Planck Institute for Biophysical Chemistry \& Abberior Instruments GmbH (2016).
   http://imspectordocs.readthedocs.io/en/latest/specpy.html

"""

import time

try:
    from specpy import Imspector

    im = Imspector()
    measurement = im.active_measurement()
except ModuleNotFoundError as err:
    print(err)
    print("Calling these functions might raise an error.")


def get_config(message=None):
    '''Fetch and return the active configuration in Imspector.

    :param message: If defined, print the following message.

    :returns: The active configuration.
    :rtype: specpy.Configuration
    '''
    if message is not None:
        print(message)
    print("Manually select imaging configuration then press enter.")
    input()
    return measurement.active_configuration()


def get_params(conf):
    '''Fetch and return the parameters of a configuration object.

    :param conf: A configuration object.

    :returns: A dict of parameters.
    :rtype: dict
    '''
    return conf.parameters("ExpControl")


def get_power(conf, laser_id):
    '''Fetch and return the power of a laser in a specific configuration.

    :param conf: A configuration object.
    :param laser_id: Index of the laser in Imspector (starting from 0).

    :returns: The power (%).
    :rtype: float
    '''
    params = conf.parameters("ExpControl/lasers/power_calibrated")
    #TODO: should we return a ratio instead?
    return params[laser_id]["value"]["calibrated"]


def get_pixelsize(conf):
    '''Fetch and return the pixel size in a specific configuration.

    :param conf: A configuration object.

    :returns: Tuple of (x, y) pixel sizes (m).
    :rtype: tuple
    '''
    x = conf.parameters("ExpControl/scan/range/x/psz")
    y = conf.parameters("ExpControl/scan/range/y/psz")
    return x, y


def get_resolution(conf):
    '''Fetch and return the resolution in a specific configuration.

    :param conf: A configuration object.

    :returns: Tuple of (x, y) resolutions (image size in pixels).
    :rtype: tuple
    '''
    x = conf.parameters("ExpControl/scan/range/x/res")
    y = conf.parameters("ExpControl/scan/range/y/res")
    return x, y


def get_imagesize(conf):
    '''Fetch and return the image size in a specific configuration.

    :param conf: A configuration object.

    :returns: Tuple of (x, y) image sizes (m).
    :rtype: tuple
    '''
    x = conf.parameters("ExpControl/scan/range/x/len")
    y = conf.parameters("ExpControl/scan/range/y/len")
    return x, y


def get_offsets(conf):
    '''Fetch and return the offsets in a specific configuration.

    :param conf: A configuration object.

    :returns: Tuple of (x, y) offsets.
    :rtype: tuple
    '''
    x = conf.parameters("ExpControl/scan/range/x/off")
    y = conf.parameters("ExpControl/scan/range/y/off")
    return x, y


def get_dwelltime(conf):
    '''Fetch and return the pixel dwell time in a specific configuration.

    :param conf: A configuration object.

    :returns: The dwell time (s).
    :rtype: float
    '''
    return conf.parameters("ExpControl/scan/dwelltime")


def get_linestep(conf, step_id):
    '''Fetch and return the line step of a specific channel in a specific configuration.

    :param conf: A configuration object.
    :param step_id: Index of the laser in Imspector (starting from 0).
    
    :returns: The line step.
    :rtype: int
    '''
    step_values = conf.parameters("ExpControl/gating/linesteps/step_values")
    return step_values[step_id]


def get_overview(conf, overview=None, prefix="Overview "):
    '''Fetch and return the overview from Imspector.

    :param conf: A configuration object.
    :param overview: The name of the overview. If `None`, ask the user to input it.
    :param prefix: A prefix to add to the name of the overview if inputed by user.

    :returns: The overview image (2d-array)
    '''
    if overview is None:
        print("Type the name of the overview then press enter.")
        overview = prefix + input()
    return conf.stack(overview).data()[0][0]


def set_offsets(conf, x, y):
    '''Set the offsets in a specific configuration.

    :param conf: A configuration object.
    :param float x: The x offset.
    :param flaot y: The y offset.
    '''
    conf.set_parameters("ExpControl/scan/range/x/off", x)
    conf.set_parameters("ExpControl/scan/range/y/off", y)


def set_power(conf, power, laser_id):
    '''Set the power of a laser in a specific configuration.

    :param conf: A configuration object.
    :param int laser_id: Imdex of the laser in Imspector (starting from 0).
    :param float power: Power of the laser in [0, 1].
    '''
    lasers = conf.parameters('ExpControl/lasers/power_calibrated')
    lasers[laser_id]["value"]["calibrated"] = power * 100
    conf.set_parameters("ExpControl/lasers/power_calibrated", lasers)


def set_dwelltime(conf, dwelltime):
    '''Set the pixel dwell time in a specific configuration.

    :param conf: A configuration object.
    :param float dwelltime: Pixel dwell time (s).
    '''
    conf.set_parameters("ExpControl/scan/dwelltime", dwelltime)


def set_linestep(conf, linestep, step_id):
    '''Set the line step of a specific channel in a specific configuration.

    :param conf: A configuration object.
    :param int linestep: The number of repetition.
    :param int step_id: Index of the line step in Imspector (starting from 0).
    '''
    step_values = conf.parameters("ExpControl/gating/linesteps/step_values")
    step_values[step_id] = linestep
    conf.set_parameters("ExpControl/gating/linesteps/step_values", step_values)



def set_rescue_signal_level(conf, signal_level, channel_id):
    '''Set the RESCue signal level in a specific configuration.

    :param conf: A configuration object.
    :param float signal_level: Signal level of RESCue.
    :param int channel_id: ID of the RESCue channel in Imspector (starting from 0).
    '''
    channels = conf.parameters("ExpControl/rescue/channels")
    channels[channel_id]["signal_level"] = signal_level
    conf.set_parameters("ExpControl/rescue/channels", channels)



def set_rescue_strength(conf, strength, channel_id):
    '''Set the RESCue strength in a specific configuration.

    :param conf: A configuration object.
    :param float strength: Strength of RESCue.
    :param int channel_id: Index of the RESCue channel in Imspector (starting from 0).
    '''
    channels = conf.parameters("ExpControl/rescue/channels")
    channels[channel_id]["strength"] = strength
    conf.set_parameters("ExpControl/rescue/channels", channels)


def acquire(conf):
    '''Activate the given configuration and acquire an image stack.

    :param conf: A configuration object.

    :return: List of images and the acquisition time (seconds).
    '''
    measurement.activate(conf)
    start = time.time()
    im.run(measurement)
    end = time.time()
    stacks = [conf.stack(i) for i in range(conf.number_of_stacks())]
    x, y = get_offsets(conf)
    # chop the first 2 lines because of imaging problems I guess
    # chop 0.08 seconds because life
    return [[image[2:].copy() for image in stack.data()[0]] for stack in stacks], end - start - 0.08
