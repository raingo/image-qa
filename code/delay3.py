from lstm import *

def getData(trainSize, testSize, length):
    trainInput = np.zeros((trainSize, length, 1), float)
    trainTarget = np.zeros((trainSize, length, 1), float)
    testInput = np.zeros((testSize, length, 1), float)
    testTarget = np.zeros((testSize, length, 1), float)
    for i in range(0, trainSize):
        for j in range(0, length):
            trainInput[i, j, :] = np.round(np.random.rand(1))
            if j >= 3:
                trainTarget[i, j, :] = trainInput[i, j - 3, :]
    for i in range(0, testSize):
        for j in range(0, length):
            testInput[i, j, :] = np.round(np.random.rand(1))
            if j >= 3:
                testTarget[i, j, :] = testInput[i, j - 3, :]
    return trainInput, trainTarget, testInput, testTarget

if __name__ == '__main__':
    lstm = LSTM(
        inputDim=1,
        memoryDim=5,
        initRange=0.01,
        initSeed=2)

    trainOpt = {
        'learningRate': 0.3,
        'numEpoch': 2000,
        'momentum': 0.0,
        'batchSize': 1,
        'learningRateDecay': 1.0,
        'momentumEnd': 0.0,
        'needValid': True,
        'name': 'delay3_train',
        'plotFigs': True,
        'combineFnDeriv': simpleSumDeriv,
        'calcError': True,
        'decisionFn': simpleSumDecision,
        'stoppingE': 0.005,
        'stoppingR': 1.0
    }

    np.random.seed(2)
    trainSize = 20
    testSize = 1000
    length = 8
    trainInput, trainTarget, testInput, testTarget = getData(trainSize, testSize, length)
    lstm.train(trainInput, trainTarget, trainOpt)
    rate, correct, total = lstm.testRate(testInput, testTarget, simpleSumDecision)

    print 'TR: %.4f' % rate
    lstm.save('delay3.npy')
    raw_input('Press Enter to continue.')
    pass