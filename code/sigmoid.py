from util_func import *

class Sigmoid:
    def __init__(self,
                 inputDim,
                 outputDim,
                 initRange=1.0,
                 initSeed=2,
                 needInit=True,
                 initWeights=0):
        self.inputDim = inputDim
        self.outputDim = outputDim
        self.random = np.random.RandomState(initSeed)

        if needInit:
            self.W = np.random.uniform(
                -initRange/2.0, initRange/2.0,
                (outputDim, inputDim + 1))
            self.W[:, -1] = 0
        else:
            self.W = initWeights
        self.X = 0
        self.Y = 0
        pass

    def chkgrd(self):
        X = np.array([0.1, 0.5])
        T = np.array([0])
        Y = self.forwardPass(X)
        E, dEdY = crossEntOne(Y, T)
        dEdW, dEdX = self.backPropagate(dEdY)
        eps = 1e-3
        dEdWTmp = np.zeros(self.W.shape)
        dEdXTmp = np.zeros(X.shape[-1])
        for i in range(0, self.W.shape[0]):
            for j in range(0, self.W.shape[1]):
                self.W[i,j] += eps
                Y = self.forwardPass(X)
                Etmp1, d1 = crossEntOne(Y, T)

                self.W[i,j] -= 2 * eps
                Y = self.forwardPass(X)
                Etmp2, d2 = crossEntOne(Y, T)

                dEdWTmp[i,j] = (Etmp1 - Etmp2) / 2.0 / eps
                self.W[i,j] += eps
        for j in range(0, X.shape[-1]):
            X[j] += eps
            Y = self.forwardPass(X)
            Etmp1, d1 = crossEntOne(Y, T)

            X[j] -= 2 * eps
            Y = self.forwardPass(X)
            Etmp2, d2 = crossEntOne(Y, T)

            dEdXTmp[j] += (Etmp1 - Etmp2) / 2.0 / eps
            X[j] += eps

        X = np.array([[0.1, 0.5], [0.2, 0.4], [0.3, -0.3], [-0.1, -0.1]])
        T = np.array([[0], [1], [0], [1]])
        Y = self.forwardPass(X)
        E, dEdY = crossEntOne(Y, T)
        dEdW, dEdX = self.backPropagate(dEdY)
        dEdWTmp = np.zeros(self.W.shape)
        dEdXTmp = np.zeros(X.shape)
        for i in range(0, self.W.shape[0]):
            for j in range(0, self.W.shape[1]):
                self.W[i,j] += eps
                Y = self.forwardPass(X)
                Etmp1, d1 = crossEntOne(Y, T)

                self.W[i,j] -= 2 * eps
                Y = self.forwardPass(X)
                Etmp2, d2 = crossEntOne(Y, T)

                dEdWTmp[i,j] = (Etmp1 - Etmp2) / 2.0 / eps
                self.W[i,j] += eps
        for t in range(0, X.shape[0]):
            for k in range(0, X.shape[-1]):
                X[t, k] += eps
                Y = self.forwardPass(X)
                Etmp1, d1 = crossEntOne(Y, T)

                X[t, k] -= 2 * eps
                Y = self.forwardPass(X)
                Etmp2, d2 = crossEntOne(Y, T)

                dEdXTmp[t, k] += (Etmp1 - Etmp2) / 2.0 / eps
                X[t, k] += eps

        print "haha"
        pass

    def forwardPass(self, X):
        if len(X.shape) == 2:
            X2 = np.concatenate((X, np.ones((X.shape[0], 1), float)), axis=1)
        else:
            X2 = np.concatenate((X, np.ones(1)))
        Y = np.inner(X2, self.W)
        Y = sigmoidFn(Y)
        self.X = X2
        self.Y = Y
        return Y

    def backPropagate(self, dEdY, outputdEdX=True):
        if len(self.X.shape) == 2:
            return self.backPropagateAll(dEdY, outputdEdX)

        Y = self.Y
        X = self.X
        dEdZ = dEdY * Y * (1 - Y)
        dEdW = np.outer(Y, X)

        if outputdEdX:
            dEdX = np.dot(dEdZ, self.W[:, :-1])

        return dEdW, dEdX

    def backPropagateAll(self, dEdY, outputdEdX=True):
        Y = self.Y
        X = self.X
        dEdZ = dEdY * Y * (1 - Y)
        dEdW = np.dot(dEdZ.transpose(), X)

        if outputdEdX:
            dEdX = np.dot(dEdZ, self.W[:, :-1])

        return dEdW, dEdX

if __name__ == '__main__':
    sigmoid = Sigmoid(
        inputDim=2,
        outputDim=1,
        initRange=0.01,
        initSeed=2)
    sigmoid.chkgrd()
