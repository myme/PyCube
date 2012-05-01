import unittest

from cube import *
from quaternion import *
import solver

class CubeTestCase(unittest.TestCase):
    def setUp(self):
        self.cube = Cube(3)
    
    def testCreateCube(self):
        assert self.cube.n == 3

    def testLoadCube(self):
        assert solver.loadCube(self.cube) == True

    def testSolvedDefault(self):
        self.testLoadCube()
        assert solver.isSolved() == True

    def testNotSolvedRandom(self):
        self.cube.scramble()
        self.testLoadCube()
        assert solver.isSolved() == False
    
    def testCreateToBig(self):
        try:
            Cube(1)
            Cube(10)
        except TypeError:
            pass
        else:
            fail("expected a TypeError")
    def testRotateAlot(self):
        i=0
        while True:
            i = i+1
            self.cube.doAction('UL', True)
            self.cube.doAction('RU', True)
            
            self.testLoadCube()
            
            if i == 50: break
        pass

    def testCorrectSolution(self):
        moves = ['DR', 'RU', 'UL', 'LD']
        correct = ['LU', 'UR', 'RD', 'DL']
        for move in moves:
            self.cube.doAction(move, True)

        self.testLoadCube()

        assert solver.solveCube() == correct

    def testPossibleSolution(self):
        self.testNotSolvedRandom()
        self.testLoadCube()
        assert len(solver.solveCube()) > 0

    def testNoErrorOnBigCube(self):
        cube = Cube(5)
        assert solver.loadCube(cube) == False

class QuaternionTestCase(unittest.TestCase):
    def setUp(self):
        self.quat = Quaternion()

    def testCreateQuaternion(self):
        w, x, y, z = self.quat.elements
        assert w == 1.0
        assert x == 0.0
        assert y == 0.0
        assert z == 0.0

    def testInitialState(self):
        x, y, z, r = self.quat.getAngleAxis()
        assert x == 0.0
        assert y == 0.0
        assert z == 1.0
        assert r == 0.0

    def testRotateQuaternion1Axis(self):
        self.quat.rotate90("left")
        x, y, z, r = self.quat.getAngleAxis()
        assert x == 0.0
        assert y == -1.0
        assert z == 0.0
        assert r == 90.0

        self.quat.rotate90("left")
        x, y, z, r = self.quat.getAngleAxis()
        assert x == 0.0
        assert y == -1.0
        assert z == 0.0
        assert r > 17.9999 and r < 180.0001

        self.quat.rotate90("left")
        self.quat.rotate90("left")
        x, y, z, r = self.quat.getAngleAxis()
        assert x == 0.0
        assert y < -1.0
        assert z == 0.0
        assert r % 360 < 0.0001 or r % 360 > 359.9999

    def testFromEuler(self):
        q = fromEuler(90., 0., 0.)
        x, y, z, r = q.getAngleAxis()

        assert x == 1.0
        assert y == 0.0
        assert z == 0.0
        assert r == 90.0

if __name__ == '__main__':
    cubeSuite = unittest.makeSuite(CubeTestCase, 'test')
    quatSuite = unittest.makeSuite(QuaternionTestCase, 'test')

    runner = unittest.TextTestRunner()
    runner.run(cubeSuite)
    runner.run(quatSuite)

