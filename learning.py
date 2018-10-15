


import pandas as pd

import numpy as np

import matplotlib.pyplot as plot



import lightgbm as lgb








def getTarget(data):

        N = data.shape[0]
        S = np.zeros((N))
        A = np.zeros((N))


        for i in range(90):


                S += data['velocity%d' % (i + 111)].values
        for i in range(200):


                A += data['velocity%d' % (i + 1)].values

        

        target = S / (A + 0.1)

        return target


def dropColumnsFromData(data, dropSpaceTime):
        for i in range(200):
                data.drop('velocity%d' % (i + 1), axis = 1, inplace = True)

        if dropSpaceTime:
                dropCols = ['unixtime', 'day', 'year', 'hour', 'id', 'latitude', 'longitude']

                data.drop(dropCols, axis = 1, inplace = True)


def getData():




        data = pd.read_csv('combined.csv')

        target = getTarget(data)

        dropColumnsFromData(data, True)

        data = data.values

        return data, target




def runLightGBM(trainData, trainTarget, testData, testTarget):
    params = {
        "objective" : "regression",
        "metric" : "rmse",
        "task": "train",
        "num_leaves" :20,
        "learning_rate" : 0.005,
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
                
                #print(model.feature_importance())


        print("Validation loss:%f" % np.sqrt(np.mean((pred - target) ** 2)))

        print("Ratio of explained variance (Validation):%f" % (1 - np.var(pred - target) / np.var(target)))

        plot.scatter(pred, target, alpha = 0.2)
        plot.title('Prediction vs. target')
        
        plot.show()


runTraining()
