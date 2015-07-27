"""
This file, written by Rohan Kapur
and Tanay Singhal, performs the
learning and persistance of the
SPCS self-driving AI car using Neural
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
    def train(self, X, y):
        ds = ClassificationDataSet(self.numFeatures, nb_classes=self.numLabels)
        ds.setField('input', X)
        ds.setField('target', y)
        self.net = buildNetwork(self.numFeatures, 100, self.numLabels, outclass=SoftmaxLayer, bias=True)
        trainer = BackpropTrainer(self.net, ds)
        print 'Training now....'
        trainer.trainUntilConvergence(validationProportion=0.1)
        print 'Done training'
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

TRAINING_DATA_DUMP_NAME = "training_data"
NEURAL_NET_DUMP_NAME = "neural_net"
class AbstractLearningClient:
    def __init__(self, name, architecture):
        self.name = name
        self.restoreFromPersistance()
        self.initializeNeuralNetwork(architecture)
    def initializeNeuralNetwork(self, architecture):
        if not self.net:
            self.net = NeuralNetwork(architecture['inputWidth'], architecture['outputLength'])
        self.configureNeuralNetwork(False)
    def restoreFromPersistance(self):
        if not hasattr(self, 'persistanceManager'):
            self.persistanceManager = PersistanceManager(self.name)
        self.net = self.persistanceManager.getPersistedData(NEURAL_NET_DUMP_NAME)
        trainingData = self.persistanceManager.getPersistedData(TRAINING_DATA_DUMP_NAME)
        if trainingData:
            self.X = trainingData['X']
            self.y = trainingData['y']
        else:
            self.X = []
            self.y = []
    def configureNeuralNetwork(self, shouldTrain):
        if shouldTrain:
            self.net.train(self.X, self.y)
            self.persistanceManager.persistData(self.net, NEURAL_NET_DUMP_NAME)
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
        self.persistanceManager.persistData({'X': self.X, 'y': self.y}, TRAINING_DATA_DUMP_NAME)
    def output(self, x):
        return self.net.predict(x)

LEARNING_HANDLER_NAME_MOTION = 'LEARNING_HANDLER_NAME_MOTION'
class MotionHandler:
    def __init__(self):
        self.learningClient = AbstractLearningClient(LEARNING_HANDLER_NAME_MOTION, {'inputWidth': 2, 'outputLength': 2})
    def motionDataToTrainingInput(self, data):
        length = len(data)
        X = [[]] * length
        y = [[]] * length
        for i in range(length):
            X[i] = self.motionDataToPredictionInput(data[i])
            y[i] = [
                data[i]['isAccelerating'],
                data[i]['isBraking']
            ]
        return {'X': X, 'y': y}
    def motionDataToPredictionInput(self, data):
        return [data['scaledForward'], data['scaledLeftRightRatio']]
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
                responseType = 'shouldBrake'
            if np.amax(output) == output[i]:
                response[responseType] = 1
            else:
                response[responseType] = 0
        return response
    # def reinforceMotionData(self, data):
    # def penalizeMotionData(self, data):

LEARNING_HANDLER_NAME_STEERING = 'LEARNING_HANDLER_NAME_STEERING'
class SteeringHandler:
    def __init__(self):
        self.learningClient = AbstractLearningClient(LEARNING_HANDLER_NAME_STEERING, {'inputWidth': 2, 'outputLength': 3})
    def steeringDataToTrainingInput(self, data):
        length = len(data)
        X = [[]] * length
        y = [[]] * length
        for i in range(length):
            X[i] = self.steeringDataToPredictionInput(data[i])
            y[i] = [
                data[i]['isTurningLeft'],
                data[i]['isTurningRight'],
                data[i]['isKeepingStraight']
            ]
        return {'X': X, 'y': y}
    def steeringDataToPredictionInput(self, data):
        return [data['scaledForward'], data['scaledLeftRightRatio']]
    def receivedNewSteeringData(self, data):
        data = self.steeringDataToTrainingInput(data)
        self.learningClient.streamInput(data['X'], data['y'])
    def suggestedSteeringResponseFromData(self, data):
        output = self.learningClient.output(self.steeringDataToPredictionInput(data))
        response = {}
        for i in range(len(output)):
            if i == 0:
                responseType = 'shouldTurnLeft'
            elif i == 1:
                responseType = 'shouldTurnRight'
            elif i == 2:
                responseType = 'shouldKeepStraight'
            if np.amax(output) == output[i]:
                response[responseType] = 1
            else:
                response[responseType] = 0
        return response
    # def reinforceSteeringData(self, data):
    # def penalizeSteeringData(self, data):
