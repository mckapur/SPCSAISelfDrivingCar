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
from pybrain.structure.modules   import SigmoidLayer
from pybrain.structure.modules   import SoftmaxLayer
from pybrain.tools.shortcuts import buildNetwork
from pybrain.tools.customxml.networkwriter import NetworkWriter
from pybrain.tools.customxml.networkreader import NetworkReader
import numpy as np
import datetime

class NeuralNetwork:
    def __init__(self, numFeatures, numLabels):
        self.numFeatures = numFeatures
        self.numLabels = numLabels
    def train(self, X, y):
        ds = ClassificationDataSet(self.numFeatures, self.numLabels, nb_classes=self.numLabels)
        ds.setField('input', X)
        ds.setField('target', y)
        self.net = buildNetwork(self.numFeatures, len(y), self.numLabels, outclass=SigmoidLayer, bias=True)
        print X
        print y
        trainer = BackpropTrainer(self.net, ds, learningrate=0.12)
        print 'Training now.... on ' + str(len(y)) + ' training examples'
        startDate = datetime.datetime.now()
        trainer.trainUntilConvergence(verbose=True, validationProportion=0.05)
        datetime.timedelta(0, 8, 562000)
        dateDiff = datetime.datetime.now() - startDate
        timeDiff = divmod(dateDiff.days*86400 + dateDiff.seconds, 60)
        print 'DONE TRAINING. TOOK %s min %s sec\r' % (timeDiff[0], timeDiff[1])
        print '=======================================================================================\r'
    def predict(self, x):
        if hasattr(self, 'net'):
            return self.net.activate(x)

DATA_DUMP_DIRECTORY = "data_dump"
DATA_DUMP_NN_EXT = "_PYBRAIN"
class PersistanceManager:
    def __init__(self, namespace):
        self.namespace = namespace
    def relPathFromFilename(self, filename):
        return DATA_DUMP_DIRECTORY + "_" + filename + "_" + self.namespace
    def persistData(self, data, name):
        with open(self.relPathFromFilename(name), 'wb') as f:
            pickle.dump(data, f)
        if name == NEURAL_NET_DUMP_NAME:
            NetworkWriter.writeToFile(data.net, self.relPathFromFilename(name + DATA_DUMP_NN_EXT))            
    def getPersistedData(self, name):
        pathToData = self.relPathFromFilename(name)
        if os.path.isfile(pathToData):
            with open(pathToData, 'rb') as f:
                data = pickle.load(f)
            if name == NEURAL_NET_DUMP_NAME:
                data.net = NetworkReader.readFrom(self.relPathFromFilename(name + DATA_DUMP_NN_EXT))
            return data

TRAINING_DATA_DUMP_NAME = "training_data"
NEURAL_NET_DUMP_NAME = "neural_net"
class AbstractLearningClient:
    def __init__(self, name, architecture):
        self.name = name
        self.restoreFromPersistance()
        self.initializeNeuralNetwork(architecture)
    def initializeNeuralNetwork(self, architecture):
        if not hasattr(self, 'net'):
            self.net = NeuralNetwork(architecture['inputWidth'], architecture['outputLength'])
        self.configureNeuralNetwork(False)
    def restoreFromPersistance(self):
        if not hasattr(self, 'persistanceManager'):
            self.persistanceManager = PersistanceManager(self.name)
        net = self.persistanceManager.getPersistedData(NEURAL_NET_DUMP_NAME)
        if net:
            self.net = net
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
        self.persistanceManager.persistData({'X': self.X, 'y': self.y}, TRAINING_DATA_DUMP_NAME)
        self.configureNeuralNetwork(True)
    def output(self, x):
        return self.net.predict(x)

LEARNING_HANDLER_NAME_MOTION = 'LEARNING_HANDLER_NAME_MOTION'
class MotionHandler:
    def __init__(self):
        self.learningClient = AbstractLearningClient(LEARNING_HANDLER_NAME_MOTION, {'inputWidth': 3, 'outputLength': 1})
        if hasattr(self.learningClient.net, 'net'):
            self.printAccuracy()
        self.learningClient.configureNeuralNetwork(True)
    def printAccuracy(self):
        errorHits = 0.0
        if len(self.learningClient.y):
            for i in range(len(self.learningClient.y)):
                if not np.around(self.learningClient.output(self.learningClient.X[i])[0]) == np.around(self.learningClient.y[i][0]):
                    errorHits += 1
            if len(self.learningClient.y):
                percentageErr = errorHits/len(self.learningClient.y)*100
                print "Motion error: " + str(percentageErr) + "%"
    def motionDataToTrainingInput(self, data):
        length = len(data)
        X = [[]] * length
        y = [[]] * length
        for i in range(length):
            X[i] = self.motionDataToPredictionInput(data[i])
            y[i] = [
                data[i]['isAccelerating']
            ]
        return {'X': X, 'y': y}
    def motionDataToPredictionInput(self, data):
        return [data['scaledForward'], data['scaledLeftRightRatio'], data['scaledSpeed']]
    def receivedNewMotionData(self, data):
        data = self.motionDataToTrainingInput(data)
        self.learningClient.streamInput(data['X'], data['y'])
    def suggestedMotionResponseFromData(self, data):
        output = self.learningClient.output(self.motionDataToPredictionInput(data))
        response = {'shouldAccelerate': np.around(output[0])}
        return response
    # def reinforceMotionData(self, data):
    # def penalizeMotionData(self, data):

LEARNING_HANDLER_NAME_STEERING = 'LEARNING_HANDLER_NAME_STEERING'
class SteeringHandler:
    def __init__(self):
        self.learningClient = AbstractLearningClient(LEARNING_HANDLER_NAME_STEERING, {'inputWidth': 3, 'outputLength': 3})
        if hasattr(self.learningClient.net, 'net'):
            self.printAccuracy()
        self.learningClient.configureNeuralNetwork(True)
    def printAccuracy(self):
        errorHits = 0.0
        if len(self.learningClient.y):
            for i in range(len(self.learningClient.y)):
                if not np.argmax(self.learningClient.output(self.learningClient.X[i])) == np.argmax(self.learningClient.y[i]):
                    errorHits += 1
            if len(self.learningClient.y):
                percentageErr = errorHits/len(self.learningClient.y)*100
                print "Steering error: " + str(percentageErr) + "%"
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
        return [data['scaledForward'], data['scaledLeftRightRatio'], data['scaledSpeed']]
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
            if np.argmax(output) == i:
                response[responseType] = 1
            else:
                response[responseType] = 0
        return response
    # def reinforceSteeringData(self, data):
    # def penalizeSteeringData(self, data):