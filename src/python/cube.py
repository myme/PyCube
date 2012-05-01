import OpenGL.GL as gl
import OpenGL.GLU as glu
import OpenGL.GLUT as glut

import math
import time
import random

from box import *
from quaternion import *
import solver

"""Rounds an angle to the nearest 90 degrees."""
def round(x):
    return math.floor(( (x + 45.0) / 90.0 ) ) * 90.0

# This class represents an entire rubik's cube. The size of a cube is determined
# by the number of cubes in the x, y, and z direction. A cube is a cube in its
# original definition, meaning it is of equal size inn all directions.
# A cube would then be constructed of n^3 boxes, but since the center of the
# cube is irrelevant, the number of boxes in a cube would be n^3 - (n-2)^3.
# This logic should be fairly clear. The boxes of the cube should be looked upon
# as "stupid" or "dumb" boxes, only knowing their own rotation around their own
# axes and their own position relative to the cube center.
class Cube:
    def __init__(self, nSide):

        if nSide < 2 or nSide > 7:
            raise TypeError("A cube can only be between 2^3 and 7^3 large")

        # A display list ("listId") holds the drawing routine of a box.
        self.boxSize = 1
        listId = buildBox(size=self.boxSize)

        # Place the cube in a nice position
        self.pos = list((0., 0., - (math.sqrt((nSide ** 2) + (nSide ** 2)) + nSide)))

        # The cube dimension and a list containing the boxes of the cube
        self.n = nSide
        self.boxes = []

        # Some member variabels containing rotation information. Names should
        # be self explanatory.
        self.rotVal = 3.14
        self.rot = [0., 0., 0.]
        self.sideRot = [0., 0., 0.]

        # Some helping member variables which hold several states of the cube.
        # Their purpose becomes clear with their use and/or name.
        self.oldMouseX = 0
        self.oldMouseY = 0
        self.moveDir = ""
        self.rotateList = []
        self.clickable = []
        self.selectedBox = -1

        # A cube is build up of 'boxCount' smaller boxes
        self.boxCount = nSide ** 3

        for i in range(self.boxCount):
            excluded = self.excludedBoxes()

            if self.isClickable(i):
                self.clickable.append(i)

            if not i in excluded:
                pos = self.positionBox(i)
                self.boxes.append(Box(listId, i, pos))
            else:
                self.boxes.append(0)

        # initiate solver
        solver.init()

    def __iter__(self):
        for i in xrange(self.boxCount):
            if self.boxes[i] != 0:
                yield i

    # These are the boxes that should not be drawn. i.e. the
    # boxes that would have been in the middle of the cube.
    def excludedBoxes(self):
        excluded = []
        n = self.n

        for i in range(n ** 3):
            if i >= n ** 2 and i < n ** 3 - n ** 2:
                tmp = i - ( int( i / n ** 2 ) * n ** 2 )

                if tmp > n and tmp < n ** 2 - n:
                    if tmp % n != 0 and tmp % n != n - 1:
                        excluded.append(i)

        return excluded

    # Calculates if a box in the cube should be clickable and therfore
    # also a control box for rotation
    def isClickable(self, id):
        odd = self.n % 2
        middle = int( self.n / 2 )

        x = self.findXFromId(id)
        y = self.findYFromId(id)
        z = self.findZFromId(id)

        if odd and (x == middle or y == middle or z == middle):
            return False

        accum = 0

        if x == 0 or x == self.n - 1:
            accum = accum + 1

        if y == 0 or y == self.n - 1:
            accum = accum + 1

        if z == 0 or z == self.n - 1:
            accum = accum + 1

        # If the box is positioned on more than one side
        # it's automatically clickable
        if accum >= 2:
            return True

        return False

    def relativeToAbsolutePos(self, relPos):
        pos = []

        pos.append(relPos[0] - float(self.n - 1) / 2)
        pos.append(float(self.n - 1) / 2 - relPos[1])
        pos.append(float(self.n - 1) / 2 - relPos[2])

        return pos

    # Gives a box the correct position in relation to the cube's center
    def positionBox(self, id):
        relPos = self.findRelativePos(id)
        
        return self.relativeToAbsolutePos(relPos)

    # Finds the plane where a box belongs. Planes are indexed starting
    # at 0 and up to n - 1, where n is the one-dimensional size of the cube.
    def findRelativePos(self, id):
        pos = []

        pos.append(self.findXFromId(id))
        pos.append(self.findYFromId(id))
        pos.append(self.findZFromId(id))

        return pos

    # Dynamically finds the x-position of a box relative
    # to the cube center.
    def findXFromId(self, id):
        return id % self.n

    # Dynamically finds the y-position of a box relative
    # to the cube center.
    def findYFromId(self, id):
        return int( id / self.n ) % self.n

    # Dynamically finds the z-position of a box relative
    # to to the cube center.
    def findZFromId(self, id):
        return int( id / self.n ** 2 )
    
    # Self explanatory really.
    def drawCube(self):
        gl.glPushMatrix()
        self.setUpCubeTransRot()

        # Draw all the boxes
        for id in range(self.boxCount):
            if self.boxes[id] == 0:
                continue

            gl.glPushMatrix()
            if id in self.rotateList:
                self.setUpSideRot()

            self.boxes[id].drawBox()
            gl.glPopMatrix()

        gl.glPopMatrix()

    # Sets up the cube's main rotation and position
    def setUpCubeTransRot(self):
        # Sets up the matrices for projecting the cube
        gl.glLoadIdentity()
        gl.glTranslatef(self.pos[0], self.pos[1], self.pos[2])

        gl.glRotatef(self.rot[0], 1., 0., 0.)
        gl.glRotatef(self.rot[1], 0., 1., 0.)
        gl.glRotatef(self.rot[2], 0., 0., 1.)

    # Sets up rotations of a side before drawing.
    def setUpSideRot(self):
        gl.glRotatef(self.sideRot[0], 1., 0., 0.)
        gl.glRotatef(self.sideRot[1], 0., 1., 0.)
        gl.glRotatef(self.sideRot[2], 0., 0., 1.)

    # Rotates the entire cube according to the mouse movement.
    def mouseRotateCube(self, x, y):
        rot = [0., 0., 0.]

        if x < self.oldMouseX:
            rot[1] = -self.rotVal
        elif x > self.oldMouseX:
            rot[1] = self.rotVal

        if y < self.oldMouseY:
            rot[0] = -self.rotVal
        elif y > self.oldMouseY:
            rot[0] = self.rotVal

        self.setRotation(rot)

    # Creates a rotation list. The rotation list contains the
    # id of all the boxes that should be rotated when rotating
    # one of the cube's sides.
    def createRotList(self, axis):
        if len(self.rotateList) == 0:
            if axis == "y":
                yVal = self.findYFromId(self.selectedBox)
                self.rotateList = list()
                for i in self:
                    if self.findYFromId(i) == yVal:
                        self.rotateList.append(i)

            elif axis == "x":
                xVal = self.findXFromId(self.selectedBox)
                self.rotateList = list()
                for i in self:
                    if self.findXFromId(i) == xVal:
                        self.rotateList.append(i)
            else:
                zVal = self.findZFromId(self.selectedBox)
                self.rotateList = list()
                for i in self:
                    if self.findZFromId(i) == zVal:
                        self.rotateList.append(i)

    # This method takes care of the animation of a rotating side
    # when the user uses the mouse to rotate a side.
    def mouseRotateSide(self, x, y):
        if self.moveDir == "x":
            # We are rotating around the y-axis by dragging the mouse in
            # the x-direction. This is along the horizontal line.
            self.createRotList("y")

            rotVal = self.rotVal

            if x - self.oldMouseX < 1:
                self.rotateSide("y", -rotVal)
            elif x - self.oldMouseX > 1:
                self.rotateSide("y", rotVal)

        elif self.moveDir == "y":
            # We are rotating around the y-axis or the z-axis depending on
            # the angle we are looking at the cube from. If we are looking
            # from the front or the back, rotate around the x-axis, if
            # we are looking from the left or right side, rotate around the
            # z-axis.
            rotVal = self.rotVal

            if round( self.rot[1] ) % 180 == 0:
                dir = "x"
                if round( self.rot[1] ) == 180:
                    rotVal = -rotVal

                self.createRotList("x")
            else:
                dir = "z"
                if round( self.rot[1] ) == 270:
                    rotVal = -rotVal

                self.createRotList("z")

            if y - self.oldMouseY < 1:
                self.rotateSide(dir, -rotVal)
            elif y - self.oldMouseY > 1:
                self.rotateSide(dir, rotVal)
        else:
            # We have not yet moved the mouse far enough to determine which
            # direction the user wants to rotate the side.
            diffX = abs(x - self.oldMouseX)
            diffY = abs(y - self.oldMouseY)

            if diffX < 10 and diffY < 10:
                return

            if diffX > diffY:
                self.moveDir = "x"
            elif diffY > diffX:
                self.moveDir = "y"

    # Callback from the main file for deciding between rotating the cube
    # or rotating one of the sides, depending on if there's a selected
    # box in the cube or not.
    def mouseMove(self, x, y):
        if self.selectedBox == -1:
            self.mouseRotateCube(x, y)
        else:
            self.mouseRotateSide(x, y)

        self.oldMouseX = x
        self.oldMouseY = y

    # Release of a mouse button. What to do?
    def mouseUp(self, x, y):
        # Check to see if we have rotated the side far enough to complete
        # the animation and register the rotation so that the cube has changed
        if len(self.rotateList) != 0:
            if self.sideRot[0] % 90 < 5 and self.sideRot[1] % 90 < 5 and self.sideRot[2] % 90 < 5:
                self.sideRot[0] = round(self.sideRot[0])
                self.sideRot[1] = round(self.sideRot[1])
                self.sideRot[2] = round(self.sideRot[2])

                self.registerSideRotation()

                return 1
            else:
                return self.snapSideRotation()

        return 1

    # A Mouse button has been clicked. Take proper action.
    def mouseDown(self, x, y):
        self.oldMouseX = x
        self.oldMouseY = y

        # Create the correct matrices for unprojection and set them up i matrices
        self.setUpCubeTransRot()
        modelView = gl.glGetDoublev(gl.GL_MODELVIEW_MATRIX)
        projectionView = gl.glGetDoublev(gl.GL_PROJECTION_MATRIX)
        viewport = gl.glGetIntegerv(gl.GL_VIEWPORT)

        # Invert y win-coord to match GL-coord and find 3d coords of the click
        y = viewport[3] - y
        z = gl.glReadPixels(x, y, 1, 1, gl.GL_DEPTH_COMPONENT, gl.GL_FLOAT)
        pos3dx, pos3dy, pos3dz = glu.gluUnProject(x, y, z, modelView, projectionView, viewport)

        # Bias allows us to click close to the boxs' edges
        bias = 0.01
        nSize = float(self.boxSize) / 2 + bias
        selectedBox = -1
        self.moveDir = ""

        # Test for which box has been clicked, if none of the clickables
        # we'll just rotate the entire cube around its own axes.
        for i in self.clickable:
            if (pos3dx >= self.boxes[i].pos[0] - nSize) and \
                (pos3dx <= self.boxes[i].pos[0] + nSize) and \
                (pos3dy >= self.boxes[i].pos[1] - nSize) and \
                (pos3dy <= self.boxes[i].pos[1] + nSize) and \
                (pos3dz >= self.boxes[i].pos[2] - nSize) and \
                (pos3dz <= self.boxes[i].pos[2] + nSize):
                selectedBox = i
                break

        self.selectedBox = selectedBox

    def zoomIn(self):
        self.pos[2] = self.pos[2] + 1

    def zoomOut(self):
        self.pos[2] = self.pos[2] - 1

    # Sets the rotation of the entire cube
    def setRotation(self, rot):
        if self.rot[0] + rot[0] <= 90. and self.rot[0] + rot[0] >= -90.:
            self.rot[0] = self.rot[0] + rot[0]
        self.rot[1] = (self.rot[1] + rot[1]) % 360
        self.rot[2] = (self.rot[2] + rot[2]) % 360

    def rotateSide(self, axis, value):
        # Limit rotation to only 90 degrees at a time, for convenience
        if axis == "x":
            self.sideRot[0] += value
            if abs(self.sideRot[0]) > 90:
                self.sideRot[0] = round(self.sideRot[0])
                return 1
        elif axis == "y":
            self.sideRot[1] += value
            if abs(self.sideRot[1]) > 90:
                self.sideRot[1] = round(self.sideRot[1])
                return 1
        elif axis == "z":
            self.sideRot[2] += value
            if abs(self.sideRot[2]) > 90:
                self.sideRot[2] = round(self.sideRot[2])
                return 1
        return 0

    # find previous box when rotated
    def prevId(self, i):
        pos = self.findRelativePos(i) 
        m = self.n - 1

        if self.sideRot[0] == 90.0:
            z = m - pos[1]
            pos[1] = pos[2]
            pos[2] = z
        elif self.sideRot[0] == -90.0:
            y = m - pos[2]
            pos[2] = pos[1]
            pos[1] = y
        elif self.sideRot[1] == 90.0:
            z = m - pos[0]
            pos[0] = pos[2]
            pos[2] = z
        elif self.sideRot[1] == -90.0:
            x = m - pos[2]
            pos[2] = pos[0]
            pos[0] = x
        elif self.sideRot[2] == 90.0:
            x = m - pos[1]
            pos[1] = pos[0]
            pos[0] = x
        elif self.sideRot[2] == -90.0:
            y = m - pos[0]
            pos[0] = pos[1]
            pos[1] = y

        return pos[0] + pos[1] * self.n + pos[2] * self.n**2

    # rotate all the boxes in the rotate list
    def registerSideRotation(self, solving=False):
        while len(self.rotateList) != 0:
            last = 0
            boxId = self.rotateList[0]

            while not last:
                self.rotateList.remove(boxId)
                prevBoxId = self.prevId(boxId)

                if prevBoxId in self.rotateList:
                    self.boxes[prevBoxId].rotateBox(self.sideRot)
                    relPos = self.findRelativePos(boxId)
                    self.boxes[prevBoxId].pos = self.relativeToAbsolutePos(relPos)

                    box = self.boxes[boxId]
                    self.boxes[boxId] = self.boxes[prevBoxId]
                    self.boxes[prevBoxId] = box

                else:
                    self.boxes[boxId].rotateBox(self.sideRot)
                    relPos = self.findRelativePos(boxId)
                    self.boxes[boxId].pos = self.relativeToAbsolutePos(relPos)
                    last = 1

                boxId = prevBoxId

        #self.sideRot = Quaternion()
        self.sideRot = [ 0., 0., 0. ]

        # if we're in auto-solve mode, we don't
        # need to check for correct solution
        if not solving:
            # check if cube is solved
            solver.loadCube(self)

            # sorry to say we "only" support solving
            # of 3x3x3 cubes at this time
            if self.n == 3:
                if solver.isSolved() and self.n == 3:
                    print "Solved"
                else:
                    left = len(solver.solveCube())
                    if (left == 1):
                        print "One move left!"
                    elif (left <= 10):
                        print "%d moves left" % left

    def snapSideRotation(self):
        # If the user released the mouse before a complete rotation,
        # rotate the side to a full 90 degrees in an animation
        if self.sideRot[0] != 0:
            if abs(self.sideRot[0]) < 45:
                if self.sideRot[0] > 0:
                    self.sideRot[0] = self.sideRot[0] - self.rotVal
                else:
                    self.sideRot[0] = self.sideRot[0] + self.rotVal
            else:
                if self.sideRot[0] > 0:
                    self.sideRot[0] = self.sideRot[0] + self.rotVal
                else:
                    self.sideRot[0] = self.sideRot[0] - self.rotVal

        elif self.sideRot[1] != 0:
            if abs(self.sideRot[1]) < 45:
                if self.sideRot[1] > 0:
                    self.sideRot[1] = self.sideRot[1] - self.rotVal
                else:
                    self.sideRot[1] = self.sideRot[1] + self.rotVal
            else:
                if self.sideRot[1] > 0:
                    self.sideRot[1] = self.sideRot[1] + self.rotVal
                else:
                    self.sideRot[1] = self.sideRot[1] - self.rotVal

        elif self.sideRot[2] != 0:
            if abs(self.sideRot[2]) < 45:
                if self.sideRot[2] > 0:
                    self.sideRot[2] = self.sideRot[2] - self.rotVal
                else:
                    self.sideRot[2] = self.sideRot[2] + self.rotVal
            else:
                if self.sideRot[2] > 0:
                    self.sideRot[2] = self.sideRot[2] + self.rotVal
                else:
                    self.sideRot[2] = self.sideRot[2] - self.rotVal

    # scrable the cube by sending a bunch of commands
    def scramble(self):
        actions = ('UL', 'UR', 'DL', 'DR', 'LU', 'LD', 'RU', 'RD', 'FC', 'FA', 'BC', 'BA')
        size = len(actions)
        
        random.seed()
        
        # 15..30 times seems like an ok amount
        times = random.randint(15, 30)
        for i in range(times):
            rand = random.randint(0, size-1)
            self.doAction(actions[rand], True, False)

    # Animates an automatic rotation of a side
    def animateAction(self, dir, angle, drawFunc):
        steps = angle / (24 * 1)
        while not self.rotateSide(dir, steps):
            drawFunc()
            yawn = 1. / 24.
            time.sleep(yawn / 2)

    # automated rotation actions
    def doAction(self, action, solving=False, drawFunc=False):
        # all these actions are "relative" to
        # the orange face (1, 0, 0)
        if action == 'UL':      # top left
            self.selectedBox = 0
            self.createRotList("y")
            if drawFunc:
                self.animateAction("y", -90., drawFunc)
            else:
                self.rotateSide("y", -90.)
            self.registerSideRotation(solving)
        elif action == 'UR':    # top right
            self.selectedBox = 0
            self.createRotList("y")
            if drawFunc:
                self.animateAction("y", 90., drawFunc)
            else:
                self.rotateSide("y", 90.)
            self.registerSideRotation(solving)
        elif action == 'DL':    # bottom left
            self.selectedBox = 6
            self.createRotList("y")
            if drawFunc:
                self.animateAction("y", -90., drawFunc)
            else:
                self.rotateSide("y", -90.)
            self.registerSideRotation(solving)
        elif action == 'DR':    # bottom right
            self.selectedBox = 6
            self.createRotList("y")
            if drawFunc:
                self.animateAction("y", 90., drawFunc)
            else:
                self.rotateSide("y", 90.)
            self.registerSideRotation(solving)
        elif action == 'LU':    # left up
            self.selectedBox = 0
            self.createRotList("z")
            if drawFunc:
                self.animateAction("z", 90., drawFunc)
            else:
                self.rotateSide("z", 90)
            self.registerSideRotation(solving)
        elif action == 'LD':    # left down
            self.selectedBox = 0
            self.createRotList("z")
            if drawFunc:
                self.animateAction("z", -90., drawFunc)
            else:
                self.rotateSide("z", -90)
            self.registerSideRotation(solving)
        elif action == 'RU':    # right up
            self.selectedBox = 18
            self.createRotList("z")
            if drawFunc:
                self.animateAction("z", 90., drawFunc)
            else:
                self.rotateSide("z", 90.)
            self.registerSideRotation(solving)
        elif action == 'RD':    # right down
            self.selectedBox = 18
            self.createRotList("z")
            if drawFunc:
                self.animateAction("z", -90., drawFunc)
            else:
                self.rotateSide("z", -90)
            self.registerSideRotation(solving)
        elif action == 'FC':    # front clockwise
            self.selectedBox = 2
            self.createRotList("x")
            if drawFunc:
                self.animateAction("x", -90., drawFunc)
            else:
                self.rotateSide("x", -90.)
            self.registerSideRotation(solving)
        elif action == 'FA':    # front counterclockwise
            self.selectedBox = 2
            self.createRotList("x")
            if drawFunc:
                self.animateAction("x", 90., drawFunc)
            else:
                self.rotateSide("x", 90.)
            self.registerSideRotation(solving)
        elif action == 'BC':    # back clockwise
            self.selectedBox = 0
            self.createRotList("x")
            if drawFunc:
                self.animateAction("x", -90., drawFunc)
            else:
                self.rotateSide("x", -90.)
            self.registerSideRotation(solving)
        elif action == 'BA':    # back counterclockwise
            self.selectedBox = 0
            self.createRotList("x")
            if drawFunc:
                self.animateAction("x", 90., drawFunc)
            else:
                self.rotateSide("x", 90.)
            self.registerSideRotation(solving)

