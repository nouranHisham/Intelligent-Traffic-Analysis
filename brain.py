from keras.models import Sequential
from keras.layers import *
from keras.optimizers import *

class Brain:
    def __init__(self, stateCount, actionCount):
        self.stateCount = stateCount
        self.actionCount = actionCount

        self.model = self.buildModel()

    def buildModel(self):
        model = Sequential()

        model.add(Dense(units=64, activation='relu', input_dim=self.stateCnt))
        model.add(Dense(units=self.actionCnt, activation='linear'))

        opt = RMSprop(lr=0.00025)
        model.compile(loss='mse', optimizer=opt)

        return model

    def train(self, x, y, epoch=1, verbose=0, batchSize=64):
        self.model.fit(x, y, batchSize, epoch, verbose)

    def predict(self, s):
        return self.model.predict(s)

    def predicFlatten(self, s):
        return self.predict(s.reshape(1, self.stateCnt)).flatten()