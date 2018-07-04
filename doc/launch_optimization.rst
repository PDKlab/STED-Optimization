Launching the optimization
==========================

Command line
------------

The module :mod:`launch_cmd` is used when the user wants to start the optimization
routine from the command window. There are two options available for the user. The
user can launch the optimization without any preset configurations or he can parse
a configuration dictionary to the :mod:`launch_cmd`.

The first option launches the optimization routine without any configuration. The
user will be guided through the process of setting up his own configuration settings
via a list of questions. To start the optimization, the user should open up a command
window in the directory containing the :mod:`launch_cmd` module and type in

``python launch_cmd.py``

There are some precautions to take with the answers that are given by the user. Here
we review all the questions and how they should be answered. ::

  Where should the results be saved? C:\Users\Path\To\Output\Folder
    **Note** no `""` are used when giving the output directory and any subsequent answers.

  What should be the name of the folder? Test_Experiment

  Do you have any previous results? If NO press enter. C:\To\Previous1, C:\To\Previous2
    **Note** The previous folders are separated by a comma and a space.

  What parameters should be used? Dwelltime Exc/Power STED/Power
    **Note** The parameters from the list that is given should be spelled the right way
    and should be separated by only a space.

  Do you want to modify the parameter space? (y/n) y
    What should be the minimum value of <name_of_parameter>? 0.1
      **Note** The user answers this question with a number. The same applies for
      the maximum value, the number of points and the every other questions asking for a
      value.

  Do you want to modify the setting of the parameters (laser_id, sted_id, channel_id)? (y/n) y
    What should be the id of <name_of_parameter>? 1

  What objectives should be optimized? Quality Bleach

  Do you want to modify the objectives values? (y/n) n

  Do you want to modify the noise upper bound values? (y/n) n

  Do you want to consider imaging time as an objective when making decisions? (y/n) y

  Do you want to simulate points in the regression model (e.g. to counter border effect)? (y/n) y

  Do you want to be able to thrash the data every region that is scanned? (y/n) n

  What version of the optimization routine do you want? Normal (0), Automatic quality rating (1), Fully automated (2) 0

As previously mentioned a dictionary can be parse to :mod:`launch_cmd` to avoid the
tedious process of answering the questions via the command window. To do so the configuration
dictionary can be parse as such

``python launch_cmd.py -c config``

where ``config`` is the configuration dict. A ``config`` file is provided in the
bundle of functions. However, we will explain in detail the entries that should
be in the configuration dictionary. ::

  autopref: { # the fully automated network
    IP: <IP_address>, # the address where the network is being run
    port: 5002 # the port number of the network to access
  }
  autoquality: { # the rating of quality network
    IP: <IP_address>, # the address where the network is being run
    port: 5000 # the port number of the network to access
  }
  noise_ub_objectives: { # the noise upper bound limit on the objectives
    Autocorrelation: 0.3,
    Bleach: 0.1,
    FRC: 0.1,
    FWHM: 5,
    Quality: 0.1,
    Quality_Last: 0.1,
    Signal_Ratio: 2
  }
  objectives: { # the objectives, set to true if wanted
    Autocorrelation: false,
    Bleach: false,
    FRC: false,
    FWHM: false,
    Quality: false,
    Quality_Last: false,
    Signal_Ratio: false
  }
  objectives_values: { # the objective values, some of them needs these entries to evaluate the objective
    FRC: 0.02, # pixel size in µm
    Signal_Ratio: 75, # percentile
  }
  output: { # saving output
    folder: Experiment_name
    previous: ['C:\To\Previous1', 'C:\To\Previous2'] # if no previous use [null]. Note the presence of '' and a list
    saving_dir: C:\Users\Path\To\Output\Folder # No '' are needed
  }
  params: { # the parameters, set to true if wanted
    Dwelltime: false,
    Exc/Power: false,
    Line_Step: false,
    STED/Power: false
  }
  params_set: { # laser id, step id and channel id
    Exc/Power: 4,
    Line_Step: 0,
    STED/Power: 5
  }
  params_space: { # the parameter space, needs a list of min, max and number of points
    Dwelltime: [1e-5, 1e-4, 10], # in seconds
    Exc/Power: [0.01, 0.4, 10], # in %
    Line_Step: [10, 25, 2],
    STED/Power: [0.05, 0.5, 10], # in %
  }
  pseudo_points: true # simulate points in the regression model (e.g. to counter border effect)
  with_time: true # to consider imaging time as an objective when making decisions

