"""
This file, written by Rohan Kapur
and Tanay Singhal, performs the
learning and persistance of the
SPCS self-driving AI car via Neural
Networks and other Machine Learning
algorithms.
"""

import numpy as np

def sigmoid(x):
    return 1.0/(1.0 + np.exp(-x))

def sigmoid_prime(x):
    return x*(1.0-x)

def tanh(x):
    return np.tanh(x)

def tanh_prime(x):
    return 1.0 - x**2

class NeuralNetwork:
    def __init__(self, layers, weights=[], activation='sigmoid'):
        if activation == 'sigmoid':
            self.activation = sigmoid
            self.activation_prime = sigmoid_prime
        elif activation == 'tanh':
            self.activation = tanh
            self.activation_prime = tanh_prime
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
            deltas = [error * self.activation_prime(a[-1])]
            for l in range(len(a) - 2, 0, -1): 
                deltas.append(deltas[-1].dot(self.weights[l].T) * self.activation_prime(a[l]))
            deltas.reverse()
            for i in range(len(self.weights)):
                layer = np.atleast_2d(a[i])
                delta = np.atleast_2d(deltas[i])
                self.weights[i] += learning_rate * layer.T.dot(delta)
            if k % 10000 == 0: print 'iters:', k
    def predict(self, x):
        a = np.concatenate((np.ones(1).T, np.array(x)), axis=1)      
        for l in range(0, len(self.weights)):
            a = self.activation(np.dot(a, self.weights[l]))
        return a

DATA_DUMP_DIRECTORY = "data_dump"
INPUT_X_DUMP_FILENAME = "_input_X_"
INPUT_y_DUMP_FILENAME = "_input_y_"
WEIGHTS_DUMP_FILENAME = "_weights_"
DATA_DUMP_SUFFIX = "dump.npy"

class PersistanceManager:
    def __init__(namespace):
        self.namespace = namespace
    def relPathFromFilename(self, filename):
        return DATA_DUMP_DIRECTORY + filename + self.namespace + DATA_DUMP_SUFFIX
    def persistData(X=[], y=[], weights=[]):
        np.save(self.relPathFromFilename(INPUT_X_DUMP_FILENAME), X)
        np.save(self.relPathFromFilename(INPUT_y_DUMP_FILENAME), y)
        np.save(self.relPathFromFilename(WEIGHTS_DUMP_FILENAME), weights)
    def getPersistedData(self):
        X = np.load(self.relPathFromFilename(INPUT_X_DUMP_FILENAME))
        y = np.load(self.relPathFromFilename(INPUT_y_DUMP_FILENAME))
        weights = np.load(self.relPathFromFilename(WEIGHTS_DUMP_FILENAME))
        return {'X': X, 'y': y, 'weights': weights}
    def wipePersistedData(self):
        self.persistData()

class AbstractLearningClient:
    def __init__(self, name):
        self.persistanceManager = PersistanceManager(name)
        data = self.persistanceManager.getPersistedData()
        self.X = data['X']
        self.y = data['y']
        self.weights = data['weights']
        self.configureNeuralNetwork(False)
    def configureNeuralNetwork(self, shouldTrain):
        inputColumnSize = self.X.shape[1]
        hiddenColumnSize = inputColumnSize
        outputColumnSize = self.y.shape[1]
        self.net = NeuralNetwork([inputColumnSize, hiddenColumnSize, outputColumnSize])
        if shouldTrain:
            self.net.train(self.X, self.y)
        else:
            self.net.weights = self.weights
        self.weights = self.net.weights
    def streamInput(self, X, y):
        self.X = np.append(self.X, X)
        self.y = np.append(self.y, y)
    def endInputStream(self):
        self.configureNeuralNetwork(True)
        self.persistanceManager.persistData(self.X, self.y, self.weights)
    def output(X):
        self.net.predict(X)
    def wipe(self):
        self.wipePersistedData
        return True

MOTION_HANDLER_NAME = 'MOTION_HANDLER'

class MotionHandler:
    def __init__(self):
        self.learningClient = AbstractLearningClient(MOTION_HANDLER_NAME)
    def receivedNewMotionData(self, data):
    def endedReceivingMotionData(self):
    def suggestedMotionResponseFromData(data):
    def delete:
        return self.learningClient.wipe()
