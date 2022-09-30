import numpy


class Exchange:

  def __init__(self, target, name):
    self.my_array = numpy.array([0, 1, 2, 3, 4])
    self.apiCalls = 0
    self.target = target
    self.path = {}
    self.name = name

  def addPath(self, input, where):
    self.path[input] = self.target + '/' + where
    self.apiCalls += 1

  def getPath(self, input):
    print(self.path[input])
    self.apiCalls += 1

  def getCallAmount(self):
    return self.apiCalls
