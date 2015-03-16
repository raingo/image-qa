from lstm_old import *
from map import *
from lut import *
from inner_prod import *
from reshape import *
from cos_sim import *
from sum import *
from elem_prod import *
from active import *
from sum_prod import *
from active_func import *
from selector import *
import unittest
import numpy as np

class StageTests(unittest.TestCase):
    def calcgrd(self, X, T):
        Y = self.model.forward(X)
        W = self.stage.W
        E, dEdY = self.costFn(Y, T)
        dEdX = self.model.backward(dEdY)
        dEdW = self.stage.dEdW
        eps = 1e-3
        dEdXTmp = np.zeros(X.shape)

        if hasattr(W, 'shape'):
            dEdWTmp = np.zeros(W.shape)
            for i in range(0, self.stage.W.shape[0]):
                for j in range(0, self.stage.W.shape[1]):
                    self.stage.W[i,j] += eps
                    Y = self.model.forward(X)
                    Etmp1, d1 = self.costFn(Y, T)

                    self.stage.W[i,j] -= 2 * eps
                    Y = self.model.forward(X)
                    Etmp2, d2 = self.costFn(Y, T)

                    dEdWTmp[i,j] = (Etmp1 - Etmp2) / 2.0 / eps
                    self.stage.W[i,j] += eps
        else:
            dEdW = 0
            dEdWTmp = 0  
        if self.testInputErr:
            if len(X.shape) == 3:
                for n in range(0, X.shape[0]):
                    for t in range(0, X.shape[1]):
                        for j in range(0, X.shape[2]):
                            X[n, t, j] += eps
                            Y = self.model.forward(X)
                            Etmp1, d1 = self.costFn(Y, T)

                            X[n, t, j] -= 2 * eps
                            Y = self.model.forward(X)
                            Etmp2, d2 = self.costFn(Y, T)

                            dEdXTmp[n, t, j] = (Etmp1 - Etmp2) / 2.0 / eps
                            X[n, t, j] += eps

            elif len(X.shape) == 2:
                for n in range(0, X.shape[0]):
                    for j in range(0, X.shape[1]):
                        X[n, j] += eps
                        Y = self.model.forward(X)
                        Etmp1, d1 = self.costFn(Y, T)

                        X[n, j] -= 2 * eps
                        Y = self.model.forward(X)
                        Etmp2, d2 = self.costFn(Y, T)

                        dEdXTmp[n, j] = (Etmp1 - Etmp2) / 2.0 / eps
                        X[n, j] += eps

            elif len(X.shape) == 1:
                for j in range(0, X.shape[0]):
                    X[j] += eps
                    Y = self.model.forward(X)
                    Etmp1, d1 = self.costFn(Y, T)

                    X[j] -= 2 * eps
                    Y = self.model.forward(X)
                    Etmp2, d2 = self.costFn(Y, T)

                    dEdXTmp[j] = (Etmp1 - Etmp2) / 2.0 / eps
                    X[j] += eps
        else:
            dEdX = None
            dEdXTmp = None
        return dEdW, dEdWTmp, dEdX, dEdXTmp

    def chkgrd(self, dE, dETmp, tolerance=1e-4):
        dE = dE.reshape(dE.size)
        dETmp = dETmp.reshape(dE.size)
        for i in range(dE.size):
            self.assertTrue(
                (dE[i] == 0 and dETmp[i] == 0) or
                (np.abs(dE[i] / dETmp[i] - 1) < tolerance))

class LSTM_MultiErr_Tests(StageTests):
    """LSTM_Old multi error tests"""
    def setUp(self):
        self.stage = LSTM_Old(
            inputDim=5,
            outputDim=3,
            initRange=0.1,
            initSeed=1,
            multiErr=True,
            cutOffZeroEnd=False)
        self.model = self.stage
        self.testInputErr = True
        self.costFn = meanSqErr
    def test_grad(self):
        random = np.random.RandomState(2)
        X = random.uniform(-0.1, 0.1, (6,4,5))
        T = random.uniform(-0.1, 0.1, (6,4,3))
        dEdW, dEdWTmp, dEdX, dEdXTmp = self.calcgrd(X, T)
        self.chkgrd(dEdW, dEdWTmp)
        self.chkgrd(dEdX, dEdXTmp)

