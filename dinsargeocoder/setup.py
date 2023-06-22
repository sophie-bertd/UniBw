from setuptools import find_packages, setup

setup(
    name='dinsargeocoder',
    packages=find_packages(),
    version='3.3.1',
    description='DInSAR Geocoder',
    author='Francescopaolo Sica, Bertrand Sophie',
    license='MIT',
    install_requires=['snappy'],
)