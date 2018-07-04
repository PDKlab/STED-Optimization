Tools
=====

This sections provides the documentation for the modules :mod:`user` and :mod:`utils`.
Those modules contain tools that are used by other modules.

User
----

.. automodule:: user

.. autoclass:: user.LinePicker

  .. automethod:: user.LinePicker.on_press

  .. automethod:: user.LinePicker.on_release

.. autoclass:: user.PointPicker

  .. automethod:: user.PointPicker.on_press

.. autofunction:: user.get_lines

.. autofunction:: user.get_points

.. autofunction:: user.get_regions

.. autofunction:: user.select

.. autofunction:: user.give_score

Utils
-----

.. automodule:: utils

.. autofunction:: utils.avg_area

.. autofunction:: utils.estimate_signal

.. autofunction:: utils.gaussian_fit

.. autofunction:: utils.points2regions

.. autofunction:: utils.gauss

.. autofunction:: utils.get_foreground

.. autofunction:: utils.find_first_min

.. autofunction:: utils.find_first_max

.. autofunction:: utils.plot_regression

.. autofunction:: utils.rescale

.. autofunction:: utils.img2float