class LSTM_MultiErrCutZero_Tests(StageTests):
    """LSTM_Old single error tests"""
    def setUp(self):
        self.stage = LSTM_Old(
            inputDim=5,
            outputDim=3,
            initRange=0.1,
            initSeed=1,
            multiErr=True,
            cutOffZeroEnd=True)
        self.model = self.stage
        self.testInputErr = True
        self.costFn = meanSqErr
    def test_grad(self):
        random = np.random.RandomState(2)
        X = np.concatenate(
            (random.uniform(-0.1, 0.1, (6,4,5)),
            np.zeros((6,3,5))), axis=1)
        T = np.concatenate(
            (random.uniform(-0.1, 0.1, (6,4,3)),
            np.zeros((6,4,3))), axis=1) # Need one more time dimension for cut off.
        dEdW, dEdWTmp, dEdX, dEdXTmp = self.calcgrd(X, T)
        self.chkgrd(dEdW, dEdWTmp)
        self.chkgrd(dEdX[:,0:4], dEdXTmp[:,0:4])

class LSTM_SingleErr_Tests(StageTests):
    """LSTM_Old single error tests"""
    def setUp(self):
        self.stage = LSTM_Old(
            inputDim=5,
            outputDim=3,
            initRange=0.1,
            initSeed=1,
            multiErr=False,
            cutOffZeroEnd=False)
        self.model = self.stage
        self.testInputErr = True
        self.costFn = meanSqErr
    def test_grad(self):
        random = np.random.RandomState(2)
        X = random.uniform(-0.1, 0.1, (6,4,5))
        T = random.uniform(-0.1, 0.1, (6,3))
        dEdW, dEdWTmp, dEdX, dEdXTmp = self.calcgrd(X, T)
        self.chkgrd(dEdW, dEdWTmp)
        self.chkgrd(dEdX, dEdXTmp)

class LSTM_SingleErrCutZero_Tests(StageTests):
    """LSTM_Old single error tests"""
    def setUp(self):
        self.stage = LSTM_Old(
            inputDim=5,
            outputDim=3,
            initRange=0.1,
            initSeed=1,
            multiErr=False,
            cutOffZeroEnd=True)
        self.model = self.stage
        self.testInputErr = True
        self.costFn = meanSqErr
    def test_grad(self):
        random = np.random.RandomState(2)
        X = np.concatenate(
            (random.uniform(-0.1, 0.1, (6,4,5)),
            np.zeros((6,3,5))), axis=1)
        T = random.uniform(-0.1, 0.1, (6,3))
        dEdW, dEdWTmp, dEdX, dEdXTmp = self.calcgrd(X, T)
        self.chkgrd(dEdW, dEdWTmp)
        self.chkgrd(dEdX[:,0:4], dEdXTmp[:,0:4])

class MapIdentity_Tests(StageTests):
    """Linear map tests"""
    def setUp(self):
        self.stage = Map(
            outputDim=3,
            initRange=0.1,
            initSeed=1,
            activeFn=IdentityActiveFn)
        self.model = self.stage
        self.testInputErr = True
        self.costFn = meanSqErr
    def test_grad(self):
        random = np.random.RandomState(2)
        X = random.uniform(-0.1, 0.1, (6,5))
        T = random.uniform(-0.1, 0.1, (6,3))
        dEdW, dEdWTmp, dEdX, dEdXTmp = self.calcgrd(X, T)
        self.chkgrd(dEdW, dEdWTmp)
        self.chkgrd(dEdX, dEdXTmp)

