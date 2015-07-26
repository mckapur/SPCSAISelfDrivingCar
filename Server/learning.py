"""
This file, written by Rohan Kapur
and Tanay Singhal, performs the
learning and persistance of the
SPCS self-driving AI car via Neural
Networks and other Machine Learning
algorithms.
"""

import os
import pickle
from pybrain.datasets            import ClassificationDataSet
from pybrain.utilities           import percentError
from pybrain.tools.shortcuts     import buildNetwork
from pybrain.supervised.trainers import BackpropTrainer
from pybrain.structure.modules   import SoftmaxLayer
import numpy as np

class NeuralNetwork:
    def __init__(self, numFeatures, numLabels):
        self.numFeatures = numFeatures
        self.numLabels = numLabels
    def train(self, X, y, iters=100000):
        ds = ClassificationDataSet(self.numFeatures, nb_classes=self.numLabels)
        for k in xrange(len(X)): 
            print y[k]
            ds.addSample(np.ravel(X[k]), y[k])
        ds.setField('input', X)
        ds.setField('target', y)
        self.net = buildNetwork(self.numFeatures, 100, self.numLabels, outclass=SoftmaxLayer, bias=True)
        trainer = BackpropTrainer(self.net, ds)
        trainer.trainUntilConvergence(verbose=True, validationProportion=0.15, maxEpochs=iters, continueEpochs=10)
        trainer.trainEpochs(iters)
    def predict(self, x):
        return self.net.activate(x)

DATA_DUMP_DIRECTORY = "data_dump"
class PersistanceManager:
    def __init__(self, namespace):
        self.namespace = namespace
    def relPathFromFilename(self, filename):
        return DATA_DUMP_DIRECTORY + "_" + filename + "_" + self.namespace
    def persistData(self, data, name):
        with open(self.relPathFromFilename(name), 'wb') as f:
            pickle.dump(data, f)
    def getPersistedData(self, name):
        pathToData = self.relPathFromFilename(name)
        if os.path.isfile(pathToData):
            with open(pathToData, 'rb') as f:
                data = pickle.load(f)
                return data
        return None

class AbstractLearningClient:
    def __init__(self, name, architecture):
        self.name = name
        self.restoreFromPersistance()
        self.initializeNeuralNetwork(architecture)
    def initializeNeuralNetwork(self, architecture):
        self.net = NeuralNetwork(architecture[0], architecture[1])
        self.configureNeuralNetwork(False)
    def restoreFromPersistance(self):
        if not hasattr(self, 'persistanceManager'):
            self.persistanceManager = PersistanceManager(self.name)
        self.net = self.persistanceManager.getPersistedData('net')
        trainingData = self.persistanceManager.getPersistedData('trainingData')
        if trainingData:
            self.X = trainingData['X']
            self.y = trainingData['y']
        else:
            self.X = []
            self.y = []
    def configureNeuralNetwork(self, shouldTrain):
        if shouldTrain:
            self.net.train(self.X, self.y)
    def streamInput(self, X, y):
        if not len(self.X):
            self.X = np.array(X)
        else:
            self.X = np.concatenate((self.X, X))
        if not len(self.y):
            self.y = np.array(y)
        else:
            self.y = np.concatenate((self.y, y))
        self.configureNeuralNetwork(True)
        self.persistanceManager.persistData({'X': self.X, 'y': self.y}, 'trainingData')
    def output(self, X):
        return self.net.predict(X)

LEARNING_HANDLER_NAME_MOTION = 'LEARNING_HANDLER_NAME_MOTION'
class MotionHandler:
    def __init__(self):
        self.learningClient = AbstractLearningClient(LEARNING_HANDLER_NAME_MOTION, [1, 3])
    def motionDataToTrainingInput(self, data):
        length = len(data)
        X = [[]] * length
        y = [[]] * length
        for i in range(length):
            X[i] = [data[i]['frontDistanceToObject']]
            y[i] = [
                data[i]['isAccelerating'],
                data[i]['isDecelerating'],
                data[i]['isBraking']
            ]
        return {'X': X, 'y': y}
    def motionDataToPredictionInput(self, data):
        return [data['frontDistanceToObject']]
    def receivedNewMotionData(self, data):
        data = self.motionDataToTrainingInput(data)
        self.learningClient.streamInput(data['X'], data['y'])
    def suggestedMotionResponseFromData(self, data):
        output = self.learningClient.output(self.motionDataToPredictionInput(data))
        response = {}
        for i in range(len(output)):
            if i == 0:
                responseType = 'shouldAccelerate'
            elif i == 1:
                responseType = 'shouldDecelerate'
            elif i == 2:
                responseType = 'shouldBrake'
            if np.amax(output) == output[i]:
                response[responseType] = 1
            else:
                response[responseType] = 0
        return response
    # def reinforceMotionData(self, data):
    # def penalizeMotionData(self, data):
