#!/usr/bin/env python3

import json
import copy
import csv

with open('../map-viewer/data/prediction_points_updated.json', 'r') as infile:
    dataset = json.load(infile)

shape_info = {}
with open('../road_shape_prediction_points.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        shape_info[ row['prediction_point_id'] ] = { 'speedLimit':  row['speed_limit'], 'speedLimitWinter': row['speed_limit_winter'] }

for i in range(0, len( dataset['features'] ) ):
    for j in range( 0, len( dataset['features'][i]['properties']['data'] ) ):
        temp_date = dataset['features'][i]['properties']['data'][j]['date'].replace( 'EET', '')
        temp_date = temp_date.replace( 'EEST', '')
        temp_date = temp_date[0 : -2 ] + ':00'
        dataset['features'][i]['properties']['data'][j]['date'] = temp_date

dataset2 = { 'prediction_times': [], 'datasets': [] }

for data in dataset['features'][0]['properties']['data']:
    dataset2['prediction_times'].append( data['date'] )

dataset2['prediction_times'].sort()

template_prediction_times = copy.deepcopy( dataset )

for i in range(0, len( template_prediction_times['features'] ) ):
    del template_prediction_times['features'][i]['properties']['data']

for timestamp in dataset2['prediction_times']:
    temp_prediction_times = copy.deepcopy( template_prediction_times )

    for i in range(0, len( dataset['features'] ) ):
        for j in range( 0, len( dataset['features'][i]['properties']['data'] ) ):
            if dataset['features'][i]['properties']['data'][j]['date'] == timestamp:
                temp_prediction_times['features'][i]['properties']['predictionResultColor'] = dataset['features'][i]['properties']['data'][j]['predictionResultColor']
                temp_prediction_times['features'][i]['properties']['predictionResult'] = dataset['features'][i]['properties']['data'][j]['predictionResult']
                temp_prediction_times['features'][i]['properties'].update( shape_info[ temp_prediction_times['features'][i]['id'] ] )
                break
    dataset2['datasets'].append( temp_prediction_times )

with open('../map-viewer/data/prediction_times.json', 'w') as outfile:
        json.dump(dataset2['prediction_times'], outfile )

for i in range(0, len( dataset2['prediction_times'] ) ):
    with open('../map-viewer/data/prediction_points_' + str(i) +'.json', 'w') as outfile:
        json.dump(dataset2['datasets'][i], outfile )
