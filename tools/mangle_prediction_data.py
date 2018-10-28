#!/usr/bin/env python3

import json
import copy

with open('../map-viewer/data/prediction_points_updated.json', 'r') as infile:
    dataset = json.load(infile)


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
                break
    dataset2['datasets'].append( temp_prediction_times )

with open('../map-viewer/data/prediction_points_updated2.json', 'w') as outfile:
    json.dump(dataset2, outfile )
