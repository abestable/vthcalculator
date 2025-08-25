#!/usr/bin/env python3
"""
Setup script for VthCalculator package.
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="vthcalculator",
    version="1.0.0",
    author="Alberto Bestable",
    author_email="alberto.bestable@example.com",
    description="Tool per l'analisi della tensione di soglia (Vth) dei transistor MOS",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/abestable/vthcalculator",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Electronic Design Automation",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "vth-gui=vthcalculator.gui.main:main",
            "vth-extract=vthcalculator.core.vth_extractor:main",
            "vth-analyze=vthcalculator.analysis.derivative_analyzer:main",
        ],
    },
    include_package_data=True,
    package_data={
        "vthcalculator": [
            "config/*.yaml",
            "config/analysis_configs/*.yaml",
        ],
    },
    keywords="mosfet vth threshold voltage electronics semiconductor analysis",
    project_urls={
        "Bug Reports": "https://github.com/abestable/vthcalculator/issues",
        "Source": "https://github.com/abestable/vthcalculator",
        "Documentation": "https://github.com/abestable/vthcalculator/docs",
    },
)

