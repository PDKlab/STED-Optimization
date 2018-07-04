
"""This modules contains the functions to compute the fourier shell correlation
given an image. These functions are based on

.. [Tortarolo2018] Tortarolo, G., Castello, M., Diaspro, A., Koho, S. & Vicidomini, G. (2018)
                   Evaluating image resolution in stimulated emission depletion microscopy.
"""

import numpy
import random
import os
import itertools


def split_image_array(img, factor):
    """Splits a 2D :method:`numpy.array` into 4 independant images.

    :param img: A 2D :method:`numpy.array`.
    :param factor: The shape of the sampled array.

    :return: A list of 4 2D :method:`numpy.array`
    """
    d = img.shape[0]
    newD = int(d/factor)
    im = [numpy.zeros((newD, newD)) for i in range(4)]
    for j in range(0, d-1, factor):
        for i in range(0, d-1, factor):
            sup = img[j:j+factor, i:i+factor]
            sup = sup.ravel()
            for k in range(len(sup)):
                a, b = int(j / factor), int(i / factor)
                im[k][a, b] += sup[k]
    return im


def fourier_shell_corr(img1, img2):
    """Computes the fourier shell correlation from two noise independant images.
    [Tortarolo2018]_.

    :param img1: A 2D :method:`numpy.array`
    :param img2: A 2D :method:`numpy.array`

    :return: The fourier shell correlation and the number of pixels in every rings
             to be used in the :func:`SNR`.
    """
    fscList, nPx = [], []
    Hm = Hamming(img1.shape[1], img1.shape[0])
    fimg1 = numpy.fft.fftshift(numpy.fft.fft2(img1 * Hm))
    fimg2 = numpy.fft.fftshift(numpy.fft.fft2(img2 * Hm))

    h, w = fimg1.shape
    yc, xc = int((h + 1) / 2) + 1, int((w + 1) / 2) + 1
    rmax = min([w - xc, h - yc])
    for r in range(rmax):
        x, y = numpy.ogrid[0:fimg1.shape[0], 0:fimg1.shape[1]]
        maskA = numpy.sqrt((x - xc)**2 + (y - yc)**2) >= r - 0.5
        maskB = numpy.sqrt((x - xc)**2 + (y - yc)**2) < r + 0.5
        mask = maskA * maskB

        corr = numpy.sum(fimg1[mask] * numpy.conjugate(fimg2[mask]))
        absA = numpy.sum(numpy.abs(fimg1[mask]**2))
        absB = numpy.sum(numpy.abs(fimg2[mask]**2))

        fscList.append(numpy.abs(corr) / numpy.sqrt(absA * absB))
        nPx.append(mask.sum())
    return numpy.array(fscList), numpy.array(nPx)


def meeting_point(fsc, res, thres):
    """Finds the first meeting point between the fourier shell correlation curve
    and the choosen threshold. It returns 0 if the fourier shell correlation never
    crosses the threshold curve.

    :param fsc: A 1D :method:`numpy.array` containing the fourier shell correlation.
    :param res: A list of the frequency associated with the fourier shell correaltion.
    :param thres: The threshold to use for the meeting point.

    :return: The frequency at which the fourier shell correlation croses the threshold
             curve.
    """
    start = False
    for i, state in enumerate((fsc < thres)):
        if state == False:
            start = True
        if (start == True) & (state == True):
            return (res[i] + res[i-1])/2
        if (i == fsc.size - 1) & (start == True):
            return res[i]
    return 0


def moving_average(x, N):
    """Performs a moving average on a 1D :method:`numpy.array`.

    :param x: A 1D :method:`numpy.array`.
    :param N: Half length of the kernel of full size (2*N+1).

    :return: A 1D :method:`numpy.array` averaged.
    """
    smoothx = numpy.zeros(x.shape)
    for i in range(x.size):
        if i <= N:
            smoothx[i] = numpy.mean(x[ : i + N])
        elif (i > N) & (i < x.size - N):
            smoothx[i] = numpy.mean(x[i - N : i + N])
        elif i >= N:
            smoothx[i] = numpy.mean(x[i - N : ])
    return smoothx


def sigma_curve(N, sig = 3):
    """Computes the sigma curve based on [Tortarolo2018]_.

    :param N: A :method:`numpy.array` containing the number of pixels in the ring.
    :param sig: The sigma criterion. (default : 3, meaning that it is the 3-sigma curve)

    :return: A 1D :method:`numpy.array`.
    """
    return sig / numpy.sqrt(N / 2)


def Hamming(w, h):
    """Computes the Hamming filter of a given shape. The :math:`\alpha` is set to
    0.54 and the :math:`\beta` is set to :math:`1 - \alpha`.

    :param w: The width of the filter.
    :param h: The height of the filter.

    :return: The Hamming window.
    """
    alpha = 0.54
    beta = 1 - alpha

    xv = (alpha - beta * numpy.cos(2 * numpy.pi / (w - 1) * numpy.arange(0, w))).reshape(1, len(numpy.arange(0, w)))
    yv = (alpha - beta * numpy.cos(2 * numpy.pi / (h - 1) * numpy.arange(0, h))).reshape(1, len(numpy.arange(0, h)))

    return (yv.T).dot(xv)
