#!/usr/bin/python
# -*- coding: utf-8 -*-

import numpy as np

class KalmanFilter():
    def __init__(self, point, deltaT=0.01):
        # Initial state vector.
        self.vecS = np.array([[point[0]], [point[1]], [0], [0]]) # X, Y, VX, VY.

        # Transition matrice.
        self._matA = np.array([[1, 0, deltaT,      0],
                               [0, 1,      0, deltaT],
                               [0, 0,      1,      0],
                               [0, 0,      0,      1]])

        # Observation matrice: observe only X and Y.
        self._matH = np.array([[1, 0, 0, 0],
                               [0, 1, 0, 0]])

        # Noise: Q, R.
        self._matQ = np.array([[1, 0, 0, 0],
                               [0, 1, 0, 0],
                               [0, 0, 1, 0],
                               [0, 0, 0, 1]])
        self._matR = np.array([[1, 0],
                               [0, 1]])

        # Covariance.
        self._matP = np.eye(self._matA.shape[1])

    def prediction(self):
        # Dynamics.
        self.vecS = np.dot(self._matA, self.vecS)
        # Error covariance.
        self._matP = np.dot(self._matA, np.dot(self._matP, self._matA.T)) + self._matQ

    def update(self, vecZ):
        # Kalman gain.
        matS = np.dot(self._matH, np.dot(self._matP, self._matH.T)) + self._matR
        matK = np.dot(self._matP, np.dot(self._matH.T, np.linalg.inv(matS)))

        # Correction / innovation.
        vecI = vecZ - np.dot(self._matH, self.vecS)
        self.vecS = np.round(self.vecS+np.dot(matK, vecI))
        matI = np.eye(self.vecS.shape[0])
        self._matP = (matI-np.dot(matK, self._matH))*self._matP
