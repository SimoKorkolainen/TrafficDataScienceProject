#!/usfloar/bin/env python3

import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import json
import csv

### 1. part: get the link for each LAM station

with open("tms-stations-uusimaa.json", "r") as read_file:
    stations = json.load(read_file)
    
linkki = []
for area in ['ITA-UUSIMAA', 'UUSIMAA_1', 'UUSIMAA_2']:
    linkki.append( gpd.read_file( area + '/DR_LINKKI_K.shp' ) )

linkki = pd.concat( linkki )
#linkki = linkki.to_crs(epsg=4326)

# remove minor roads 
linkki = linkki[ linkki['LINKKITYYP'] < 5 ]

linkki = linkki.reset_index()

stations2 = {}
for sta in stations["features"]:
    #p_sta = Point( sta["geometry"]["coordinates"] )
    p_sta = Point( sta["properties"]["coordinatesETRS89"][0], sta["properties"]["coordinatesETRS89"][1] )
    roadNumber = sta["properties"]["roadAddress"]["roadNumber"]
    
    stations2[ sta["id"] ] = { 'roadNumber': roadNumber }

    i = 0
    nearest_linkki = -1
    d = float('Inf')
    for shape in linkki.geometry:
        if linkki.loc[ i, "TIENUMERO" ] == roadNumber:
            if p_sta.distance( shape ) < d:
                d = p_sta.distance( shape )
                nearest_linkki = i
        i += 1
    
    stations2[ sta["id"] ]["LINK_ID"] = linkki.loc[ nearest_linkki, "LINK_ID" ]
    stations2[ sta["id"] ]["SEGM_ID"] = linkki.loc[ nearest_linkki, "SEGM_ID" ]

#del linkki

### 2. part: road width for each station
width = []
for area in ['ITA-UUSIMAA', 'UUSIMAA_1', 'UUSIMAA_2']:
    width.append( gpd.read_file( area + '/DR_LEVEYS_K.shp' ) )

width = pd.concat( width )
width = width.reset_index()
width = width.to_crs( epsg=4326)

#for sta in stations["features"]:
#    p_sta = Point( sta["geometry"]["coordinates"] )
    
    #i = 0
    #nearest = -1
    #d = float('Inf')
    #for shape in width.geometry:
        #if p_sta.distance( shape ) < d:
            ##d = p_sta.distance( shape )
            #3nearest = i
        ##i += 1

    ##stations2[ sta["id"] ]["ROAD_WIDTH"] = width.loc[ nearest, "ARVO" ]
    ##print( stations2[ sta["id"] ]["ROAD_WIDTH"] )

#del width

### part: speed limit
speed = []
for area in ['ITA-UUSIMAA', 'UUSIMAA_1', 'UUSIMAA_2']:
    speed.append( gpd.read_file( area + '/DR_NOPEUSRAJOITUS_K.shp' ) )

speed = pd.concat( speed )
speed = speed.reset_index()
speed = speed.to_crs( epsg=4326)

#for sta in stations["features"]:
#    p_sta = Point( sta["geometry"]["coordinates"] )
#    
#    i = 0
#    nearest = -1
#    d = float('Inf')
#    for shape in speed.geometry:
#        if p_sta.distance( shape ) < d:
#            d = p_sta.distance( shape )
#            nearest = i
#        i += 1

#    stations2[ sta["id"] ]["speed_limit"] = speed.loc[ nearest, "ARVO" ]
#    print( stations2[ sta["id"] ]["speed_limit"] )

### part: speed limit
speed_winter = []
for area in ['ITA-UUSIMAA', 'UUSIMAA_1', 'UUSIMAA_2']:
    speed_winter.append( gpd.read_file( area + '/DR_TALVINOPEUSRAJOITUS_K.shp' ) )

speed_winter = pd.concat( speed_winter )
speed_winter = speed_winter.reset_index()
speed_winter = speed_winter.to_crs( epsg=4326)

#for sta in stations["features"]:
#    p_sta = Point( sta["geometry"]["coordinates"] )
#    
#    i = 0
#    nearest = -1
#    d = float('Inf')
#    for shape in speed_winter.geometry:
#        if p_sta.distance( shape ) < d:
#            d = p_sta.distance( shape )
#            nearest = i
#        i += 1

#    stations2[ sta["id"] ]["speed_limit_winter"] = speed_winter.loc[ nearest, "ARVO" ]
#    print( stations2[ sta["id"] ]["speed_limit_winter"] )

for sta in stations["features"]:
    segment_id = stations2[ sta['id'] ]['SEGM_ID']
    tmp = width.loc[ width['SEGM_ID'] == segment_id, "ARVO" ]
    if len( tmp ) > 0:
        stations2[ sta["id"] ]["road_width"] = tmp.values[0]
    else:
        stations2[ sta["id"] ]["road_width"] = "N/A"
    
    tmp = speed.loc[ speed['SEGM_ID'] == segment_id, "ARVO" ]
    if len( tmp ) > 0:
        stations2[ sta["id"] ]["speed_limit"] = tmp.values[0]
    else:
        stations2[ sta["id"] ]["speed_limit"] = "N/A"
    
    tmp = speed_winter.loc[ speed_winter['SEGM_ID'] == segment_id, "ARVO" ]
    if len( tmp ) > 0:
        stations2[ sta["id"] ]["speed_limit_winter"] = tmp.values[0]
    else:
        stations2[ sta["id"] ]["speed_limit_winter"] = stations2[ sta["id"] ]["speed_limit"]
    

### last part: write csv file
with open('road_shape_lam_stations.csv', 'w', newline='') as csvfile:
    fieldnames = ['station_id', 'roadNumber', 'road_width', 'speed_limit', 'speed_limit_winter', 'SEGM_ID', 'LINK_ID']
    datawriter = csv.DictWriter(csvfile, delimiter=',',
                            quotechar='\"', quoting=csv.QUOTE_MINIMAL, fieldnames=fieldnames)
    datawriter.writeheader()
    for sta in stations["features"]:
        datawriter.writerow({'station_id': sta["properties"]["tmsNumber"],  **stations2[ sta["id"] ] } )
    
