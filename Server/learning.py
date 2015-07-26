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
import numpy as np

def sigmoid(x):
    return 1.0/(1.0 + np.exp(-x))
def dsigmoid(x):
    return x*(1.0-x)

def tanh(x):
    return np.tanh(x)
def dtanh(x):
    return 1.0 - x**2

class NeuralNetwork:
    def __init__(self, layers, weights=[], activation='sigmoid'):
        if activation == 'sigmoid':
            self.activation = sigmoid
            self.dactivation = dsigmoid
        elif activation == 'tanh':
            self.activation = tanh
            self.dactivation = dtanh
        self.weights = weights
        if (len(self.weights) != layers[0]):
            for i in range(1, len(layers) - 1):
                self.weights.append(2 * np.random.random((layers[i-1] + 1, layers[i] + 1)) - 1)
            self.weights.append(2 * np.random.random((layers[i] + 1, layers[i+1])) - 1)
    def train(self, X, y, learning_rate=0.2, iters=100000):
        ones = np.atleast_2d(np.ones(X.shape[0]))
        X = np.concatenate((ones.T, X), axis=1)
        for k in range(iters):
            i = np.random.randint(X.shape[0])
            a = [X[i]]
            for l in range(len(self.weights)):
                dot_value = np.dot(a[l], self.weights[l])
                activation = self.activation(dot_value)
                a.append(activation)
            error = y[i] - a[-1]
            deltas = [error * self.dactivation(a[-1])]
            for l in range(len(a) - 2, 0, -1): 
                deltas.append(deltas[-1].dot(self.weights[l].T) * self.dactivation(a[l]))
            deltas.reverse()
            for i in range(len(self.weights)):
                layer = np.atleast_2d(a[i])
                delta = np.atleast_2d(deltas[i])
                self.weights[i] += learning_rate * layer.T.dot(delta)
            if k % 10000 == 0:
                print 'iters:', k
    def predict(self, x):
        a = np.concatenate((np.ones(1).T, np.array(x)), axis=1)      
        for l in range(0, len(self.weights)):
            a = self.activation(np.dot(a, self.weights[l]))
        return a

DATA_DUMP_DIRECTORY = "data_dump"
INPUT_X_DUMP_FILENAME = "input_X"
INPUT_y_DUMP_FILENAME = "input_y"
WEIGHTS_DUMP_FILENAME = "weights"
NPY_EXTENSION = '.npy'
class PersistanceManager:
    def __init__(self, namespace):
        self.namespace = namespace
    def relPathFromFilename(self, filename, extension):
        return DATA_DUMP_DIRECTORY + "_" + filename + "_" + self.namespace + extension
    def persistData(self, X=np.array([]), y=np.array([]), weights=[]):
        np.save(self.relPathFromFilename(INPUT_X_DUMP_FILENAME, NPY_EXTENSION), X)
        np.save(self.relPathFromFilename(INPUT_y_DUMP_FILENAME, NPY_EXTENSION), y)
        with open(self.relPathFromFilename(WEIGHTS_DUMP_FILENAME, ''), 'wb') as f:
            pickle.dump(weights, f)
    def getPersistedData(self):
        X = np.array([])
        y = np.array([])
        weights = []
        pathToX = self.relPathFromFilename(INPUT_X_DUMP_FILENAME, NPY_EXTENSION)
        pathToY = self.relPathFromFilename(INPUT_y_DUMP_FILENAME, NPY_EXTENSION)
        pathToWeights = self.relPathFromFilename(WEIGHTS_DUMP_FILENAME, '')
        if os.path.isfile(pathToX):
            X = np.load(pathToX)
        if os.path.isfile(pathToY):
            y = np.load(pathToY)
        if os.path.isfile(pathToWeights):
            with open(pathToWeights, 'rb') as f:
                weights = pickle.load(f)
        return {'X': X, 'y': y, 'weights': weights}
    def wipePersistedData(self):
        self.persistData()

class AbstractLearningClient:
    def __init__(self, name, architecture):
        self.name = name
        self.restoreFromPersistance()
        self.initializeNeuralNetwork(architecture)
    def initializeNeuralNetwork(self, architecture):
        self.net = NeuralNetwork(architecture)
        self.configureNeuralNetwork(False)
    def restoreFromPersistance(self):
        print "called?"
        if not hasattr(self, 'persistanceManager'):
            self.persistanceManager = PersistanceManager(self.name)
        data = self.persistanceManager.getPersistedData()
        self.X = data['X']
        self.y = data['y']
        self.weights = data['weights']
    def configureNeuralNetwork(self, shouldTrain):
        if shouldTrain:
            self.net.train(self.X, self.y)
        elif len(self.weights):
            self.net.weights = self.weights
        self.weights = self.net.weights
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
        self.persistanceManager.persistData(self.X, self.y, self.weights)
    def output(self, X):
        return self.net.predict(X)
    def wipe(self):
        self.persistanceManager.wipePersistedData()
        self.restoreFromPersistance()
        return True

LEARNING_HANDLER_NAME_MOTION = 'LEARNING_HANDLER_NAME_MOTION'
class MotionHandler:
    def __init__(self):
        self.learningClient = AbstractLearningClient(LEARNING_HANDLER_NAME_MOTION, [1, 1, 3])
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
    def wipe(self):
        return self.learningClient.wipe()