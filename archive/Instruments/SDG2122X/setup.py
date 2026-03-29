# setup.py
from setuptools import setup, find_packages

setup(
    name="SDG2122X",
    version="0.1.0",
    packages=find_packages(),         # finds the mylib/ package
    install_requires=[                # list any dependencies here
        # e.g. "numpy>=1.20.0",
    ],
    author="Dino Dubroja",
    description="SDG2122X library",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
)
