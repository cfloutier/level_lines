"""
Based on https://github.com/pypa/sampleproject

"""

# Always prefer setuptools over distutils
import pathlib
import re
import setuptools

# install_requires is dynamically created (below) and therefore cannot easily be
# specified in pyproject.toml, so it is specified here.

install_requires = [
    "pyaml>=6",
    "cartopy",
    # + axidraw python api
]


here = pathlib.Path.absolute(pathlib.Path(__file__).parent)

setuptools.setup(
    packages=setuptools.find_packages(exclude=["venv", "docs", "test"]),
    install_requires=install_requires,
)
