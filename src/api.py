import requests
import snappy

class Api:

    def __init__(self, username, password, token):
        self.username = username
        self.password = password
        self.token = token

    def getLast(self, params):
        response = requests.get("http://catalogue.dataspace.copernicus.eu/resto/api/collections/Sentinel1/search.json?", params = params)

        return {"status": response.status_code, "data": response.json()}