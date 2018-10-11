#!/usr/bin/env python3
import json

with open("tms-stations.json", "r") as read_file:
    data = json.load(read_file)
    
features = []
for sta in data["features"]:
    if sta["properties"]["province"] == "Uusimaa":
        features.append( sta )

data["features"] = features
        
with open('tms-stations-uusimaa.json', 'w') as data_file:
    data = json.dump(data, data_file)