class MapSigmoid_Tests(StageTests):
    """Sigmoid map tests"""
    def setUp(self):
        self.stage = Map(
            outputDim=3,
            initRange=0.1,
            initSeed=1,
            activeFn=SigmoidActiveFn)
        self.model = self.stage
        self.testInputErr = True
        self.costFn = meanSqErr
    def test_grad(self):
        random = np.random.RandomState(2)
        X = random.uniform(-0.1, 0.1, (6,5))
        T = random.uniform(-0.1, 0.1, (6,3))
        dEdW, dEdWTmp, dEdX, dEdXTmp = self.calcgrd(X, T)
        self.chkgrd(dEdW, dEdWTmp)
        self.chkgrd(dEdX, dEdXTmp)

class MapSigmoid_CrossEnt_Tests(StageTests):
    """Sigmoid map tests"""
    def setUp(self):
        self.stage = Map(
            outputDim=3,
            initRange=0.1,
            initSeed=1,
            activeFn=SigmoidActiveFn)
        self.model = self.stage
        self.testInputErr = True
        self.costFn = crossEntOne
    def test_grad(self):
        random = np.random.RandomState(2)
        X = random.uniform(-0.1, 0.1, (6,5))
        T = random.uniform(0, 1, (6,3)).astype(int)
        dEdW, dEdWTmp, dEdX, dEdXTmp = self.calcgrd(X, T)
        self.chkgrd(dEdW, dEdWTmp)
        self.chkgrd(dEdX, dEdXTmp)

class MapSoftmax_Tests(StageTests):
    """Sigmoid map tests"""
    def setUp(self):
        self.stage = Map(
            outputDim=3,
            initRange=0.1,
            initSeed=1,
            activeFn=SoftmaxActiveFn)
        self.model = self.stage
        self.testInputErr = True
        self.costFn = meanSqErr
    def test_grad(self):
        random = np.random.RandomState(2)
        X = random.uniform(-0.1, 0.1, (6,5))
        T = random.uniform(-0.1, 0.1, (6,3))
        dEdW, dEdWTmp, dEdX, dEdXTmp = self.calcgrd(X, T)
        self.chkgrd(dEdW, dEdWTmp)
        self.chkgrd(dEdX, dEdXTmp)

class MapSoftmax_CrossEnt_Tests(StageTests):
    """Linear map tests"""
    def setUp(self):
        self.stage = Map(
            outputDim=3,
            initRange=0.1,
            initSeed=1,
            activeFn=SoftmaxActiveFn)
        self.model = self.stage
        self.testInputErr = True
        self.costFn = crossEntIdx
    def test_grad(self):
        random = np.random.RandomState(2)
        X = random.uniform(-0.1, 0.1, (6,5))
        T = random.uniform(0, 2, (6)).astype(int)
        dEdW, dEdWTmp, dEdX, dEdXTmp = self.calcgrd(X, T)
        self.chkgrd(dEdW, dEdWTmp)
        self.chkgrd(dEdX, dEdXTmp)

class LUT_Tests(StageTests):
    """Lookup table tests"""
    def setUp(self):
        self.stage = LUT(
            inputDim=5,
            outputDim=3,
            inputNames=None,
            initRange=0.1,
            initSeed=1,
            learningRate=0.9)
        self.model = self.stage
        self.testInputErr = False
        self.costFn = meanSqErr
    def test_grad(self):
        random = np.random.RandomState(2)
        X = np.array([1,2,3,4,5], dtype=int)
        T = random.uniform(-0.1, 0.1, (5,3))
        dEdW, dEdWTmp, dEdX, dEdXTmp = self.calcgrd(X, T)
        self.chkgrd(dEdW, dEdWTmp)

class Active_Tests(StageTests):
    def setUp(self):
        self.stage = Active(
            outputDim=6,
            name='active',
            inputNames=None,
            activeFn=TanhActiveFn())
        self.model = self.stage
        self.testInputErr = True
        self.costFn = meanSqErr
    def test_grad(self):
        random = np.random.RandomState(2)
        X = random.uniform(-0.1, 0.1, (3,6))
        T = random.uniform(-0.1, 0.1, (3,6))
        dEdW, dEdWTmp, dEdX, dEdXTmp = self.calcgrd(X, T)
        self.chkgrd(dEdX, dEdXTmp)

