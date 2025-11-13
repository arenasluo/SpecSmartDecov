"""
Peak shape and background functions for spectroscopy fitting.
"""

import numpy as np
from scipy.special import wofz


def voigt(x, amplitude, center, nu, sigma):
    """
    Voigt profile function.

    A Voigt profile is a convolution of a Gaussian and Lorentzian profile.

    Parameters
    ----------
    x : array_like
        Independent variable (e.g., wavelength, wavenumber)
    amplitude : float
        Scale factor
    center : float
        Peak center position
    nu : float
        Shape parameter (0=Lorentzian, 1=Gaussian)
    sigma : float
        Width parameter (related to FWHM)

    Returns
    -------
    array_like
        Voigt profile values
    """
    sigma = np.abs(sigma)

    # Gaussian component
    gaussian = np.exp(-((x - center) ** 2) / (2 * sigma ** 2)) / (sigma * np.sqrt(2 * np.pi))

    # Lorentzian component
    lorentzian = (sigma / np.pi) / ((x - center) ** 2 + sigma ** 2)

    # Combine based on nu parameter
    profile = nu * gaussian + (1 - nu) * lorentzian

    return amplitude * profile


def voigt_wofz(x, amplitude, center, sigma_g, sigma_l):
    """
    Voigt profile using Faddeeva function (more accurate).

    Parameters
    ----------
    x : array_like
        Independent variable
    amplitude : float
        Scale factor
    center : float
        Peak center
    sigma_g : float
        Gaussian width
    sigma_l : float
        Lorentzian width

    Returns
    -------
    array_like
        Voigt profile values
    """
    z = ((x - center) + 1j * sigma_l) / (sigma_g * np.sqrt(2))
    profile = np.real(wofz(z)) / (sigma_g * np.sqrt(2 * np.pi))
    return amplitude * profile


def lognormal(x, amplitude, mode, zero, fwhm):
    """
    LogNormal distribution (reverse/flipped).

    Parameters
    ----------
    x : array_like
        Independent variable
    amplitude : float
        Scale factor
    mode : float
        Mode of the distribution
    zero : float
        Flip point on x-axis
    fwhm : float
        Full width at half maximum

    Returns
    -------
    array_like
        LogNormal profile values
    """
    # Avoid division by zero
    x_shifted = zero - x
    mask = x_shifted > 0

    result = np.zeros_like(x, dtype=float)

    if np.any(mask):
        # Calculate sigma from FWHM (approximate)
        sigma = fwhm / (2 * np.sqrt(2 * np.log(2)))

        # LogNormal calculation
        x0 = np.log(zero - mode) + sigma ** 2
        log_term = np.log(x_shifted[mask])

        result[mask] = amplitude * np.exp(-(log_term - x0 + sigma ** 2 / 2) ** 2 / (2 * sigma ** 2)) / (
            x_shifted[mask] * sigma * np.sqrt(2 * np.pi)
        )

    return result


def background_constant(x, c0):
    """
    Constant background.

    Parameters
    ----------
    x : array_like
        Independent variable
    c0 : float
        Constant background value

    Returns
    -------
    array_like
        Constant background
    """
    return np.full_like(x, c0, dtype=float)


def background_linear(x, c0, c1):
    """
    Linear background (two-point).

    Parameters
    ----------
    x : array_like
        Independent variable
    c0 : float
        Background at start
    c1 : float
        Background at end

    Returns
    -------
    array_like
        Linear background
    """
    return c0 + (c1 - c0) * (x - x[0]) / (x[-1] - x[0])


def background_slope(x, c0, slope):
    """
    Linear background with slope.

    Parameters
    ----------
    x : array_like
        Independent variable
    c0 : float
        Background constant at start
    slope : float
        Background slope

    Returns
    -------
    array_like
        Linear background
    """
    return c0 + slope * (x - x[0])


