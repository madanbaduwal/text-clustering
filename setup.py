# This code is only work when you make a package locally or in pypi

# !/usr/bin/env python
 
from pathlib import Path
from setuptools import setup,find_packages

 
BASE_DIR = Path(__file__).parent

# Load packages from requirements.txt
with open(Path(BASE_DIR, "requirements.txt")) as file:
    required_packages = [ln.strip() for ln in file.readlines()]

test_packages = [
    "great-expectations==0.13.14",
    "pytest==6.0.2",
    "pytest-cov==2.10.1",
]

dev_packages = [
    "black==20.8b1",
    "flake8==3.8.3",
    "isort==5.5.3",
    "jupyterlab==2.2.8",
    "pre-commit==2.11.1",
]

docs_packages = [
    "mkdocs==1.1.2",
    "mkdocs-macros-plugin==0.5.0",
    "mkdocs-material==6.2.4",
    "mkdocstrings==0.14.0",
]

setup(
    install_requires=[required_packages],
    name="sse",  # name of the package , pip install name of the package
    version="0.0.1",
    author="Madan Baduwal",
    author_email="madan@fusemachines.com",
    description="Student status Engine",
    # url="https://github.com/MadanBaduwal/ai_library",
    # project_urls={
    #     "Bug Tracker": "https://github.com/MadanBaduwal/ai_library/issues",
    # },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    # packages = find_packages() # find all the packages automatically
    # packages = ['src'], # You can define packages manually
    # packages = find_packages("src"), # Specific package only
    # package_dir = {'': 'src'}, # {"package name ": "Tyo package ko location"}# Listing whole packages  
    python_requires=">=3.6",

    extras_require={
        "test": test_packages,
        "dev": test_packages + dev_packages + docs_packages,
        "docs": docs_packages,
    },

    entry_points={
        "console_scripts": [
            "ssev2 = interfaces.command-line.setuptoolcli:app", 
        ],
    },


)


# Usage
# Make package in local
# We can install our package for different situations like so:
# Install from setup.py (-e, --editable installs a project in develop mode)(setup.py bata install garni package locally)
# Create a virtualenv for your application and activate it, and go to your project directory
## python -m pip install -e .            # installs required packages only
## python -m pip install -e ".[dev]"     # installs required + dev packages
## python -m pip install -e ".[test]"    # installs required + test packages

# from entry point
## ssev2 --help


# Upload package to PYPI

## python3 -m pip install --upgrade build
## python3 -m pip install --upgrade twine
## python3 -m twine upload --repository testpypi dist/*
