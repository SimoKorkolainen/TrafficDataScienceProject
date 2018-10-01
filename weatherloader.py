

import urllib2
import pandas as pd
import numpy as np
import datetime
import time
import re
import matplotlib.pyplot as plot

from pandas.compat import StringIO
from xml.etree import ElementTree


class WeatherLoader:




        
        def __init__(self, params, startDay, weeks, coordinates):
                self.parameters = params
                self.startDay = startDay
                self.weeks = weeks
                self.coordinates = coordinates


        def readData(self, element, colNames):

	        info = element.text
	

	        info = re.sub(" +", " ", info)
	        info = info.replace(" \n", "\n")
         	info = info.rstrip()

                data = pd.read_csv(StringIO(info), sep = " ", skipinitialspace = True, header = None, names = colNames)

	        return data

        def readWeatherData(self, treeRoot):

	        tupleList = treeRoot.find(".//{http://www.opengis.net/gml/3.2}doubleOrNilReasonTupleList")

	        return self.readData(tupleList, self.parameters)

        def readPositionData(self, treeRoot):
	        pos = treeRoot.find(".//{http://www.opengis.net/gmlcov/1.0}positions")

	        return self.readData(pos, ["latitude", "longitude", "unixtime"])


        def getDataFromTree(self, wfsTree):

                treeRoot = wfsTree.getroot()
	
         	pos = self.readPositionData(treeRoot)

	        weather = self.readWeatherData(treeRoot)


	        data = pd.concat((weather, pos), axis = 1)
           

                return data




        def createQuery(self, firstDay, days):


	        c = ",".join(self.coordinates * 2)

	        bbox = "bbox=%s" % c
	       

                apiKey = "4ae5f71b-196f-4dc0-b730-05259ab23c23"

                endDay = self.getDateAfterDays(firstDay, days)

            
                startTime = "starttime=%sT00:00:00Z" % firstDay.isoformat()
                endTime = "endtime=%sT00:00:00Z" % endDay.isoformat()

         
         
                parameters = "parameters=%s" % ",".join(self.parameters)
         
                queryId ="storedquery_id=fmi::observations::weather::multipointcoverage"

                timeStep = "timestep=60"

                address = "http://data.fmi.fi/fmi-apikey/%s/wfs?request=getFeature" % apiKey

               

                query = "&".join((address, queryId, parameters, timeStep, startTime, endTime, bbox))


                return query

        def requestWFS(self, query):

                       
                contents = urllib2.urlopen(query)


                tree = ElementTree.parse(contents)


                return self.getDataFromTree(tree)


                 

        def getDateAfterDays(self, date, days):

                

                return datetime.date.fromordinal(date.toordinal() + days)




        def getWeatherData(self):



                data = None
                dayStep = 7 ## maximum allowed number of days per request
                for i in range(self.weeks):
                        
                        startTime = time.time()
                        atDay = self.getDateAfterDays(self.startDay, i * dayStep)

                        query = self.createQuery(atDay, dayStep)


                        subData = self.requestWFS(query)

                   
		        data = pd.concat((data, subData), axis = 0)

		
                        print("Loading week %d took %f seconds." % (i, time.time() - startTime))




	        return data


        def saveData(self, data):
	        data.to_csv("weather_data_%s_%s.csv" % (self.coordinates[0].replace(".", "-"), self.coordinates[1].replace(".", "-")))









def plotData(data):
        D = data.shape[1]

        for i in range(D):
                

                plot.subplot(D, 1, i + 1)
                plot.plot(data.values[:, i])
	        plot.title(data.columns[i])
        plot.show()








def example():






        #coordinates = ["25.67087", "62.39758"]
        coordinates = ["24.94459", "60.17523"] # [longitude, latitude]

        params = ["t2m", "ws_10min", "wg_10min", "wd_10min", "rh", "td", "r_1h", "ri_10min", "snow_aws", "vis", "n_man"]

        startDay = datetime.date(2016, 1, 1)

        weeks = 20

        loader = WeatherLoader(params, startDay, weeks, coordinates)

        data = loader.getWeatherData()

        print(data.head())


        loader.saveData(data)

        plotData(data)









example()

