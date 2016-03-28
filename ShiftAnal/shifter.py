#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d

class shifter:
    """Performs shift analysis of Xmax data by examining the distribution the
    two sample Cramér-von Mises test on two Xmax distributions: data and MC. In
    this test the MC distribution is shifted to find the minimum of the CVM test
    statistic, which corresponds to the compatibility of the data with tested MC
    species model.

    See "On the Distribution of the Two-Sample Cramér-von Mises Criterion",
    T.W. Anderson
    (http://projecteuclid.org/download/pdf_1/euclid.aoms/1177704477) for a
    description of the test."""
    def __init__(self):
        self.energyBin = '' # string to describe the energy bin being tested
        self.xmaxData = []  # once set xmaxData won't change
        self.xmaxMC = []    # xmaxMC is the distribution that is shifted

        # table of test statistics and lim_{n->\infinity} P(n\omega^2 <= z)
        self.a1_z = np.linspace(0., 0.99, 100)
        self.a1_z = np.append(self.a1_z, 0.999)
        self.z = [0.00000, 0.02480, 0.02878, 0.03177, 0.03430, 0.03656, 0.03865,
             0.04061, 0.04247, 0.04427, 0.04601, 0.04772, 0.04939, 0.05103,
             0.05265, 0.05426, 0.05586, 0.05746, 0.05904, 0.06063, 0.06222,
             0.06381, 0.06541, 0.06702, 0.06863, 0.07025, 0.07189, 0.07354,
             0.07521, 0.07690, 0.07860, 0.08032, 0.08206, 0.08383, 0.08562,
             0.08744, 0.08928, 0.09115, 0.09306, 0.09499, 0.09696, 0.09896,
             0.10100, 0.10308, 0.10520, 0.10736, 0.10956, 0.11182, 0.11412,
             0.11647, 0.11888, 0.12134, 0.12387, 0.12646, 0.12911, 0.13183,
             0.13463, 0.13751, 0.14046, 0.14350, 0.14663, 0.14986, 0.15319,
             0.15663, 0.16018, 0.16385, 0.16765, 0.17159, 0.17568, 0.17992,
             0.18433, 0.18892, 0.19371, 0.19870, 0.20392, 0.20939, 0.21512,
             0.22114, 0.22748, 0.23417, 0.24124, 0.24874, 0.25670, 0.26520,
             0.27429, 0.28406, 0.29460, 0.30603, 0.31849, 0.33217, 0.34730,
             0.36421, 0.38331, 0.40520, 0.43077, 0.46136, 0.49929, 0.54885,
             0.61981, 0.74346, 1.16786]
        # create the interpolation function
        self.f = interp1d(self.z, self.a1_z, bounds_error = False)

    def ecdf(self, v, x, returnECDF = False):
        """Given a vector v, return the ECDF evaluated at x and, optionally,
        the ECDF vector."""
        F_x = []

        if len(v) == 0:
            if returnECDF == True:
                return 0., np.array(F_x)
            else:
                return 0.

        fx = []
        n = 0
        vsorted = np.sort(v)
        for s in vsorted:
            n += 1
            fx.append(n)
        if n == 0:
            if returnECDF == True:
                return 0., F_x
            else:
                return 0.
        F_x = np.array(fx)/float(n)

        i = np.searchsorted(vsorted, x, side = 'right') - 1
        if i < 0:
            if returnECDF == True:
                return 0., F_x
            else:
                return 0.
        else:
            if returnECDF == True:
                return F_x[i], F_x
            else:
                return F_x[i]

    def cvm(self, x = None, y = None):
        """User provides two arrays and the CVM test statistic and p-values are
        computed.
        
        Function returns the CVM test statistic, the test statistic adjusted to
        the limiting value (where n, m -> infinity), and p-value."""
        if (x is None):
            x = self.xmaxData
        if (y is None):
            y = self.xmaxMC

        T = 0.
        N = float(len(x))
        M = float(len(y))

        if N == 0 or M == 0:
            raise ValueError('cvm: empty vector')

        s1 = 0.
        for ex in x:
            s1 += (self.ecdf(x, ex) - self.ecdf(y, ex))**2
        
        s2 = 0.
        for ey in y:
            s2 += (self.ecdf(x, ey) - self.ecdf(y, ey))**2

        # the CVM test statistic
        T = N*M/(N + M)**2*(s1 + s2)

        # the expected value of T (under the null hypothesis)
        expT = 1./6. + 1./(6.*(M + N))

        # the variance of T
        varT = 1./45.*(M + N + 1.)/(M + N)**2*\
                (4.*M*N*(M + N) - 3.*(M**2 + N**2) - 2.*M*N)/(4.*M*N)

        # adjust T so that its significance can be computed using the limiting
        # distribution
        limitT = (T - expT)/np.sqrt(45.*varT) + 1./6.


        # p-value for this test statistic
        if T > self.z[-1]:
            p = 0.
        else:
            p = 1. - self.f(T)

        return T, limitT, p


    def shift(self, step = 0.):
        """Shift the MC distribution by STEP g/cm^2 and return the CVM test
        statistic."""
        pass
