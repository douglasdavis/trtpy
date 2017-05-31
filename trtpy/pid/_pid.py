# -*- coding: utf-8 -*-

import numpy as np
import scipy.interpolate as spi
import ROOT

from ._utils import axis

class roc_curve(object):
    """
    A class to construct and describe a ROC curve from two probability histograms.

    A flexible way to generate performance curves from TH1, TH2, or
    TH3 style ROOT histograms. Also supports numpy arrays of raw probabilities


    Parameters
    ----------        
    sighist: ROOT ``TH{1,2,3}`` representing signal, or a numpy 1D array of probabilities
    bkghist: ROOT ``TH{1,2,3}`` representing background, or a numpy 1D array of probabilities
    primary_axis: define the axis to create the curve from if multidimensional histogram
    interpolate: generate an interpolation of the ROC curve from the points 
    xbinrange: bins on the x-axis used to produce the curve if multidimensional histogram (for ROOT input)
    ybinrange: bins on the y-axis used to produce the curve if multidimensional histogram (for ROOT input)
    zbinrange: bins on the z-axis used to produce the curve if multidimensional histogram (for ROOT input)
    npbinning: define binning from ``numpy.linspace`` if feeding numpy arrays of probabilities.

    Attributes
    -----------
    sigPoints: the points along the x-axis of the ROC curve
    bkgPoints: the points along the y-axis of the ROC curve
    interpolation: a scipy.interpolation object from interp1d

    """

    def __init__(self, sighist, bkghist, primary_axis='x',interpolate=False,
                 xbinrange=(1,1), ybinrange=(1,1), zbinrange=(1,1), npbinning=np.linspace(0.0,1.0,100)):

        sigPtConstruct = []
        bkgPtConstruct = []

        if isinstance(sighist,np.ndarray) and isinstance(bkghist,np.ndarray):
            binning = npbinning
            sigHist, sigEdges = np.histogram(sighist,bins=binning)
            bkgHist, bkgEdges = np.histogram(bkghist,bins=binning)
            self.sigInteg, self.bkgInteg = float(np.sum(sigHist)), float(np.sum(bkgHist))
            for i in range(len(sigHist)):
                x = float(np.sum(sigHist[i+1:]))/self.sigInteg
                y = float(np.sum(bkgHist[i+1:]))/self.bkgInteg
                sigPtConstruct.append(x)
                bkgPtConstruct.append(y)

        elif isinstance(sighist, ROOT.TObject) and isinstance(bkghist, ROOT.TObject):
            # determine if ROOT histograms
            if isinstance(sighist, ROOT.TH3) and isinstance(bkghist, ROOT.TH3):
                dim = 3
                if 'y' in primary_axis:
                    self._primAxis = axis.y
                elif 'z' in primary_axis:
                    self._primAxis = axis.z
                else:
                    self._primAxis = axis.x
            elif isinstance(sighist, ROOT.TH2) and isinstance(bkghist, ROOT.TH2):
                dim = 2
                if 'y' in primary_axis:
                    self._primAxis = axis.y
                else:
                    self._primAxis = axis.x
            elif isinstance(sighist, ROOT.TH1) and isinstance(bkghist, ROOT.TH1):
                dim = 1
                self._primAxis = axis.x
            else:
                raise TypeError(
                    'inputs must be the same type of ROOT histograms'
                )

            self._sigRootHist = sighist
            self._bkgRootHist = bkghist
            # check for equal binnings
            axisGets = ['GetXaxis','GetYaxis','GetZaxis']
            for idim, ax in zip(range(dim),axisGets):
                if getattr(sighist,ax)().GetNbins() != getattr(bkghist,ax)().GetNbins():
                    raise ValueError('Histograms have different number of bins')

            # define the primary axis to compute the ROC curve on
            if self._primAxis == axis.x:
                self._rootAxis  = sighist.GetXaxis()
            elif self._primAxis == axis.y:
                self._rootAxis = sighist.GetYaxis()
            elif self._primAxis == axis.z:
                self._rootAxis = sighist.GetZaxis()
            else:
                raise ValueError('primary axis is not x, y, or z')
            primNbins = self._rootAxis.GetNbins()

            if dim == 1:
                x1, x2 = 1, primNbins
                self.sigInteg = sighist.Integral(x1,x2)
                self.bkgInteg = bkghist.Integral(x1,x2)
                for i in range(x2):
                    sigPtConstruct.append(sighist.Integral(x2-i,x2)/self.sigInteg)
                    bkgPtConstruct.append(bkghist.Integral(x2-i,x2)/self.bkgInteg)

            elif dim == 2:
                if self._primAxis == axis.x:
                    x1, x2, y1, y2 = 1, primNbins, ybinrange[0], ybinrange[1]
                    self.sigInteg = sighist.Integral(x1,x2,y1,y2)
                    self.bkgInteg = bkghist.Integral(x1,x2,y1,y2)
                    for i in range(x2):
                        sigPtConstruct.append(sighist.Integral(x2-i,x2,y1,y2)/self.sigInteg)
                        bkgPtConstruct.append(bkghist.Integral(x2-i,x2,y1,y2)/self.bkgInteg)
                elif self._primAxis == axis.y:
                    x1, x2, y1, y2 = xbinrange[0], xbinrange[1], 1, primNbins
                    self.sigInteg = sighist.Integral(x1,x2,y1,y2)
                    self.bkgInteg = bkghist.Integral(x1,x2,y1,y2)
                    for i in range(y2):
                        sigPtConstruct.append(sighist.Integral(x1,x2,y2-i,y2)/self.sigInteg)
                        bkgPtConstruct.append(bkghist.Integral(x1,x2,y2-i,y2)/self.bkgInteg)

            elif dim == 3:
                if self._primAxis == axis.x:
                    x1, x2, y1, y2 = 1, primNbins, ybinrange[0], ybinrange[1], zbinrange[0], zbinrange[1]
                    self.sigInteg = sighist.Integral(x1,x2,y1,y2,z1,z2)
                    self.bkgInteg = bkghist.Integral(x1,x2,y1,y2,z1,z2)
                    for i in range(x2):
                        sigPtConstruct.append(sighist.Integral(x2-i,x2,y1,y2,z1,z2)/self.sigInteg)
                        bkgPtConstruct.append(bkghist.Integral(x2-i,x2,y1,y2,z1,z2)/self.bkgInteg)
                elif self._primAxis == axis.y:
                    x1, x2, y1, y2 = xbinrange[0], xbinrange[1], 1, primNbins, zbinrange[0], zbinrange[1]
                    self.sigInteg = sighist.Integral(x1,x2,y1,y2,z1,z2)
                    self.bkgInteg = bkghist.Integral(x1,x2,y1,y2,z1,z2)
                    for i in range(y2):
                        sigPtConstruct.append(sighist.Integral(x1,x2,y2-i,y2,z1,z2)/self.sigInteg)
                        bkgPtConstruct.append(bkghist.Integral(x1,x2,y2-i,y2,z1,z2)/self.bkgInteg)
                elif self._primAxis == axis.z:
                    x1, x2, y1, y2 = xbinrange[0], xbinrange[1], ybinrange[0], ybinrange[1], 1, primNbins
                    self.sigInteg = sighist.Integral(x1,x2,y1,y2,z1,z2)
                    self.bkgInteg = bkghist.Integral(x1,x2,y1,y2,z1,z2)
                    for i in range(z2):
                        sigPtConstruct.append(sighist.Integral(x1,x2,y1,y2,z2-i,z2)/self.sigInteg)
                        bkgPtConstruct.append(bkghist.Integral(x1,x2,y1,y2,z2-i,z2)/self.bkgInteg)

        else:
            raise Exception('Give ROOT histograms or numpy arrays')

        self.sigPoints = np.array(sigPtConstruct,copy=True,dtype='d')
        self.bkgPoints = np.array(bkgPtConstruct,copy=True,dtype='d')
        self.bmax, self.bmin = self.bkgPoints.max(), self.bkgPoints.min()
        self.smax, self.smin = self.sigPoints.max(), self.sigPoints.min()

        if interpolate:
            self.interpolation = spi.interp1d(self.sigPoints,self.bkgPoints,fill_value='extrapolate')

    def plot(self,on,*args,**kwargs):
        """
        Plot the ROC curve on a matplotlib plottable axis

        args and kwargs are sent to ``on.plot(...)``

        Parameters
        ----------
        on: the plottable object, like matplotlib.pyplot or a matplotlib axis
        """
        on.plot(self.sigPoints,self.bkgPoints,*args,**kwargs)

    def efficiency(self,at_sig=0.9,at_bkg=0.1,norm_by_entries=False,return_inv=False):
        """
        Calculate the background efficiency at a given signal
        efficiency.  If the interpolation object is not created yet,
        this function will create one.
        
        Parameters
        ----------
        at_sig: the target signal efficiency
        at_bkg: the target background efficiency
        norm_by_entries: normalize the error from number of entries (instead of integral)

        Returns
        -------
        float
            The background efficiency value
        float
            The error

        """
        if not hasattr(self,'interpolation'):
            self.interpolation = spi.interp1d(self.sigPoints,self.bkgPoints,fill_value='extrapolate')
        else:
            pass
        if norm_by_entries:
            normfactorsig = self._sigRootHist.GetEntries()
            normfactorbkg = self._bkgRootHist.GetEntries()
        else:
            normfactorsig = self.sigInteg
            normfactorbkg = self.bkgInteg
        inv_interp = spi.interp1d(self.bkgPoints,self.sigPoints,fill_value='extrapolate')
        eff = self.interpolation(at_sig)
        err = np.sqrt(eff*(1-eff)/normfactorbkg)
        eff2 = inv_interp(at_bkg)
        err2 = np.sqrt(eff2*(1-eff2)/normfactorsig)
        if return_inv:
            return eff, np.sqrt(err*err + err2*err2), env_interp
        return eff, np.sqrt(err*err + err2*err2)