class InnerProduct_Tests(StageTests):
    """Inner product tests"""
    def setUp(self):
        self.stage = InnerProduct(
            name='inner',
            inputNames=None,
            outputDim=0)
        self.model = self.stage
        self.testInputErr = True
        self.costFn = meanSqErr
    def test_grad(self):
        random = np.random.RandomState(2)
        X = random.uniform(-0.1, 0.1, (6,2,5))
        T = random.uniform(-0.1, 0.1, (6,1))
        dEdW, dEdWTmp, dEdX, dEdXTmp = self.calcgrd(X, T)
        self.chkgrd(dEdX, dEdXTmp)

class Reshape_Tests(StageTests):
    def setUp(self):
        self.stage = Reshape(
            reshapeFn='(x[0], x[1] / 2, 2)')
        self.model = self.stage
        self.testInputErr = True
        self.costFn = meanSqErr
    def test_grad(self):
        random = np.random.RandomState(2)
        X = random.uniform(-0.1, 0.1, (6, 10))
        T = random.uniform(-0.1, 0.1, (6, 5, 2))
        dEdW, dEdWTmp, dEdX, dEdXTmp = self.calcgrd(X, T)
        self.chkgrd(dEdX, dEdXTmp)

class Sum_Tests(StageTests):
    def setUp(self):
        self.stage = Sum(
            outputDim=3,
            name='sum',
            inputNames=None,
            numComponents=2)
        self.model = self.stage
        self.testInputErr = True
        self.costFn = meanSqErr
    def test_grad(self):
        random = np.random.RandomState(2)
        X = random.uniform(-0.1, 0.1, (3,6))
        T = random.uniform(-0.1, 0.1, (3,3))
        dEdW, dEdWTmp, dEdX, dEdXTmp = self.calcgrd(X, T)
        self.chkgrd(dEdX, dEdXTmp)

class ElementProduct_Tests(StageTests):
    def setUp(self):
        self.stage = ElementProduct(
            outputDim=3,
            name='product',
            inputNames=None)
        self.model = self.stage
        self.testInputErr = True
        self.costFn = meanSqErr
    def test_grad(self):
        random = np.random.RandomState(2)
        X = random.uniform(-0.1, 0.1, (3,6))
        T = random.uniform(-0.1, 0.1, (3,3))
        dEdW, dEdWTmp, dEdX, dEdXTmp = self.calcgrd(X, T)
        self.chkgrd(dEdX, dEdXTmp)

class CosSimilarity_Tests(StageTests):
    def setUp(self):
        self.stage = CosSimilarity(
            bankDim=6,
            inputNames=None,
            outputDim=0,
            name='cos')
        self.model = self.stage
        self.testInputErr = True
        self.costFn = rankingLoss
    def test_grad(self):
        random = np.random.RandomState(2)
        X = random.uniform(-1, 1, (10, 12))
        T = random.uniform(0, 6, (4)).astype(int)
        dEdW, dEdWTmp, dEdX, dEdXTmp = self.calcgrd(X, T)
        self.chkgrd(dEdX, dEdXTmp)

class Selector_Tests(StageTests):
    def setUp(self):
        self.stage = Selector(
            name='sel',
            inputNames=None,
            start=5,
            end=10,
            axis=-1)
        self.model = self.stage
        self.testInputErr = True
        self.costFn = meanSqErr
    def test_grad(self):
        random = np.random.RandomState(2)
        X = random.uniform(-0.1, 0.1, (3,15))
        T = random.uniform(-0.1, 0.1, (3,5))
        dEdW, dEdWTmp, dEdX, dEdXTmp = self.calcgrd(X, T)
        self.chkgrd(dEdX, dEdXTmp)

