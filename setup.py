#!/usr/bin/env python3

import os

from setuptools import find_packages, setup

directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="termtyper",
    version="1.0.0",
    description="Practice Your typing speeds without leaving the terminal.",
    author="Piotr Skowroński",
    license="GPLv3",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    package_dir={"termtyper": "termtyper"},
    package_data={"termtyper": ["words/*.json"]},
    classifiers=[
        "Environment :: Console",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    entry_points={
        "console_scripts": [
            "termtyper=termtyper.main:main",
        ],
    },
    python_requires=">=3.10",
    extras_require={
        "formatting": [
            "black",
        ],
        "linting": [
            "flake8",
            "mypy",
        ],
    },
)
