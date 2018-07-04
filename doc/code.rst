Algorithms
============

.. automodule:: algorithms

Functions
-----------------

.. autofunction:: algorithms.estimate_noise

Kernel Thompson Sampling
------------------------

.. autoclass:: algorithms.Kernel_TS

  .. automethod:: algorithms.Kernel_TS.predict(bandwidth, s_lb, s_ub)

  .. automethod:: algorithms.Kernel_TS.sample(X_pred)

  .. automethod:: algorithms.Kernel_TS.update(actions, rewards[, *args])


.. autoclass:: algorithms.Kernel_TS_PseudoActions

  .. automethod:: algorithms.Kernel_TS_PseudoActions.predict(bandwidth, s_lb, s_ub, space_bounds)

  .. automethod:: algorithms.Kernel_TS_PseudoActions.sample(X_pred)

  .. automethod:: algorithms.Kernel_TS_PseudoActions.update(action, rewards[, space_bounds=None])
