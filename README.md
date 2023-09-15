# Geocoding script

The aim of this script is to automate the coregistration and geocoding process of large stacks of Sentinel-1 TOPS SAR images.

## Dependencies

- [docker](https://www.docker.com)
- [dinsargeocoder](https://github.com/AlphardHydrae/UniBw/tree/main/dinsargeocoder)
- [snappy](https://senbox.atlassian.net/wiki/spaces/SNAP/pages/50855941/Configure+Python+to+use+the+SNAP-Python+snappy+interface+SNAP+versions+9)

## Requirements

In order to function properly, make sure you pasted the files in the correct folder:

```
.
├── input
│   ├── master
│   │   └── master.zip
│   └── slaves
│       └── *.zip
└── output
```

## Usage

### Using the provided Docker environment

In the root directory of the project run the following command to start the Dpcker process:

```sh
docker compose up
```

### Using your own python environment

Once the file structure has been correctly defined start the script:

```sh
python3 main.py
```
