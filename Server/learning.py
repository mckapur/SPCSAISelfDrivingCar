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
    def __init__(self, layers, activation='sigmoid'):
        if activation == 'sigmoid':
            self.activation = sigmoid
            self.activation_prime = sigmoid_prime
        elif activation == 'tanh':
            self.activation = tanh
            self.activation_prime = tanh_prime
        self.weights = []
        for i in range(1, len(layers) - 1):
            self.weights.append(2*np.random.random((layers[i-1]+1, layers[i]+1))-1)
        self.weights.append(2*np.random.random((layers[i]+1, layers[i+1]))-1)
    def train(self, X, y, learning_rate=0.2, epochs=100000):
        ones = np.atleast_2d(np.ones(X.shape[0]))
        X = np.concatenate((ones.T, X), axis=1)
        for k in range(epochs):
            i = np.random.randint(X.shape[0])
            a = [X[i]]
            for l in range(len(self.weights)):
                    dot_value = np.dot(a[l], self.weights[l])
                    activation = self.activation(dot_value)
                    a.append(activation)
            error = y[i] - a[-1]
            deltas = [error * self.activation_prime(a[-1])]
            for l in range(len(a) - 2, 0, -1): 
                deltas.append(deltas[-1].dot(self.weights[l].T)*self.activation_prime(a[l]))
            deltas.reverse()
            for i in range(len(self.weights)):
                layer = np.atleast_2d(a[i])
                delta = np.atleast_2d(deltas[i])
                self.weights[i] += learning_rate * layer.T.dot(delta)
            if k % 10000 == 0: print 'epochs:', k
    def predict(self, x):
        a = np.concatenate((np.ones(1).T, np.array(x)), axis=1)      
        for l in range(0, len(self.weights)):
            a = self.activation(np.dot(a, self.weights[l]))
        return a

nn = NeuralNetwork([2, 2, 1])
X = np.array([
	[0, 0], 
	[0, 1], 
	[1, 0], 
	[1, 1]
])
y = np.array([[0, 0.5], [1, 0.3], [1, 0.4], [0, 0.6]])
nn.train(X, y)
for i in range(len(y)):
	print(y[i], nn.predict(X[i]))