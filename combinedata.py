# -*- coding: utf8 -*-
import stations
import lam
import numpy as np
import pandas as pd
import datetime
from weatherloader import WeatherLoader
import time 


def getWeatherDataFrames(startDate, weeks, fmisids):
	params = ["t2m", "ws_10min", "wg_10min", "wd_10min", "rh", "td", "r_1h", "ri_10min", "snow_aws", "vis", "n_man"]


	dataFrames = {}

	startTime = time.time()


	for i in fmisids:

	        loader = WeatherLoader(params, startDate, weeks, [0, 0], i)

                weather = loader.getWeatherData()

		dataFrames[i] = weather


	print("loading weather took %f s" % (time.time() - startTime))
	return dataFrames



def addSpeedingInfo(data):

	

	maxSpeed = 200

        speeding = np.zeros((data.shape[0]))

	limit = data['speed_limit'].values

        for i in range(maxSpeed):
		v = i + 1

		count = data['velocity%d' % v].values

                speeding += count * (v > limit)


	data['speeding'] = speeding






def getCombinedData(startDate, weeks):


        names, stationCoord, fmisids = stations.getWeatherStationLocations()

        stationCoord = np.asarray(stationCoord).astype('float')

        road = stations.getTraficSensorData()

	sensorCoord = road[['longitude', 'latitude']].values

	sensorId = road['station_id'].values
	
        nearest = stations.getNearestWeatherStation(sensorCoord, stationCoord)

	uniqueNearest = np.unique(nearest)

	fmisids = np.asarray(fmisids)
	
	uniqueFmisids = fmisids[uniqueNearest]


	weather = getWeatherDataFrames(startDate, weeks, uniqueFmisids)

        data = None
        for i in range(nearest.shape[0]):

                station = nearest[i]

                coordinates = stationCoord[station, :]

                params = ["t2m", "ws_10min", "wg_10min", "wd_10min", "rh", "td", "r_1h", "ri_10min", "snow_aws", "vis", "n_man"]

		print(names[station])
		print(fmisids[station])

                w = weather[fmisids[station]]

                if w.empty:
                        print("No weather data found!")
                        continue


                traffic = lam.readData(sensorId[i], startDate, weeks * 7)

                if traffic.empty:
                        print("No traffic data found!")
                        continue

		for col in road.columns.values:

			traffic[col] = road.ix[road['station_id'] == sensorId[i], col].values[0]


		addSpeedingInfo(traffic)


                combined = w.merge(traffic, on = 'unixtime', how = 'inner')

                data = pd.concat((data, combined), axis = 0)


                

        return data



def combinePredictionPointsWithWeather():

        startDate = datetime.datetime(2018, 8, 1)
        weeks = 1

        selectTime = 1533103200
        hour = 9
        year = startDate.year
        day = startDate.toordinal() + 1 - datetime.datetime(year, 1, 1).toordinal()


        road = pd.read_csv('road_shape_prediction_points.csv')

        data = road.copy()

        data['hour'] = hour
        data['year'] = year
        data['day'] = day

        names, stationCoord, fmisids = stations.getWeatherStationLocations()

        stationCoord = np.asarray(stationCoord).astype('float')


	sensorCoord = road[['longitude', 'latitude']].values

	predictionId = road['prediction_point_id'].values
	
        nearest = stations.getNearestWeatherStation(sensorCoord, stationCoord)

	uniqueNearest = np.unique(nearest)

	fmisids = np.asarray(fmisids)
	
	uniqueFmisids = fmisids[uniqueNearest]


	weather = getWeatherDataFrames(startDate, weeks, uniqueFmisids)
        for station in uniqueNearest:
                

                params = ["t2m", "ws_10min", "wg_10min", "wd_10min", "rh", "td", "r_1h", "ri_10min", "snow_aws", "vis", "n_man"]

		print(names[station])
		print(fmisids[station])

                w = weather[fmisids[station]]

                pos = nearest == station
                selectedWeather = w[w['unixtime'] == selectTime]

                for col in selectedWeather.columns.values:

                        data.at[pos, col] = selectedWeather[col].values[0]


                data.to_csv('prediction_combined.csv', index = False)
        print(weather)


def example():
        '''
        startDate = datetime.date(2015, 1, 1)
        weeks = 2

        data = getCombinedData(startDate, weeks)

        data.to_csv('combined.csv', index = False)
	
        '''
        combinePredictionPointsWithWeather()
example()
