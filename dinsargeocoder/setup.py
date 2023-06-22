from setuptools import find_packages, setup

setup(
    name='dinsargeocoder',
    packages=find_packages(),
    version='3.2.1',
    description='DInSAR Geocoder',
    author='Francescopaolo Sica, Bertrand Sophie',
    license='MIT',
    install_requires=['snappy', 'numpy', 'rasterio', 'gdal', 'matplotlib'],
)