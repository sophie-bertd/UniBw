from setuptools import find_packages, setup

setup(
    name='dinsargeocoder',
    packages=find_packages(),
    version='2.4.0',
    description='DinSAR Geocoder',
    author='Francescopaolo Sica, Bertrand Sophie',
    license='MIT',
    install_requires=['snappy', 'gdal'],
)