from configparser import ConfigParser
from datetime import date

from sentinelsat import SentinelAPI, geojson_to_wkt, read_geojson

# initialize the parser
parser = ConfigParser()
parser.read('query.config')

# connect to the API
api = SentinelAPI(parser.get('Download', 'username'), parser.get('Download', 'password'))

# search by polygon, time, and Hub query keywords
footprint = parser.get('AOI', 'aoi')
products = api.query(footprint=footprint,
                    platformname='Sentinel-1',
                    producttype=parser.get('Search Parameters', 'processingLevel'),
                    sensoroperationalmode=parser.get('Search Parameters', 'beamMode'),
                    relativeorbitnumber=parser.getint('Search Parameters', 'relativeOrbit'),
                    orbitdirection=parser.get('Search Parameters', 'flightDirection'),
                    beginposition=(date(2023, 1, 1), date(2023, 5, 1))
                    )

# print the total number of products found
# print(products)
print(len(products))

# download all results from the search
api.download_all(products)