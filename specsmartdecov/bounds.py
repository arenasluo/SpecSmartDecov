"""
Parameter bounds generation for constrained fitting.
"""

import numpy as np


def generate_bounds(x, y, initial_guess, n_peaks, bg_type='bg1', peak_type='voigt'):
    """
    Generate lower and upper bounds for fitting parameters.

    Parameters
    ----------
    x : array_like
        Independent variable
    y : array_like
        Dependent variable (spectrum)
    initial_guess : array_like
        Initial parameter guess
    n_peaks : int
        Number of peaks
    bg_type : str, optional
        Background type: 'bg0', 'bg1', 'bg2', 'bg3', 's'
    peak_type : str, optional
        Peak type: 'voigt' or 'lognormal'

    Returns
    -------
    tuple
        (lower_bounds, upper_bounds) arrays
    """
    lower_bounds = []
    upper_bounds = []

    param_idx = 0

    # Background bounds
    if bg_type == 'bg0':
        pass  # No background
    elif bg_type == 'bg1':
        # Constant background
        lower_bounds.append(0)
        upper_bounds.append(np.max(y))
        param_idx += 1
    elif bg_type == 'bg2':
        # Two-point linear background
        lower_bounds.extend([0, 0])
        upper_bounds.extend([np.max(y), np.max(y)])
        param_idx += 2
    elif bg_type == 'bg3':
        # Linear background with slope
        lower_bounds.extend([0, -np.inf])
        upper_bounds.extend([np.max(y), np.inf])
        param_idx += 2
    elif bg_type == 's':
        # Shirley background
        pass

    # Peak bounds
    x_range = x[-1] - x[0]
    y_range = np.max(y) - np.min(y)

    for i in range(n_peaks):
        if peak_type == 'voigt':
            # Voigt parameters: [amplitude, center, nu, sigma]

            # Amplitude bounds
            lower_bounds.append(0)
            upper_bounds.append(y_range * 10)

            # Center bounds
            lower_bounds.append(x[0])
            upper_bounds.append(x[-1])

            # Nu bounds (0 to 1: 0=Lorentzian, 1=Gaussian)
            lower_bounds.append(0)
            upper_bounds.append(1)

            # Sigma bounds
            lower_bounds.append(x_range / 1000)
            upper_bounds.append(x_range)

        elif peak_type == 'lognormal':
            # LogNormal parameters: [amplitude, mode, zero, fwhm]

            # Amplitude bounds
            lower_bounds.append(0)
            upper_bounds.append(y_range * 10)

            # Mode bounds
            lower_bounds.append(x[0])
            upper_bounds.append(x[-1])

            # Zero bounds (must be > mode)
            current_mode = initial_guess[param_idx + 1]
            lower_bounds.append(current_mode + x_range / 1000)
            upper_bounds.append(x[-1] + x_range)

            # FWHM bounds
            lower_bounds.append(x_range / 1000)
            upper_bounds.append(x_range)

        param_idx += 4

    return np.array(lower_bounds), np.array(upper_bounds)


def update_bounds(lower_bounds, upper_bounds, param_idx, new_lower, new_upper):
    """
    Update specific parameter bounds.

    Parameters
    ----------
    lower_bounds : array_like
        Current lower bounds
    upper_bounds : array_like
        Current upper bounds
    param_idx : int
        Parameter index to update
    new_lower : float
        New lower bound
    new_upper : float
        New upper bound

    Returns
    -------
    tuple
        Updated (lower_bounds, upper_bounds)
    """
    lower_bounds = np.array(lower_bounds)
    upper_bounds = np.array(upper_bounds)

    lower_bounds[param_idx] = new_lower
    upper_bounds[param_idx] = new_upper

    return lower_bounds, upper_bounds


def validate_bounds(params, lower_bounds, upper_bounds):
    """
    Check if parameters are within bounds.

    Parameters
    ----------
    params : array_like
        Parameters to validate
    lower_bounds : array_like
        Lower bounds
    upper_bounds : array_like
        Upper bounds

    Returns
    -------
    bool
        True if all parameters are within bounds
    """
    return np.all((params >= lower_bounds) & (params <= upper_bounds))


def adjust_params_to_bounds(params, lower_bounds, upper_bounds):
    """
    Adjust parameters to be within bounds.

    Parameters
    ----------
    params : array_like
        Parameters to adjust
    lower_bounds : array_like
        Lower bounds
    upper_bounds : array_like
        Upper bounds

    Returns
    -------
    array_like
        Adjusted parameters
    """
    params = np.array(params)
    params = np.maximum(params, lower_bounds)
    params = np.minimum(params, upper_bounds)

    return params
