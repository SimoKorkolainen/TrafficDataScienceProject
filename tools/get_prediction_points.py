#!/usfloar/bin/env python3

import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import json

linkki = []
for area in ['ITA-UUSIMAA', 'UUSIMAA_1', 'UUSIMAA_2']:
    linkki.append( gpd.read_file( area + '/DR_LINKKI_K.shp' ) )

linkki = pd.concat( linkki )

# remove minor roads 
linkki = linkki[ linkki['LINKKITYYP'] < 5 ]

linkki = linkki.reset_index()
linkki = linkki.to_crs(epsg=4326)

majorRoads = linkki.loc[ linkki["TIENUMERO"] < 200, "TIENUMERO" ].unique()

maxLen = 0
for roadNumber in majorRoads:
    road = linkki.loc[ linkki["TIENUMERO"] == roadNumber, : ] 
    road = road.loc[ road["AJOSUUNTA"] < 4 , :].dissolve(by='TIENUMERO').geometry
    if float(road.length) > maxLen:
        maxLen = float(road.length)

pointDistance = maxLen / 400

predictionPoints = { "type": "FeatureCollection", "features": [] }
for roadNumber in majorRoads:
    road = linkki.loc[ linkki["TIENUMERO"] == roadNumber, : ] 
    road = road.loc[ road["AJOSUUNTA"] < 4 , :].dissolve(by='TIENUMERO').geometry
    i = 0
    n = 0
    while i < float(road.length):
        point = road.interpolate( i )
        point = json.loads(point.to_json() )
        predictionPoints["features"].append( { "id": str(int(roadNumber)) + "_" + str(n), "type": "Feature", "properties": { "roadAddress": { "roadNumber": roadNumber } }, "geometry": point["features"][0]["geometry"] } )
        
        i += pointDistance
        n += 1

with open('prediction_points.json', 'w') as outfile:
    json.dump(predictionPoints, outfile)
    

####

width = []
for area in ['ITA-UUSIMAA', 'UUSIMAA_1', 'UUSIMAA_2']:
    width.append( gpd.read_file( area + '/DR_LEVEYS_K.shp' ) )

width = pd.concat( width )
width = width.reset_index()
width = width.to_crs( epsg=4326)

speed = []
for area in ['ITA-UUSIMAA', 'UUSIMAA_1', 'UUSIMAA_2']:
    speed.append( gpd.read_file( area + '/DR_NOPEUSRAJOITUS_K.shp' ) )

speed = pd.concat( speed )
speed = speed.reset_index()
speed = speed.to_crs( epsg=4326)

speed_winter = []
for area in ['ITA-UUSIMAA', 'UUSIMAA_1', 'UUSIMAA_2']:
    speed_winter.append( gpd.read_file( area + '/DR_TALVINOPEUSRAJOITUS_K.shp' ) )

speed_winter = pd.concat( speed_winter )
speed_winter = speed_winter.reset_index()
speed_winter = speed_winter.to_crs( epsg=4326)

####
pred2 = {}
for point in predictionPoints["features"]:
    road = linkki.loc[ linkki["TIENUMERO"] == point["properties"]["roadAddress"]["roadNumber"], : ] 
    road = road.loc[ road["AJOSUUNTA"] < 4 , :]
    road = road.reset_index()
    
    p = Point( point["geometry"]["coordinates"][0], point["geometry"]["coordinates"][1]  )
    
    pred2[ point["id"] ] = {}
    
    i = 0
    nearest_linkki = -1
    d = float('Inf')
    for r in road.geometry:
        if p.distance( r ) < d:
                d = p.distance( r )
                nearest_linkki = i
        i += 1
    
    segment_id = road.loc[ nearest_linkki, "SEGM_ID" ]
        
    tmp = width.loc[ width['SEGM_ID'] == segment_id, "ARVO" ]
    if len( tmp ) > 0:
        pred2[ point["id"] ]["road_width"] = tmp.values[0]
    else:
        pred2[ point["id"] ]["road_width"] = "N/A"
    
    tmp = speed.loc[ speed['SEGM_ID'] == segment_id, "ARVO" ]
    if len( tmp ) > 0:
        pred2[ point["id"] ]["speed_limit"] = tmp.values[0]
    else:
        pred2[ point["id"] ]["speed_limit"] = "N/A"
    
    tmp = speed_winter.loc[ speed_winter['SEGM_ID'] == segment_id, "ARVO" ]
    if len( tmp ) > 0:
        pred2[ point["id"] ]["speed_limit_winter"] = tmp.values[0]
    else:
        pred2[ point["id"] ]["speed_limit_winter"] = pred2[ point["id"] ]["speed_limit"]
    

### last part: write csv file
with open('road_shape_prediction_points.csv', 'w', newline='') as csvfile:
    fieldnames = ['prediction_point_id', 'longitude', 'latitude', 'roadNumber', 'road_width', 'speed_limit', 'speed_limit_winter']
    datawriter = csv.DictWriter(csvfile, delimiter=',',
                            quotechar='\"', quoting=csv.QUOTE_MINIMAL, fieldnames=fieldnames)
    datawriter.writeheader()
    for point in predictionPoints["features"]:
        datawriter.writerow({'prediction_point_id': point["id"], 'longitude':  point["geometry"]["coordinates"][0], 'latitude': point["geometry"]["coordinates"][1], **pred2[ point["id"] ] } )
    
