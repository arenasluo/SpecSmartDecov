"""
Input/Output utilities for spectroscopy data.
"""

import numpy as np
import struct
from pathlib import Path


def load_txt(file_path, delimiter=None, skip_header=0):
    """
    Load data from text file.

    Parameters
    ----------
    file_path : str
        Path to text file
    delimiter : str, optional
        Column delimiter. If None, uses whitespace
    skip_header : int, optional
        Number of header lines to skip

    Returns
    -------
    tuple
        (x, y) data arrays
    """
    data = np.loadtxt(file_path, delimiter=delimiter, skiprows=skip_header)

    if data.ndim == 1:
        raise ValueError("Data must have at least 2 columns")

    x = data[:, 0]
    y = data[:, 1]

    return x, y


def load_csv(file_path, skip_header=0):
    """
    Load data from CSV file.

    Parameters
    ----------
    file_path : str
        Path to CSV file
    skip_header : int, optional
        Number of header lines to skip

    Returns
    -------
    tuple
        (x, y) data arrays
    """
    return load_txt(file_path, delimiter=',', skip_header=skip_header)


def load_spe(file_path):
    """
    Load SPE (Princeton Instruments) format file.

    This is a basic implementation based on the MATLAB loadSPE.m function.

    Parameters
    ----------
    file_path : str
        Path to SPE file

    Returns
    -------
    dict
        Dictionary containing:
        - 'wavelength': wavelength/x-axis data
        - 'intensity': intensity/y-axis data
        - 'header': file header information
    """
    with open(file_path, 'rb') as f:
        # Read header (simplified version)
        header = {}

        # Controller version
        f.seek(0)
        header['version'] = struct.unpack('f', f.read(4))[0]

        # Data dimensions
        f.seek(42)
        xdim = struct.unpack('H', f.read(2))[0]

        f.seek(656)
        ydim = struct.unpack('H', f.read(2))[0]

        # Number of frames
        f.seek(1446)
        num_frames = struct.unpack('I', f.read(4))[0]

        header['xdim'] = xdim
        header['ydim'] = ydim
        header['num_frames'] = num_frames

        # Data type
        f.seek(108)
        data_type = struct.unpack('h', f.read(2))[0]

        # Read spectral data
        f.seek(4100)  # Data starts at byte 4100

        # Determine data type
        if data_type == 0:  # float
            dtype = np.float32
        elif data_type == 1:  # long
            dtype = np.int32
        elif data_type == 2:  # short
            dtype = np.int16
        elif data_type == 3:  # unsigned short
            dtype = np.uint16
        else:
            dtype = np.float32

        # Read data
        data = np.fromfile(f, dtype=dtype, count=xdim * ydim * num_frames)
        data = data.reshape((num_frames, ydim, xdim))

        # Sum across frames if multiple
        if num_frames > 1:
            intensity = np.sum(data, axis=0)
        else:
            intensity = data[0, :, :]

        # If 2D, sum across one dimension to get 1D spectrum
        if intensity.ndim == 2:
            intensity = np.sum(intensity, axis=0)

        # Read calibration for wavelength axis
        f.seek(3000)
        polynom_order = struct.unpack('b', f.read(1))[0]

        f.seek(3263)
        calibration = []
        for i in range(6):
            calib_val = struct.unpack('d', f.read(8))[0]
            calibration.append(calib_val)

        # Calculate wavelength
        if calibration[0] != 0 or calibration[1] != 0:
            pixels = np.arange(xdim)
            wavelength = np.zeros(xdim)

            for i in range(polynom_order + 1):
                wavelength += calibration[i] * (pixels ** i)
        else:
            # No calibration, use pixel numbers
            wavelength = np.arange(xdim)

    return {
        'wavelength': wavelength,
        'intensity': intensity,
        'header': header
    }


