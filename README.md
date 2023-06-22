# Geocoding script

The aim of this script is to automate the coregistration and geocoding process of large stacks of SAR images.

## Dependencies

- [dinsargeocoder]()

## Requirements

In order to function properly, the initial file structure should look like the following:

```
.
├── input
│   ├── master
│   │   └── master.zip
│   └── slaves
│       └── *.zip
└── output
```

The master folder containing the image to use as the master image in a _.zip_ file format.
The slaves folder containing the rest of the images in a _.zip_ file format.

## Usage

Once the file structure has been correctly defined start the script:

```sh
python3 main.py
```

Once the processes are completed you can find the results under _exports/output/geocoding_.
