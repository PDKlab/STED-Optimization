
"""This module contains classes to generate options presented to the user in the online
multi-objective kernelized bandits optimization problem.

.. [Durand2018] Durand, Maillard and Pineau (2018). Streaming kernel regression with
   provably adaptive mean, variance, and regularization. *JMLR*
.. [Williams2006] Williams and Rasmussen (2006). Gaussian processes for machine learning.
   *The MIT Press*
"""

import numpy

from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF


def estimate_noise(X, y, bandwidth, s_minus, s_plus, norm_bound, delta):
    """Given initial lower and upper bounds on the noise standard deviation :math:`\sigma`, this function
    estimates lower and upper bounds on :math:`\sigma` from previous observations
    obtained using streaming kernel regression [Durand2018]_. The estimated bounds define a
    confidence interval that holds with probability :math:`1-3\delta`. This function relies on the
    Gaussian process implementation from :mod:`sklearn` with a fixed RBF kernel [Williams2006]_.

    :param X: Input points (2d array).
    :param y: Observations (1d array)
    :param bandwidth: The bandwidth of the RBF kernel.
    :param s_minus: Initial lower bound on :math:`\sigma`.
    :param s_plus: Initial upper bound on :math:`\sigma`.
    :param norm_bound: A bound on the norm of the function in the RKHS induced by the
                       RBF kernel of given `bandwidth`.
    :param delta: The confidence :math:`\delta`.
    :returns: Lower and upper bound estimates on :math:`\sigma`.
    """
    lambda_ = s_plus**2 / norm_bound**2
    model = GaussianProcessRegressor(RBF(length_scale=bandwidth), alpha=lambda_, optimizer=None, normalize_y=True)
    model.fit(X, y)
    y_hat, sqrt_k = model.predict(X, return_std=True)
    ks = sqrt_k**2
    s_hat = numpy.sqrt(numpy.mean((y - y_hat)**2))

    t = X.shape[0]
    c = numpy.log(numpy.e/delta) * (1 + numpy.log(numpy.pi**2*numpy.log(t)/6) / numpy.log(1/delta))

    e = 1 - 1 / numpy.max(1 + ks / lambda_)
    s_lb = (s_hat - norm_bound * numpy.sqrt(lambda_*e/t)) / (1 + numpy.sqrt(2*c/t))
    if numpy.isnan(s_lb):
        s_lb = s_minus
    else:
        s_lb = max(s_lb, s_minus)

    lambda_star = s_lb**2 / norm_bound**2
    model = GaussianProcessRegressor(RBF(length_scale=bandwidth), alpha=lambda_star, optimizer=None, normalize_y=True)
    model.fit(X, y)
    _, sqrt_k = model.predict(X, return_std=True)
    ks = sqrt_k**2

    d = 2 * numpy.log(1/delta) + numpy.sum(numpy.log(1+ks/lambda_star))
    a = max(1 - numpy.sqrt(c/t) - numpy.sqrt((c+2*d)/t), 1e-10)
    b = norm_bound * numpy.sqrt(lambda_*d) / (2 * t)
    s_ub = (numpy.sqrt(b) + numpy.sqrt(b + s_hat * a))**2 / a**2
    if numpy.isnan(s_ub):
        s_ub = s_plus
    else:
        s_ub = min(s_ub, s_plus)

    return s_lb, s_ub


