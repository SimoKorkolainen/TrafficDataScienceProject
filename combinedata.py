# -*- coding: utf8 -*-
import stations
import lam
import numpy as np
import pandas as pd
import datetime
from weatherloader import WeatherLoader
import time 
import pytz

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



def unixTimeToFinnishDateTime(unixTime):

	date = datetime.datetime.fromtimestamp(unixTime)

        finlandTime = pytz.timezone('Europe/Helsinki')

        date = finlandTime.localize(date)  

	return date

def getCombinedData(startDate, weeks):


        names, stationCoord, fmisids = stations.getWeatherStationLocations()

        stationCoord = np.asarray(stationCoord).astype('float')

        road = stations.getTraficSensorData()

	sensorCoord = road[['longitude', 'latitude']].values

	sensorId = road['station_id'].values
	speedLimits = road['speed_limit'].values
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


                traffic = lam.readData(sensorId[i], startDate, weeks * 7, speedLimits[i])

                if traffic.empty:
                        print("No traffic data found!")
                        continue

		for col in road.columns.values:

			traffic[col] = road.ix[road['station_id'] == sensorId[i], col].values[0]


		#addSpeedingInfo(traffic)


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


def combinePredictionPointsWithWeather2():

        startDate = datetime.datetime(2018, 10, 22)
        weeks = 1



        road = pd.read_csv('road_shape_prediction_points.csv')

        names, stationCoord, fmisids = stations.getWeatherStationLocations()

        stationCoord = np.asarray(stationCoord).astype('float')

        road = road.iloc[: 100, :]

	stationCoord = stationCoord[: 6, :]

	sensorCoord = road[['longitude', 'latitude']].values

	predictionId = road['prediction_point_id'].values
	
        nearest = stations.getNearestWeatherStation(sensorCoord, stationCoord)
        
	uniqueNearest = np.unique(nearest)

	fmisids = np.asarray(fmisids)
	
	uniqueFmisids = fmisids[uniqueNearest]
	
	print(nearest.shape)
	weather = getWeatherDataFrames(startDate, weeks, uniqueFmisids)

	data = None

	for i in range(nearest.shape[0]):
                if i % 20 == 0:
                        print(float(i) / nearest.shape[0])
		station = nearest[i]


		pointData = weather[fmisids[station]].copy()



	        unixTime = pointData['unixtime'].values

                dayN = np.zeros((unixTime.shape[0]), dtype = 'int')
                hour = np.zeros((unixTime.shape[0]), dtype = 'int')
                year = np.zeros((unixTime.shape[0]), dtype = 'int')
                dateString = np.full((unixTime.shape[0]), "", dtype = 'object')

                for j in range(unixTime.shape[0]):

                        obsDate = unixTimeToFinnishDateTime(unixTime[j])

                        year[j] = obsDate.year
                        dayN[j] = obsDate.toordinal() - datetime.datetime(year[j], 1, 1).toordinal() + 1
                        hour[j] = obsDate.hour
		        timeFormat = "%Y-%m-%d %H:%M:%S %Z%z"
                        s = obsDate.strftime(timeFormat)

                        dateString[j] = obsDate.strftime(timeFormat)

                
                pointData['year'] = year
                pointData['hour'] = hour
                pointData['date'] = dateString
                pointData['day'] = dayN
		for col in road.columns.values:

			pointData[col] = road.ix[i, col]

		#print(pointData.columns.values)
		
		data = pd.concat((data, pointData), axis = 0)

        data.to_csv('prediction_combined.csv', index = False)

	'''
	for u in unixTime:
		d = unixTimeToFinnishDateTime(u)
		dayFormat = "%Y-%m-%d"
		timeFormat = "%H:%M:%S %Z%z"
		print(d.strftime(dayFormat))
		print(d.strftime(timeFormat))'''



	'''
	for i in weather.keys():

		print(weather[i].head(20))'''


	'''
        selectTime = 1533103200
        hour = 9
        year = startDate.year
        day = startDate.toordinal() + 1 - datetime.datetime(year, 1, 1).toordinal()


        data = road.copy()

        data['hour'] = hour
        data['year'] = year
        data['day'] = day


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
        print(weather)'''


def example():


       	'''
        startDate = datetime.date(2015, 1, 1)
        weeks = 50
        data = getCombinedData(startDate, weeks)

        data.to_csv('combined.csv', index = False)
	'''
        
        combinePredictionPointsWithWeather2()
example()
