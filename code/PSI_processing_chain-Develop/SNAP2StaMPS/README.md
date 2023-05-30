# Snap2StaMPS processing

![processing_chain](img/processing%20chain.png)

#

## Structure

The project structure should look like the following upon creation

```
.
├── README.md
├── exports
│   ├── Project
│   │   ├── master
│   │   └── slaves
│   └── bin
├── img
│   └── *.png
└── snap_to_stamps_export_all_swaths.py
```

The following folders are created automatically

- split
- coreg
- ifg
- merge

#

## Usage

Download the SAR images of interest. Select the master image used for the processing and move it to the **exports/Project/master** folder. Move the rest of the image to the **exports/Project/slaves** folder. Images must be in the **.zip** format.

_Note: the automatic designation function of the optimal master image to use is issuing an error thus the SAR image to be used as the master image has to be chosen either ahead of time using a different mean or arbitrarily._

#

## Run

```bash
python3.8 snap_to_stamps_export_all_swaths.py
```

#

## Benchmark

The expected running times fo rthe different functions are as follows (per image) using 43Go RAM for snappy and 16Go javaCacheSize

- Apply Orbit File & Split --> ~1min
- Coregistration & Interferogram generation --> ~5min
- Merge & Geocoding --> ~10min (.dim) / ~20min (.dim + .tif)

The final output results can be found in **exports/Project/merge**.

_Note: the final output format can be set in function line 283._