Graphical User Interface (GUI)
------------------------------

The GUI can be launched from the provided executable or can also be launched from
the terminal using the command ``python launch_gui.py`` if all the necessary packages
are installed in the python environment.

Main window
^^^^^^^^^^^

When launched the main GUI will look like the following image. The main GUI separates
in three different sections. The output directory, the parameters and the objectives
to optimize and a set of buttons.

.. image:: images/main_gui.png
  :align: center

**Output directory**

This block allows the user to select the output directory, *i.e.* where the data
will be saved. To do so, the user can click on the *Browse* button to select a folder
or he can enter the name of the folder where he wants to export the data. The user
must then give a name to the experience. This will create a folder in the output
directory with the name of the experience containing all the images and the optimization
parameters. The user can also import previous knowledge from previous optimization
routine.

**Parameters and objectives**

The user must select the parameters (left list) that he wants to optimize the objectives
with. To select multiple parameters, the user must hold the *ctrl* key and click on the
wanted parameters. The user should also select the objectives that he wants to
optimize during the optimization routine. Once again, if multiple objectives are to
be selected, the user should hold the *ctrl* key during the selection.

**Buttons**

There are three buttons in the third section of the main GUI: *Show advanced parameters*,
*Microscope config* and *Start Optimization*. The first button allows the user
to open a new window (see the next section). The second button asks the user to
select the confocal and the STED configuration from the microscope. The user should
be careful since the questions are asked in the *Command Window* that is open during
the optimization routine. When all the parameters have been set, the user can launch
the optimization using the *Start Optimization* button.

Advanced parameters window
^^^^^^^^^^^^^^^^^^^^^^^^^^

The advanced parameter window, after the button *Show advanced parameters* has been
clicked, will look like this. This window can be separated in different sections
each of which will be explained later.

.. image:: images/advanced_gui.png
  :align: center

**Parameter space**

This is the different values that the parameters can take. These are set using the
python functions :func:`numpy.arange` and :func:`numpy.linspace` from the module
:mod:`numpy`. This means that depending on the parameters, the inc. will not
mean the same thing. The other parameters use the function :func:`numpy.linspace` meaning that the inc.
represent the number of points between the two values.

Here is the list of the unit of every parameter

====================  =====
     Parameter        Unit
--------------------  -----
Dwelltime             s
Exc/Power             %
STED/Power            %
Line_Step             -
====================  =====

**Parameter set**

This sets the id of the excitation laser and the STED laser in the microscope. It also
changes the step id and the channel id for the rescue channel.

**Objectives values**

The given objectives must have an input value if the user wants to evaluate those.
The Signal_Ratio is the percentile at which to detect the signal
and the foreground respectively. The FRC objective takes as an input the size of the
pixels in the image before. This size is in micrometers, *i.e.* a 20 nm pixel will
have a value of 20e-3 µm.

**Objectives noise upper bound**

This section sets the noise of the upper bound limit for the sampling algorithm.

**Auto quality network**

The auto quality network allows the optimization algorithm to rate the STED image
without the need for the user input. If the user wants to use the auto quality network,
he must select the button. The IP address has to be set where the docker image is
being run. The port number is 5000 by default. **Important** If the user wants to
use the auto quality network, he must select the Quality as an objective in the main
window.

**Fully auto network**

The fully auto network allows the optimization algorithm to be completely automatic.
The network will rate the quality of the image and will also make the trade-off that
the user must make in the normal and auto quality network. If the user wants to use
the fully automatic network, he must select the button. The IP has to be the address where
the docker image is being run. The port number is 5002 by default. **Important** If the
user wants to use the fully auto network, he must select the Quality as an objective
in the main window.

**Optional parameters**

The user can select those optional parameters if he desires. *with_time* allows the
user to take into account the imaging time as an objective. *pseudo_points* simulates more
points for the user to choose from when making the tradeoffs in the normal and auto
quality network. *thrash_data* offers the possibility to the user to discard the images
that were taken during an experiment.