class Kernel_TS:
    """This class relies on kernel regression to generate options to present to the user
    using a Thompson Sampling approach. It relies on the Gaussian process implementation
    from :mod:`sklearn` with a fixed RBF kernel [Williams2006]_ and maintain empirical
    confidence interval on the noise standard deviation :math:`\sigma` [Durand2018]_.

    :param bandwidth: The bandwidth of the RBF kernel.
    :param s_lb: An initial lower bound on :math:`\sigma`.
    :param s_ub: An initial upper bound on :math:`\sigma`.
    """
    def __init__(self, bandwidth, s_lb, s_ub):
        self.bandwidth = bandwidth
        self.s_lb = s_lb
        self.s_ub = s_ub
        self.X = None
        self.y = None

        norm_bound = 5
        self.lambda_ = s_ub**2/norm_bound**2

    def predict(self, X_pred):
        """Predict mean and standard deviation at given points *X_pred*.

        :param X_pred: A 2d array of locations at which to predict.
        :returns: An array of means and an array of standard deviations.
        """
        if self.X is not None:
            gp = GaussianProcessRegressor(RBF(length_scale=self.bandwidth), alpha=self.lambda_, optimizer=None, normalize_y=True)
            gp.fit(self.X, self.y)
            mean, sqrt_k = gp.predict(X_pred, return_std=True)
            std = self.s_ub / numpy.sqrt(self.lambda_) * sqrt_k
        else:
            mean = numpy.full(X_pred.shape[0], 0)
            std = numpy.full(X_pred.shape[0], self.s_ub / numpy.sqrt(self.lambda_))
        return mean, std

    def sample(self, X_sample):
        """Sample a function evaluated at points *X_sample*.

        :param X_sample: A 2d array locations at which to evaluate the sampled function.
        :returns: A 1-D of the pointwise evaluation of a sampled function.
        """
        if self.X is not None:
            gp = GaussianProcessRegressor(RBF(length_scale=self.bandwidth), alpha=self.lambda_,
                                              optimizer=None, normalize_y=True)
            gp.fit(self.X, self.y)
            mean, k = gp.predict(X_sample, return_cov=True)
            cov = self.s_ub**2 / self.lambda_ * k
        else:
            mean= numpy.full(X_sample.shape[0], 0)
            cov = self.s_ub**2 / self.lambda_ * numpy.identity(X_sample.shape[0])
        f_tilde = numpy.random.multivariate_normal(mean, cov, 1)[0]
        return f_tilde

    def update(self, action, reward, *args):
        """Update the kernel regression model using the observations *reward* acquired at
        location *action*. Estimate upper and lower bounds on the noise variance using
        :func:`estimate_noise` with confidence :math:`\delta=0.1`.
        
        :param action: A 2d array of locations.
        :param reward: A 1-D array of observations.
        :param `*args`: Dummy parameter to handle functions of inheritated classes.
        """
        if self.X is None:
            self.X = numpy.asarray(action)
            self.y = numpy.asarray(reward)
        else:
            self.X = numpy.r_[self.X, action]
            self.y = numpy.r_[self.y, reward]

        norm_bound = 5
        delta = 0.1
        s_lb, s_ub = estimate_noise(self.X, self.y, self.bandwidth, self.s_lb, self.s_ub,
                                    norm_bound, delta)
        lambda_, lambda_star = s_ub**2/norm_bound**2, s_lb**2/norm_bound**2
        self.s_lb, self.s_ub, self.lambda_, self.lambda_star = s_lb, s_ub, lambda_, lambda_star


