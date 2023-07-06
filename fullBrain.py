from keras.models import Sequential
from keras.layers import *
from keras.optimizers import *
from keras.layers import Dense, Flatten, LeakyReLU, Input, concatenate, Reshape, Lambda, BatchNormalization, Dropout
from keras import regularizers
from keras.models import Model
from keras import backend as K


class FullDqnBrain:
    def __init__(self, stateCount, actionCount):
        self.stateCount = stateCount
        self.actionCount = actionCount

        self.model = self.buildModel()

    def buildModel(self):
        model = Sequential()

        model.add(Dense(256, activation='relu', input_dim=self.stateCount))
        model.add(Dense(128, activation='relu'))
        model.add(Dense(self.actionCount, activation='linear'))

        opt = RMSprop(learning_rate=0.000001)
        model.compile(loss='mse', optimizer=opt)

        return model

    def train(self, x, y, epoch=1, verbose=0, batchSize=64):
        self.model.fit(x, y, epoch, verbose)

    def predict(self, s, target=False):
            return self.model.predict(s)

    def predicFlatten(self, s, target=False):
        return self.predict(s.reshape(1, self.stateCount), target=target).flatten()
