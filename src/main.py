import api
import os

API = api.Api(os.environ.get("USERNAME"), os.environ.get("PASSWORD"), os.environ.get("TOKEN"))

params = {
    "startDate": "2023-03-01",
    "completionDate": "2023-04-01",
}

result = API.getLast(params)
arr = []

for item in result["data"]["features"]:
    arr.append({"title": item["properties"]["title"], "date": item["properties"]["startDate"], "link": item["properties"]["services"]["download"]["url"]})

print(len(arr))