class SumProduct_Tests(StageTests):
    def setUp(self):
        self.stage = SumProduct(
            name='sp', 
            inputNames=None,
            sumAxis=1, 
            outputDim=10
            )
        self.model = self.stage
        self.testInputErr = True
        self.costFn = meanSqErr
    def test_grad(self):
        random = np.random.RandomState(2)
        X = [random.uniform(-0.1, 0.1, (3, 10, 1)), 
             random.uniform(-0.1, 0.1, (3, 10, 5))]
        T = random.uniform(-0.1, 0.1, (3, 5))
        
        Y = self.model.forward(X)
        W = self.stage.W
        E, dEdY = self.costFn(Y, T)
        dEdX = self.model.backward(dEdY)

        eps = 1e-3
        dEdXTmp = np.zeros(X[0].shape)
        for n in range(0, 3):
            for t in range(0, 10):
                X[0][n, t] += eps
                Y = self.model.forward(X)
                Etmp1, d1 = self.costFn(Y, T)

                X[0][n, t] -= 2 * eps
                Y = self.model.forward(X)
                Etmp2, d2 = self.costFn(Y, T)

                dEdXTmp[n, t] = (Etmp1 - Etmp2) / 2.0 / eps
                X[0][n, t] += eps
        self.chkgrd(dEdX[0], dEdXTmp)
        dEdXTmp = np.zeros(X[1].shape)
        for n in range(0, 3):
            for t in range(0, 10):
                for j in range (0, 5):
                    X[1][n, t, j] += eps
                    Y = self.model.forward(X)
                    Etmp1, d1 = self.costFn(Y, T)

                    X[1][n, t, j] -= 2 * eps
                    Y = self.model.forward(X)
                    Etmp2, d2 = self.costFn(Y, T)

                    dEdXTmp[n, t, j] = (Etmp1 - Etmp2) / 2.0 / eps
                    X[1][n, t, j] += eps
        self.chkgrd(dEdX[1], dEdXTmp)


if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTests(
        unittest.TestLoader().loadTestsFromTestCase(LSTM_MultiErr_Tests))
    suite.addTests(
        unittest.TestLoader().loadTestsFromTestCase(LSTM_MultiErrCutZero_Tests))
    suite.addTests(
        unittest.TestLoader().loadTestsFromTestCase(LSTM_SingleErr_Tests))
    suite.addTests(
        unittest.TestLoader().loadTestsFromTestCase(LSTM_SingleErrCutZero_Tests))
    suite.addTests(
        unittest.TestLoader().loadTestsFromTestCase(MapIdentity_Tests))
    suite.addTests(
        unittest.TestLoader().loadTestsFromTestCase(MapSigmoid_Tests))
    suite.addTests(
        unittest.TestLoader().loadTestsFromTestCase(MapSigmoid_CrossEnt_Tests))
    suite.addTests(
        unittest.TestLoader().loadTestsFromTestCase(MapSoftmax_Tests))
    suite.addTests(
        unittest.TestLoader().loadTestsFromTestCase(MapSoftmax_CrossEnt_Tests))
    suite.addTests(
        unittest.TestLoader().loadTestsFromTestCase(LUT_Tests))
    suite.addTests(
        unittest.TestLoader().loadTestsFromTestCase(InnerProduct_Tests))
    suite.addTests(
        unittest.TestLoader().loadTestsFromTestCase(TimeSum_Tests))
    suite.addTests(
        unittest.TestLoader().loadTestsFromTestCase(Reshape_Tests))
    suite.addTests(
        unittest.TestLoader().loadTestsFromTestCase(Sum_Tests))
    suite.addTests(
        unittest.TestLoader().loadTestsFromTestCase(ElementProduct_Tests))
    suite.addTests(
        unittest.TestLoader().loadTestsFromTestCase(Active_Tests))
    suite.addTests(
        unittest.TestLoader().loadTestsFromTestCase(CosSimilarity_Tests))
    suite.addTests(
          unittest.TestLoader().loadTestsFromTestCase(Selector_Tests))
    suite.addTests(
          unittest.TestLoader().loadTestsFromTestCase(SumProduct_Tests))
    unittest.TextTestRunner(verbosity=2).run(suite)