Objectives
============

.. automodule:: objectives

Abstract objective
------------------

.. autoclass:: objectives.Objective

  .. automethod:: objectives.Objective.evaluate(sted_stack, confocal_init, confocal_end, sted_fg, confocal_fg)

Concrete objective
------------------------

.. autoclass:: objectives.Signal_Ratio

  .. automethod:: objectives.Signal_Ratio.evaluate(sted_stack, confocal_init, confocal_end, sted_fg, confocal_fg)

.. autoclass:: objectives.FWHM

  .. automethod:: objectives.FWHM.evaluate(sted_stack, confocal_init, confocal_end, sted_fg, confocal_fg)

.. autoclass:: objectives.Autocorrelation

  .. automethod:: objectives.Autocorrelation.evaluate(sted_stack, confocal_init, confocal_end, sted_fg, confocal_fg)
