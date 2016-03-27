#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt

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

    def ecdf(self, v, x):
        """Given a vector v, return the ECDF evaluated at x."""
        if len(v) == 0:
            return

        fx = []
        n = 0
        vsorted = np.sort(v)
        for s in vsorted:
            n += 1
            fx.append(n)
        F_x = np.array(fx)/float(n)

        i = np.searchsorted(vsorted, x, side = 'right') - 1
        #print vsorted, F_x
        if i < 0:
            return 0.
        else:
            return F_x[i]

    def shift(self, step = 0.):
        """Shift the MC distribution by STEP g/cm^2 and return the CVM test
        statistic."""
        pass
