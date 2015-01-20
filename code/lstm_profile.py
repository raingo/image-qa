from lstm import *

lstm = LSTM(
    inputDim=20,
    memoryDim=10,
    initRange=.1,
    initSeed=3,
    cutOffZeroEnd=True)

for i in range(0, 10):
    X = np.random.rand(10, 100, 20)
    Y = lstm.forwardPass(X)
    dEdY = np.random.rand(10, 100, 10)
    dEdY = lstm.backPropagate(dEdY, outputdEdX=False)