def background_shirley(x, y):
    """
    Shirley background calculation (iterative).

    Parameters
    ----------
    x : array_like
        Independent variable
    y : array_like
        Dependent variable (spectrum)

    Returns
    -------
    array_like
        Shirley background
    """
    # Iterative Shirley background
    bg = np.linspace(y[0], y[-1], len(y))

    max_iterations = 50
    tolerance = 1e-6

    for _ in range(max_iterations):
        bg_old = bg.copy()

        # Calculate total peak area above background
        total_area = np.trapz(y - bg, x)

        if total_area <= 0:
            break

        # Update background
        for i in range(len(x)):
            area_right = np.trapz(y[i:] - bg[i:], x[i:])
            bg[i] = y[-1] + (y[0] - y[-1]) * area_right / total_area

        # Check convergence
        if np.max(np.abs(bg - bg_old)) < tolerance:
            break

    return bg


def multi_peak(x, params, bg_type='bg1', peak_type='voigt'):
    """
    Calculate multiple peaks with background.

    Parameters
    ----------
    x : array_like
        Independent variable
    params : array_like
        Parameter vector [bg_params..., peak1_params..., peak2_params..., ...]
    bg_type : str, optional
        Background type: 'bg0', 'bg1', 'bg2', 'bg3', 's'
    peak_type : str, optional
        Peak type: 'voigt' or 'lognormal'

    Returns
    -------
    array_like
        Combined spectrum (background + peaks)
    """
    # Parse background parameters
    if bg_type == 'bg0':
        bg = np.zeros_like(x)
        peak_params = params
    elif bg_type == 'bg1':
        bg = background_constant(x, params[0])
        peak_params = params[1:]
    elif bg_type == 'bg2':
        bg = background_linear(x, params[0], params[1])
        peak_params = params[2:]
    elif bg_type == 'bg3':
        bg = background_slope(x, params[0], params[1])
        peak_params = params[2:]
    elif bg_type == 's':
        # Shirley background handled separately
        bg = np.zeros_like(x)
        peak_params = params
    else:
        bg = background_constant(x, params[0])
        peak_params = params[1:]

    # Calculate peaks
    result = bg.copy()
    n_params_per_peak = 4
    n_peaks = len(peak_params) // n_params_per_peak

    for i in range(n_peaks):
        idx = i * n_params_per_peak
        p = peak_params[idx:idx + n_params_per_peak]

        if peak_type == 'voigt':
            # params: [amplitude, center, nu, sigma]
            result += voigt(x, p[0], p[1], p[2], p[3])
        elif peak_type == 'lognormal':
            # params: [amplitude, mode, zero, fwhm]
            result += lognormal(x, p[0], p[1], p[2], p[3])

    return result


def calculate_peak_area(params, peak_type='voigt'):
    """
    Calculate area under a peak.

    Parameters
    ----------
    params : array_like
        Peak parameters [amplitude, ...]
    peak_type : str
        Peak type: 'voigt' or 'lognormal'

    Returns
    -------
    float
        Area under the peak
    """
    if peak_type == 'voigt':
        amplitude, center, nu, sigma = params
        sigma = np.abs(sigma)

        # Area calculation for Voigt approximation
        gaussian_contrib = nu * np.sqrt(np.pi / np.log(2)) / np.abs(sigma)
        lorentzian_contrib = (1 - nu) / (np.pi * np.abs(sigma))

        area = 0.5 * amplitude / (gaussian_contrib + lorentzian_contrib)

    elif peak_type == 'lognormal':
        amplitude, mode, zero, fwhm = params

        # Area calculation for LogNormal
        sigma = fwhm / (2 * np.sqrt(2 * np.log(2)))
        x0 = np.log(zero - mode) + sigma ** 2
        g = 1 / (sigma * np.sqrt(2 * np.pi) * np.exp(x0 - sigma ** 2 / 2))
        area = amplitude / g

    else:
        area = 0

    return area
