"""
SpecSmartDecov - Spectroscopy Peak Fitting Package

A Python package for deconvolution and fitting of spectroscopy data
(Raman/PL) using Voigt or LogNormal line shapes.

Based on the MATLAB package by Weijun (Eric) Luo.
Original: https://www.mathworks.com/matlabcentral/fileexchange/52321

Author: Weijun (Eric) Luo
Contact: ericluo@bu.edu
"""

__version__ = '1.0.0'
__author__ = 'Weijun (Eric) Luo'
__email__ = 'ericluo@bu.edu'

from .core import deconvolve
from .fitting import fit_spectrum
from .functions import voigt, lognormal

__all__ = ['deconvolve', 'fit_spectrum', 'voigt', 'lognormal']
