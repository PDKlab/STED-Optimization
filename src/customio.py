
import os
import yaml

import numpy


def read_previous_results(path, params=None, objectives=None, y_filename="y"):
    """Reads previous results in the config from the given path. The previous results
    has to have the same parameters and the same objectives.

    :param path: The path where to get the config file from.
    :param params: A list of params names.
    :param objectives: A list of objectives names.
    :param y_filename: The name of the file containing the evaluated objectives.

    :return: The previous parameters and the obectives evaluated with those parameters.
    """
    with open(os.path.join(path, "config"), "r") as f:
        config = yaml.load(f)
        if params is not None:
            assert params == config["params"], "Previous results can only be used for same params."
        if objectives is not None:
            assert objectives == config["objectives"], "Previous results can only be used for same objectives."
    with open(os.path.join(path, "X"), "rb") as f:
        previous_X = numpy.loadtxt(f, delimiter=",")[:, 1:]
    with open(os.path.join(path, y_filename), "rb") as f:
        previous_y = numpy.loadtxt(f, delimiter=",")[:, 1:]
    return previous_X, previous_y
