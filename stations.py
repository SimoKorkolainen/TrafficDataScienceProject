

import urllib2
from bs4 import BeautifulSoup
import json
import matplotlib.pyplot as plot
import numpy as np

from scipy.spatial.distance import cdist

def getWeatherStationLocations():

	contents = urllib2.urlopen("https://en.ilmatieteenlaitos.fi/observation-stations")


	soup = BeautifulSoup(contents, "html.parser")

	t = soup.tbody

	stations = t.find_all("tr")

	coordinates = []
	names = []
	for s in stations:

		data = s.find_all('td')
		name = data[0].string
		longitude = data[5].string
		latitude = data[4].string
		stationTypes = data[7].contents

		
		if "Weather" in stationTypes:
			coordinates.append([longitude, latitude])
			names.append(name)
	return names, coordinates



def getSphericalCoordinates(coordinates):
	
	c = 2 * np.pi * coordinates / 360 
	x = np.cos(c[:, 1]) * np.cos(c[:, 0])

	y = np.cos(c[:, 1]) * np.sin(c[:, 0])


	z = np.sin(c[:, 1])
	return np.vstack((x, y, z)).T



def getNearestWeatherStation(coord, stationCoord):

	X = getSphericalCoordinates(coord)
	Y = getSphericalCoordinates(stationCoord)
	print(X.shape)
	print(Y.shape)
	distToStation = cdist(X, Y)
	print(distToStation.shape)
	a = np.argmin(distToStation, axis = 1)

	return a


def getTraficSensors():

        with open("tms-stations.json") as f:

                a = json.load(f)

                print(a['features'])



def getTraficSensorCoordinates():

        coordinates = []
        sensorIds = []
        with open("tms-stations.json") as f:

                a = json.load(f)

   

                for j in a['features']:
                        
                        province = j['properties']['province']

                        if province == "Uusimaa":
  
                                c = j['geometry']['coordinates']
                                

                                coordinates.append([c[0], c[1]])

                                sensorIds.append(j['id'])

        coordinates = np.asarray(coordinates)

	return coordinates



def example():
	names, stationCoord = getWeatherStationLocations()

	stationCoord = np.asarray(stationCoord).astype('float')

	sensorCoord = getTraficSensorCoordinates()

	a = getNearestWeatherStation(sensorCoord, stationCoord)
	u = np.unique(a)

	print("Nearest weather stations to the traffic sensors in Uusimaa:")
	for j in u:

		print(names[j])


	plot.scatter(sensorCoord[:, 0], sensorCoord[:, 1], alpha = 0.5)
	plot.scatter(stationCoord[u, 0], stationCoord[u, 1], c = 'red')
	plot.show()




example()
