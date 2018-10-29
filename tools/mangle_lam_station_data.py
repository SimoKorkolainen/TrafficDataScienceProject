#!/usr/bin/env python3

import json
import copy
import csv

dataset = {}
dataset2 = {}
with open('../combined.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        if not  row['station_id' ] in dataset:
            dataset[ row['station_id' ] ] = []
        if not   row['station_id' ] in dataset2:
            dataset2[ row['station_id' ] ] = { 'weatherLatitude': row['weatherLatitude'], 'weatherLongitude': row['weatherLongitude'], 'speed_limit': row['speed_limit'], 'speed_limit_winter': row['speed_limit_winter'] }
            
        dataset[  row['station_id' ] ].append( { 't2m': row['t2m'],
            'ws_10min': row['ws_10min'],
            'wg_10min': row['wg_10min'],
            'wd_10min': row['wd_10min'],
            'rh': row['rh'],
            'td': row['td'],
            'r_1h': row['r_1h'],
            'ri_10min': row['ri_10min'],
            'snow_aws': row['snow_aws'],
            'vis': row['vis'],
            'n_man': row['n_man'],
            'hour': row['hour'],
            'day': row['day'],
            'year': row['year'],
            'n_cars': row['n_cars'],
            'n_speeding_cars': row['n_speeding_cars'] } )
            
with open('../tms-stations-uusimaa.json', 'r') as infile:
    tms = json.load(infile)

for feature in tms['features']:
    station_id = str( feature['properties']['tmsNumber'] )
    if not station_id in dataset:
        dataset[ station_id ] = []

for key in dataset.keys():
    with open('../map-viewer/data/measurements/lam_' + key +'.csv', 'w') as outfile:
        fieldnames = ['t2m', 'ws_10min', 'wg_10min', 'wd_10min', 'rh', 'td', 'r_1h', 'ri_10min', 'snow_aws', 'vis', 'n_man', 'hour', 'day', 'year', 'n_cars', 'n_speeding_cars' ]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(dataset[ key ])
