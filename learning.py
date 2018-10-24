


import pandas as pd

import numpy as np

import matplotlib.pyplot as plot

import json


import lightgbm as lgb










def dropColumnsFromData(data, dropSpaceTime):
        for i in range(200):
                data.drop('velocity%d' % (i + 1), axis = 1, inplace = True)
        data.drop('speeding', axis = 1, inplace = True)

        if dropSpaceTime:
                dropCols = ['unixtime', 'day', 'year', 'hour', 'id', 'station_id', 'latitude', 'longitude']

                data.drop(dropCols, axis = 1, inplace = True)


def getData():




        data = pd.read_csv('combined.csv')

        target = np.log1p(data['speeding'].values)

 
        dropColumnsFromData(data, True)

        data.sort_index(axis = 1, inplace = True)

        print(data.columns)

        data = data.values


        return data, target

def getPredictionData():

        data = pd.read_csv('prediction_combined.csv')

        dataIndex = data['prediction_point_id'].values

        dropCols = ['unixtime', 'day', 'year', 'hour', 'prediction_point_id', 'latitude', 'longitude']

        data.drop(dropCols, axis = 1, inplace = True)

        data.sort_index(axis = 1, inplace = True)

        print(data.columns)
        data = data.values

        return data, dataIndex


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
                trainData = data[fold != i, :]
                testData = data[fold == i, :]

                trainTarget = target[fold != i]
                testTarget = target[fold == i]

                
                model, evals_result = runLightGBM(trainData, trainTarget, testData, testTarget)

                pred[fold == i] = model.predict(testData, num_iteration = model.best_iteration)
                models.append(model)
                #print(model.feature_importance())


        print("Validation loss:%f" % np.sqrt(np.mean((pred - target) ** 2)))

        print("Ratio of explained variance (Validation):%f" % (1 - np.var(pred - target) / np.var(target)))

        plot.scatter(pred, target, alpha = 0.2)
        plot.title('Prediction vs. target')
        
        plot.show()
        return models


def makePredictions(data, models):


        predicted = np.zeros((data.shape[0]))

        for m in models:





                pred = m.predict(data, num_iteration = m.best_iteration)


                predicted += pred / len(models)


        
        return predicted


def writePredictions(models):

        data, dataIndex = getPredictionData()
        
        
        pred = makePredictions(data, models)

        jsonData = None

        with open('map-viewer/data/prediction_points.json') as f:
                jsonData = json.load(f)

        if jsonData is None:
                return


        for features in jsonData['features']:

                pointId = features['id']

                value = pred[dataIndex == pointId][0]

                features['properties']['predictionResultLog1p'] = value

                features['properties']['predictionResult'] = np.expm1(value)

        with open('map-viewer/data/prediction_points_updated.json', 'w') as output:
            json.dump(jsonData, output)


        

models = runTraining()

writePredictions(models)