class Kernel_TS_PseudoActions(Kernel_TS):
    """This class relies on kernel regression to generate options to present to the user
    using a Thompson Sampling approach. It relies on the Gaussian process implementation
    from :mod:`sklearn` with a fixed RBF kernel [Williams2006]_ and maintain empirical
    confidence interval on the noise standard deviation :math:`\sigma` [Durand2018]_.
    It extends the class :class:`Kernel_TS` to hallucinate pseudo-actions (and associated
    pseudo-rewards). Pseudo-actions are reflected at over the boundaries of the space and
    

    :param bandwidth: The bandwidth of the RBF kernel.
    :param s_lb: An initial lower bound on :math:`\sigma`.
    :param s_ub: An initial upper bound on :math:`\sigma`.
    :param space_bounds: A list of tuple (lower, upper) bounds, bounding the input space in
                         for each dimension.
    """
    def __init__(self, bandwidth, s_lb, s_ub, space_bounds):
        super().__init__(bandwidth, s_lb, s_ub)

        self.space_bounds = space_bounds
        self.pseudo_X = None
        self.pseudo_y = None

    def predict(self, X_pred):
        """Predict mean and standard deviation at given points *X_pred*.

        :param X_pred: A 2d array of locations at which to predict.
        :returns: An array of means and an array of standard deviations.
        """
        if self.pseudo_X is not None:
            gp = GaussianProcessRegressor(RBF(length_scale=self.bandwidth), alpha=self.lambda_,
                                              optimizer=None, normalize_y=True)
            gp.fit(self.pseudo_X, self.pseudo_y)
            mean, sqrt_k = gp.predict(X_pred, return_std=True)
            std = self.s_ub / numpy.sqrt(self.lambda_) * sqrt_k
        else:
            mean = numpy.full(X_pred.shape[0], 0)
            std = numpy.full(X_pred.shape[0], self.s_ub / numpy.sqrt(self.lambda_))
        return mean, std

    def sample(self, X_sample):
        """Sample a function evaluated at points *X_sample*.

        :param X_sample: A 2d array locations at which to evaluate the sampled function.
        :returns: A 1-D of the pointwise evaluation of a sampled function.
        """
        if self.pseudo_X is not None:
            gp = GaussianProcessRegressor(RBF(length_scale=self.bandwidth), alpha=self.lambda_,
                                              optimizer=None, normalize_y=True)
            gp.fit(self.pseudo_X, self.pseudo_y)
            mean, k = gp.predict(X_sample, return_cov=True)
            cov = self.s_ub**2 / self.lambda_ * k
        else:
            mean= numpy.full(X_sample.shape[0], 0)
            cov = self.s_ub**2 / self.lambda_ * numpy.identity(X_sample.shape[0])
        f_tilde = numpy.random.multivariate_normal(mean, cov, 1)[0]
        return f_tilde

    def update(self, actions, rewards, space_bounds=None):
        """Update the kernel regression model using the observations *reward* acquired at
        location *action*. Estimate upper and lower bounds on the noise variance using
        :func:`estimate_noise` with confidence :math:`\delta=0.1`.
        
        :param action: A 2d array of locations.
        :param reward: A 1-D array of observations.
        :param space_bounds: A list of tuple (lower, upper) bounds, bounding the input space in
                             for each dimension (default: None). If None, uses the object attribute
                             :attr:`space_bounds`.
        """
        if self.X is None:
            self.X = numpy.asarray(actions)
            self.y = numpy.asarray(rewards)
            self.pseudo_X = numpy.asarray(actions)
            self.pseudo_y = numpy.asarray(rewards)
        else:
            self.X = numpy.r_[self.X, actions]
            self.y = numpy.r_[self.y, rewards]
            self.pseudo_X = numpy.r_[self.pseudo_X, actions]
            self.pseudo_y = numpy.r_[self.pseudo_y, rewards]

        # add pseudo rewards
        if space_bounds is None: space_bounds = self.space_bounds
        for a, r in zip(actions, rewards):
            for i, (l, u) in enumerate(space_bounds):
                if a[i] == l:
                    pseudo_a = numpy.copy(a)
                    pseudo_a[i] = l - (u - l)
                    self.pseudo_X = numpy.r_[self.pseudo_X, [pseudo_a]]
                    self.pseudo_y = numpy.r_[self.pseudo_y, r]
                elif a[i] == u:
                    pseudo_a = numpy.copy(a)
                    pseudo_a[i] = u + (u - l)
                    self.pseudo_X = numpy.r_[self.pseudo_X, [pseudo_a]]
                    self.pseudo_y = numpy.r_[self.pseudo_y, r]

        norm_bound = 5
        delta = 0.1
        s_lb, s_ub = estimate_noise(self.X, self.y, self.bandwidth, self.s_lb, self.s_ub,
                                    norm_bound, delta)
        lambda_, lambda_star = s_ub**2/norm_bound**2, s_lb**2/norm_bound**2
        self.s_lb, self.s_ub, self.lambda_, self.lambda_star = s_lb, s_ub, lambda_, lambda_star
