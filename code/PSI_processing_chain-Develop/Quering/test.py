from configparser import ConfigParser
from urllib import response
import asf_search as asf
import logging

# logger = logging.basicConfig()
# import SBAS

# print(asf.__version__)

from shapely.geometry import Polygon

class Download_SLCs_for_PSI:
    def __init__(self, config_filepath) -> None:
        self.config_filepath = config_filepath
        self.parser = ConfigParser()
        self.parser.read(self.config_filepath)
        self.savepath = self.parser.get('Download', 'saveFilePath')
    
    def parser_to_dict(self):
        opts = {
                'platform':getattr(asf.PLATFORM, self.parser.get('Search Parameters','platform')),
                'maxResults': self.parser.getint('Search Parameters','maxResults'),
                'beamMode': getattr(asf.BEAMMODE, self.parser.get('Search Parameters','beamMode')),
                'frame': self.parser.getint('Search Parameters', 'frame'),
                'polarization': getattr(asf.POLARIZATION, self.parser.get('Search Parameters', 'polarization')),
                'processingLevel': getattr(asf.PRODUCT_TYPE, self.parser.get('Search Parameters', 'processingLevel')),
                'relativeOrbit': self.parser.getint('Search Parameters', 'relativeOrbit'),
                'start': self.parser.get('Search Parameters', 'start'),
                'end': self.parser.get('Search Parameters', 'end'),
                "flightDirection": self.parser.get('Search Parameters', 'flightDirection')
            } 
        return opts
    
    def get_urls_for_slcs(self):
        opts = self.parser_to_dict() 
        aoi = self.parser.get('AOI', 'aoi')
        start_date = self.parser.get('Search Parameters', 'start')
        end_date = self.parser.get('Search Parameters', 'end')
        results = asf.geo_search(intersectsWith=aoi, **opts)
        print('*'*40)
        count = asf.search_count(**opts)
        print(f'There are {count} SLCs in between {start_date} and {end_date} with same relative orbit')
        return results
    
    def download_slcs(self):
        import getpass
        import os 
        print('*'*40)
        print('Enter the username and password for Earthdata Login')
        username = input('Username: ')
        password = getpass.getpass('Password: ')
        print('*'*40)
        results = self.get_urls_for_slcs()
        number_of_slcs = int(input('Enter the number of slcs for downloading: '))
        try:
            user_pass_session = asf.ASFSession().auth_with_creds(username, password)
        except asf.ASFAuthenticationError as e:
            print(f'Auth failed: {e}')
        else:
            print('Authentication Success!')
        results[0:number_of_slcs].download(path = self.savepath, session = user_pass_session, processes = 50)
        print('*'*40)
        print('Saved files')
        print(os.listdir(self.savepath))
        
        
if __name__ == '__main__':
    query_config_filepath = 'query.config'
    download1 = Download_SLCs_for_PSI(config_filepath=query_config_filepath).download_slcs()
    
    