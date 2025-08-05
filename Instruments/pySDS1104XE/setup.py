from setuptools import setup, find_packages

setup(
    name="pySDS1104XE",
    version="0.1.0",
    packages=find_packages(),
    install_requires=["pyvisa"],
    author="Your Name",
    description="Driver for Siglent SDS1104X-E Oscilloscope",
)