def save_txt(file_path, x, y, header=None):
    """
    Save data to text file.

    Parameters
    ----------
    file_path : str
        Output file path
    x : array_like
        X data
    y : array_like
        Y data
    header : str, optional
        Header text to include
    """
    data = np.column_stack([x, y])

    if header is not None:
        # Ensure header lines start with #
        header_lines = header.split('\n')
        header_lines = ['# ' + line if not line.startswith('#') else line
                       for line in header_lines]
        header = '\n'.join(header_lines)

    np.savetxt(file_path, data, fmt='%.6f', header=header if header else '',
              comments='')

    print(f"Data saved to: {file_path}")


def save_csv(file_path, x, y, header=None):
    """
    Save data to CSV file.

    Parameters
    ----------
    file_path : str
        Output file path
    x : array_like
        X data
    y : array_like
        Y data
    header : str, optional
        Header text
    """
    data = np.column_stack([x, y])

    np.savetxt(file_path, data, fmt='%.6f', delimiter=',',
              header=header if header else '', comments='')

    print(f"Data saved to: {file_path}")


def load_multiple_files(file_pattern):
    """
    Load multiple files matching a pattern.

    Parameters
    ----------
    file_pattern : str
        File pattern (supports wildcards, e.g., 'data/*.txt')

    Returns
    -------
    list
        List of (file_path, x, y) tuples
    """
    from glob import glob

    files = glob(file_pattern)
    results = []

    for file_path in sorted(files):
        try:
            x, y = load_txt(file_path)
            results.append((file_path, x, y))
        except Exception as e:
            print(f"Warning: Failed to load {file_path}: {e}")

    return results


def export_fit_parameters(fit_result, file_path):
    """
    Export fit parameters to a structured text file.

    Parameters
    ----------
    fit_result : FitResult
        Fitting result object
    file_path : str
        Output file path
    """
    with open(file_path, 'w') as f:
        f.write("# Fit Parameters Export\n")
        f.write(f"# Number of peaks: {fit_result.n_peaks}\n")
        f.write(f"# Background type: {fit_result.bg_type}\n")
        f.write(f"# Peak type: {fit_result.peak_type}\n")
        f.write(f"# R-squared: {fit_result.r_squared:.6f}\n")
        f.write(f"# Residual norm: {fit_result.resnorm:.6e}\n")
        f.write("#\n")

        # Background parameters
        f.write("# Background Parameters:\n")
        param_idx = 0
        if fit_result.bg_type == 'bg1':
            f.write(f"bg_constant\t{fit_result.parameters[0]:.6f}\t{fit_result.confidence_intervals[0]:.6f}\n")
            param_idx = 1
        elif fit_result.bg_type == 'bg2':
            f.write(f"bg_constant_1\t{fit_result.parameters[0]:.6f}\t{fit_result.confidence_intervals[0]:.6f}\n")
            f.write(f"bg_constant_2\t{fit_result.parameters[1]:.6f}\t{fit_result.confidence_intervals[1]:.6f}\n")
            param_idx = 2
        elif fit_result.bg_type == 'bg3':
            f.write(f"bg_constant\t{fit_result.parameters[0]:.6f}\t{fit_result.confidence_intervals[0]:.6f}\n")
            f.write(f"bg_slope\t{fit_result.parameters[1]:.6f}\t{fit_result.confidence_intervals[1]:.6f}\n")
            param_idx = 2

        f.write("#\n")
        f.write("# Peak Parameters:\n")

        if fit_result.peak_type == 'voigt':
            f.write("# peak\tamplitude\t±\tcenter\t±\tnu\t±\tsigma\t±\tarea\n")
        else:
            f.write("# peak\tamplitude\t±\tmode\t±\tzero\t±\tfwhm\t±\tarea\n")

        for i in range(fit_result.n_peaks):
            idx = param_idx + i * 4
            f.write(f"{i + 1}\t")
            for j in range(4):
                f.write(f"{fit_result.parameters[idx + j]:.6f}\t{fit_result.confidence_intervals[idx + j]:.6f}\t")
            f.write(f"{fit_result.peak_areas[i]:.6f}\n")

    print(f"Parameters exported to: {file_path}")
