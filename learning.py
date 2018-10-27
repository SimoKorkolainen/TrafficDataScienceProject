


import pandas as pd

import numpy as np

import matplotlib.pyplot as plot

import json


import lightgbm as lgb


from matplotlib.colors import rgb2hex







def dropColumnsFromData(data):
	'''
        for i in range(200):
                data.drop('velocity%d' % (i + 1), axis = 1, inplace = True)
        data.drop('speeding', axis = 1, inplace = True)
	'''


        
        #dropCols = ['unixtime', 'day', 'year', 'hour', 'id', 'station_id', 'latitude', 'longitude']

        dropCols = ['unixtime', 'year', 'id', 'station_id', 'n_speeding_cars', 'n_cars']

        data.drop(dropCols, axis = 1, inplace = True)



def getData():




        data = pd.read_csv('combined.csv')

        target = np.log1p(data['n_speeding_cars'].values)

 
        dropColumnsFromData(data)

        data.sort_index(axis = 1, inplace = True)

        print(data.columns)

        #data = data.values


        return data, target

def getPredictionData():

        data = pd.read_csv('prediction_combined.csv')


        dataIndex = data['prediction_point_id'].values
        date = data['date'].values
        dropCols = ['unixtime', 'year', 'prediction_point_id', 'date']

        data.drop(dropCols, axis = 1, inplace = True)

        data.sort_index(axis = 1, inplace = True)

        

        print(data.columns)
        #data = data.values

        return data, dataIndex, date


def runLightGBM(trainData, trainTarget, testData, testTarget):
    params = {
        "objective" : "regression",
        "metric" : "rmse",
        "task": "train",
        "num_leaves" :20,
        "learning_rate" : 0.2,
        "bagging_fraction" : 0.1,
        "feature_fraction" : 1,
        "bagging_freq" : 0,
        "verbosity" : -1,
	"seed" : 42
    }
    
    train = lgb.Dataset(trainData, label = trainTarget)
    valid = lgb.Dataset(testData, label = testTarget)

    evalsResult = {}
    model = lgb.train(params, train, 5000, 
                      valid_sets = [train, valid], 
                      early_stopping_rounds = 500, 
                      verbose_eval = 500, 
                      evals_result = evalsResult)
    

    return model, evalsResult


def runTraining():
        data, target = getData()
        
        models = []
        
        foldN = 5
        fold = np.random.randint(foldN, size = data.shape[0])


        pred = np.zeros((data.shape[0]))

        for i in xrange(foldN):
                trainData = data.iloc[fold != i, :]
                testData = data.iloc[fold == i, :]

                trainTarget = target[fold != i]
                testTarget = target[fold == i]

                
                model, evals_result = runLightGBM(trainData, trainTarget, testData, testTarget)

                pred[fold == i] = model.predict(testData, num_iteration = model.best_iteration)
                models.append(model)
                #print(model.feature_importance())


        print("Validation loss:%f" % np.sqrt(np.mean((pred - target) ** 2)))

        print("Ratio of explained variance (Validation):%f" % (1 - np.var(pred - target) / np.var(target)))

        '''
        plot.scatter(np.expm1(pred), np.expm1(target), alpha = 0.8, s = 1)
        plot.title('Prediction vs. target')
        
        plot.show()'''
        return models


def makePredictions(data, models):


        predicted = np.zeros((data.shape[0]))

        for m in models:





                pred = m.predict(data, num_iteration = m.best_iteration)


                predicted += pred / len(models)


        
        return predicted





def writePredictions(models):

        data, dataIndex, dates = getPredictionData()
        
        
        pred = makePredictions(data, models)

	values = pred.copy()

	values -= np.amin(values)
	values /= np.amax(values)


	colorMap = plot.get_cmap('plasma')

	predColors = colorMap(values)

	predColors = predColors[:, : 3]

	hexColors = np.apply_along_axis(rgb2hex, 1, predColors)

        jsonData = None

        with open('map-viewer/data/prediction_points.json') as f:
                jsonData = json.load(f)

        if jsonData is None:
                return


        for features in jsonData['features']:

                pointId = features['id']
		ind = dataIndex == pointId
                pointValue = pred[ind]
		pointCol = hexColors[ind]
                pointDates = dates[ind]
                features['properties']['data'] = []
                for i in range(len(pointValue)):
                        d = {}
                        d["predictionResult"] = int(np.round(np.expm1(pointValue[i])))
                        d["predictionResultColor"] = pointCol[i]
                        d["date"] = pointDates[i]

                        features['properties']['data'].append(d)


        with open('map-viewer/data/prediction_points_updated.json', 'w') as output:
            json.dump(jsonData, output)
        

models = runTraining()

writePredictions(models)
