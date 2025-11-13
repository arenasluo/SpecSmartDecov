"""
Setup configuration for SpecSmartDecov package.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text() if (this_directory / "README.md").exists() else ""

setup(
    name="specsmartdecov",
    version="1.0.0",
    author="Weijun (Eric) Luo",
    author_email="ericluo@bu.edu",
    description="Spectroscopy peak fitting package using Voigt or LogNormal line shapes",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/arenasluo/SpecSmartDecov",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Scientific/Engineering :: Chemistry",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=[
        "numpy>=1.19.0",
        "scipy>=1.5.0",
        "matplotlib>=3.3.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.10",
            "black>=20.8b1",
            "flake8>=3.8",
        ],
    },
    keywords="spectroscopy raman photoluminescence peak-fitting voigt lognormal deconvolution",
    project_urls={
        "Bug Reports": "https://github.com/arenasluo/SpecSmartDecov/issues",
        "Source": "https://github.com/arenasluo/SpecSmartDecov",
    },
)
