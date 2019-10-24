import configparser
import os

from component.ImageTester import ImageTester

config = configparser.ConfigParser()
config.read('config/parameters.ini')

imageTester = ImageTester(config['app']['OverwatchAppName'])

compDir = 'resources/test_screens/comp/'
compImgs = os.listdir(compDir)

for img in compImgs:
    isComp, isQp = imageTester.analyze(compDir + img)
    assert isComp
    print("comp {} is ok".format(img))

qpDir = 'resources/test_screens/qp/'
qpImgs = os.listdir(qpDir)

for img in qpImgs:
    isComp, isQp = imageTester.analyze(qpDir + img)
    assert isQp
    print("qp {} is ok".format(img))

print('All tests done!')
