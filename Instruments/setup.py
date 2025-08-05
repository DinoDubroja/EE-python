# setup.py
from setuptools import setup, find_packages

setup(
    name="siglent",            # any name you like
    version="0.1.0",
    packages=find_packages(),  # will discover SDG2122X and SDG3303X
)
