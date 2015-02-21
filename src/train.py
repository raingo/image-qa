import nn
import numpy as np
import sys
import yaml

'''
Usage: python train.py {name} -d {train data} -m {model spec} -c {config} -o {output folder}
'''

def readFlags():
    if len(sys.argv) < 2:
        raise Exception('Name not specified')
    name = sys.argv[1]
    outputFolder = None
    configFilename = None
    trainDataFilename = None
    testDataFilename = None
    modelFilename = None
    for i in range(2, len(sys.argv) - 1):
        if sys.argv[i] == '-o' or sys.argv[i] == '-out':
            outputFolder = sys.argv[i + 1]
        elif sys.argv[i] == '-d' or sys.argv[i] == '-data':
            trainDataFilename = sys.argv[i + 1]
        elif sys.argv[i] == '-t' or sys.argv[i] == '-test':
            testDataFilename = sys.argv[i + 1]
        elif sys.argv[i] == '-m' or sys.argv[i] == '-model':
            modelFilename = sys.argv[i + 1]
        elif sys.argv[i] == '-c' or sys.argv[i] == '-config':
            configFilename = sys.argv[i + 1]

    if configFilename is None:
        raise Exception('Config file not specified')
    if trainDataFilename is None:
        raise Exception('Data file not specified')
    if modelFilename is None:
        raise Exception('Model file not specified')

    return name, modelFilename, configFilename, trainDataFilename, outputFolder

if __name__ == '__main__':
    name, modelFilename, configFilename, trainDataFilename, outputFolder = readFlags()
    with open(configFilename) as f:
        trainOpt = yaml.load(f)
    trainData = np.load(trainDataFilename)
    trainInput = trainData[0]
    trainTarget = trainData[1]
    model = nn.load(modelFilename)
    trainer = nn.Trainer(
        name=name+'-v',
        model=model,
        trainOpt=trainOpt,
        outputFolder=outputFolder
    )
    trainer.train(trainInput, trainTarget)

    # Retrain with all the data
    trainOpt['needValid'] = False
    trainOpt['numEpoch'] = trainer.stoppedEpoch + 1
    model = nn.load(modelFilename)
    trainer = nn.Trainer(
        name=name,
        model=model,
        trainOpt=trainOpt,
        outputFolder=outputFolder
    )
    trainer.train(trainInput, trainTarget)

    if testDataFilename is not None:
        testData = np.load(testDataFilename)
        testInput = testData[0]
        testTarget = testData[1]
        model = nn.load(modelFilename)
        model.loadWeights(np.load(trainer.modelFilename))
        testOutput = nn.test(model, testInput, testTarget)
        testRate, c, t = nn.calcRate(model, testOutput, testTarget)
        with open(os.path.join(outputFolder, 'result.txt'), 'w+') as f:
            f.write('Test rate: %f' % testRate)