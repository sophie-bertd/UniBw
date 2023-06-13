# DInSAR geocoding library

The aim of this library is to eliminate the redundancy of manually setting the SAR processing functions paramaters and to provide ready to use functions.

## Dependencies

- [snappy](https://senbox.atlassian.net/wiki/spaces/SNAP/pages/50855941/Configure+Python+to+use+the+SNAP-Python+snappy+interface+SNAP+versions+9)

## Installation

Inside the library folder:

1. Build the wheel

```sh
python3 setup.py bdist_wheel
```

2. Install the wheel

```sh
pip install .
```

## Usage

Import the library:

```python
import dinsargeocoder
```

Directly use the available functions:

```python
dinsargeocoder.read_product(product)
```

The list of available functions are available below:

- apply_orbit_file(product)
- back_geocoding(master_product, slave_product)
- create_product_array(products)
- enhanced_spectral_diversity(product)
- goldstein_phase_filtering(product)
- interferogram(product)
- merge(product_array)
- multilook(product)
- read_product(product)
- terrain_correction(product)
- topo_phase_removal(product)
- topsar_deburst(product)
- topsar_split(product, subswath)
- write_dim_product(product, save_path)
- write_rat_product(product, save_path)
- write_tiff_product(product, save_path)
