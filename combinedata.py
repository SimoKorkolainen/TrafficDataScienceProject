
import stations
import lam
import numpy as np
import pandas as pd
import datetime
from weatherloader import WeatherLoader




def getCombinedData(startDate, weeks):


        names, stationCoord = stations.getWeatherStationLocations()

        stationCoord = np.asarray(stationCoord).astype('float')

        sensorId, sensorCoord = stations.getTraficSensorCoordinates()



        nearest = stations.getNearestWeatherStation(sensorCoord, stationCoord)

        data = None
        for i in range(nearest.shape[0]):
                station = nearest[i]

                coordinates = stationCoord[station, :]

                params = ["t2m", "ws_10min", "wg_10min", "wd_10min", "rh", "td", "r_1h", "ri_10min", "snow_aws", "vis", "n_man"]


                loader = WeatherLoader(params, startDate, weeks, coordinates)

                weather = loader.getWeatherData()

                if weather.empty:
                        print("No weather data found!")
                        continue


                traffic = lam.readData(sensorId[i], startDate, weeks * 7)

                if traffic.empty:
                        print("No traffic data found!")
                        continue

                combined = weather.merge(traffic, on = 'unixtime', how = 'inner')

                data = pd.concat((data, combined), axis = 0)

        return data


def example():

        startDate = datetime.date(2016, 1, 1)
        weeks = 5

        data = getCombinedData(startDate, weeks)

        data.to_csv('combined.csv', index = False)



example()
