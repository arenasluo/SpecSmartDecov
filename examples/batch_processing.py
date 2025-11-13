"""
Batch processing example for SpecSmartDecov package.

This example demonstrates how to:
1. Generate multiple synthetic spectra
2. Process them in batch mode
3. Compare results
4. Export summary statistics
"""

import numpy as np
import matplotlib.pyplot as plt
from specsmartdecov.core import batch_process
from specsmartdecov.plotting import plot_comparison
import os


def generate_multiple_spectra(n_files=5):
    """
    Generate multiple synthetic spectra with varying parameters.
    """
    print(f"Generating {n_files} synthetic spectra...")

    # Create output directory
    os.makedirs('batch_data', exist_ok=True)

    file_list = []

    for i in range(n_files):
        # X-axis
        x = np.linspace(400, 800, 1000)

        # Varying background
        bg_offset = 40 + i * 5
        background = bg_offset + 0.015 * (x - 400)

        # Peak 1 (position varies slightly)
        peak1_center = 520 + i * 2
        peak1_amplitude = 300 + i * 20
        peak1_width = 15 + i * 0.5
        peak1 = peak1_amplitude * np.exp(-((x - peak1_center) ** 2) / (2 * peak1_width ** 2))

        # Peak 2
        peak2_center = 580
        peak2_amplitude = 450 - i * 10
        peak2_width = 20
        peak2 = peak2_amplitude * np.exp(-((x - peak2_center) ** 2) / (2 * peak2_width ** 2))

        # Combine
        y = background + peak1 + peak2

        # Add noise
        noise = np.random.normal(0, 8, size=y.shape)
        y_noisy = y + noise

        # Save to file
        filename = f'batch_data/spectrum_{i + 1:03d}.txt'
        data = np.column_stack([x, y_noisy])
        np.savetxt(filename, data, fmt='%.6f',
                  header='wavelength intensity', comments='# ')

        file_list.append(filename)
        print(f"  Created: {filename}")

    print()
    return file_list


def analyze_batch_results(results):
    """
    Analyze and summarize batch processing results.
    """
    print("=" * 80)
    print("Batch Processing Summary")
    print("=" * 80)
    print()

    # Extract statistics
    r_squared_values = [r.r_squared for r in results if r is not None]
    resnorm_values = [r.resnorm for r in results if r is not None]

    # Peak 1 centers (assuming background type bg3, peak params start at index 2)
    peak1_centers = [r.parameters[2 + 1] for r in results if r is not None]
    peak1_amplitudes = [r.parameters[2 + 0] for r in results if r is not None]

    print(f"Number of spectra processed: {len(results)}")
    print(f"Successful fits: {len([r for r in results if r is not None])}")
    print()

    print("R² Statistics:")
    print(f"  Mean: {np.mean(r_squared_values):.6f}")
    print(f"  Std:  {np.std(r_squared_values):.6f}")
    print(f"  Min:  {np.min(r_squared_values):.6f}")
    print(f"  Max:  {np.max(r_squared_values):.6f}")
    print()

    print("Peak 1 Center Statistics:")
    print(f"  Mean: {np.mean(peak1_centers):.2f}")
    print(f"  Std:  {np.std(peak1_centers):.2f}")
    print(f"  Min:  {np.min(peak1_centers):.2f}")
    print(f"  Max:  {np.max(peak1_centers):.2f}")
    print()

    print("Peak 1 Amplitude Statistics:")
    print(f"  Mean: {np.mean(peak1_amplitudes):.2f}")
    print(f"  Std:  {np.std(peak1_amplitudes):.2f}")
    print()

    # Create summary plot
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # R² distribution
    axes[0, 0].hist(r_squared_values, bins=10, edgecolor='black', alpha=0.7)
    axes[0, 0].set_xlabel('R²')
    axes[0, 0].set_ylabel('Frequency')
    axes[0, 0].set_title('R² Distribution')
    axes[0, 0].grid(True, alpha=0.3)

    # Peak centers
    axes[0, 1].plot(range(1, len(peak1_centers) + 1), peak1_centers, 'o-', markersize=8)
    axes[0, 1].set_xlabel('Spectrum Number')
    axes[0, 1].set_ylabel('Peak 1 Center')
    axes[0, 1].set_title('Peak 1 Center Position')
    axes[0, 1].grid(True, alpha=0.3)

    # Peak amplitudes
    axes[1, 0].plot(range(1, len(peak1_amplitudes) + 1), peak1_amplitudes, 's-', markersize=8, color='orange')
    axes[1, 0].set_xlabel('Spectrum Number')
    axes[1, 0].set_ylabel('Peak 1 Amplitude')
    axes[1, 0].set_title('Peak 1 Amplitude')
    axes[1, 0].grid(True, alpha=0.3)

    # Residual norms
    axes[1, 1].plot(range(1, len(resnorm_values) + 1), resnorm_values, '^-', markersize=8, color='green')
    axes[1, 1].set_xlabel('Spectrum Number')
    axes[1, 1].set_ylabel('Residual Norm')
    axes[1, 1].set_title('Fit Quality (Residual Norm)')
    axes[1, 1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('batch_summary.png', dpi=300, bbox_inches='tight')
    print("Summary plot saved to: batch_summary.png")
    print()

    plt.show()


def main():
    """
    Main batch processing example.
    """
    print()
    print("=" * 80)
    print("SpecSmartDecov - Batch Processing Example")
    print("=" * 80)
    print()

    # Generate synthetic spectra
    file_list = generate_multiple_spectra(n_files=5)

    # Process in batch mode
    print("Processing spectra in batch mode...")
    print("-" * 80)

    results = batch_process(
        file_list,
        output_dir='batch_results',
        x_range='all',
        n_peaks=2,
        bg_type='bg3',
        peak_type='voigt',
        initial_guess='auto',
        verbose=False  # Suppress individual fit outputs
    )

    print("-" * 80)
    print()

    # Analyze results
    analyze_batch_results(results)

    # Compare first 3 fits
    print("Creating comparison plot for first 3 spectra...")
    if len(results) >= 3:
        plot_comparison(
            results[:3],
            labels=[f'Spectrum {i + 1}' for i in range(3)],
            save_path='batch_comparison.png',
            dpi=300
        )
        print("Comparison plot saved to: batch_comparison.png")
        print()

    print("=" * 80)
    print("Batch processing example completed!")
    print("=" * 80)
    print()
    print("Output directories created:")
    print("  - batch_data/     : Input spectra")
    print("  - batch_results/  : Fitting results")
    print()
    print("Output files created:")
    print("  - batch_summary.png    : Statistical summary")
    print("  - batch_comparison.png : First 3 spectra comparison")
    print()


if __name__ == '__main__':
    main()
