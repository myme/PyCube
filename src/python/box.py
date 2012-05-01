import OpenGL.GL as gl
from math import *

from quaternion import *

def colorFromCoord(c):
    if c[0] >  0.5: return 3
    if c[0] < -0.5: return 5
    if c[1] >  0.5: return 1
    if c[1] < -0.5: return 6
    if c[2] >  0.5: return 2
    if c[2] < -0.5: return 4
    return 0

def getOpposite(num):
    if num == 1: return 6
    if num == 2: return 4
    if num == 3: return 5
    if num == 4: return 2
    if num == 5: return 3
    if num == 6: return 1

# The boxes of the cube should be looked upon as "stupid" or "dumb"
# boxes, only knowing their own rotation around their own
# axes and their own position relative to the cube center.
class Box:
    def __init__(self, listId, id, pos):
        # The listId is given by the parent cube object and refers
        # to the displaying routine compiled on the GPU for drawing
        # single boxes. A compiled routine is quicker than drawing
        # every face on demand each time a box is repainted (redrawn).
        self.listId = listId
        self.pos = pos

        self.id = id

        self.rot = Quaternion()
        
        # which side points where
        self.side = [1, 2, 3, 4, 5, 6]

    # Big Whoop.
    def drawBox(self):
        gl.glTranslatef(self.pos[0], self.pos[1], self.pos[2])

        x, y, z, r = self.rot.getAngleAxis()
        gl.glRotatef( r, x, y, z )

        gl.glCallList(self.listId)

    # Self explanatory
    def rotateBox(self, rot):
        self.rot.rotateEuler( rot )

        top = colorFromCoord(self.rot.vertex( [0., 1., 0.] ))
        front = colorFromCoord(self.rot.vertex( [0., 0., 1.] ))
        right = colorFromCoord(self.rot.vertex( [1., 0., 0.] ))


        self.side[top-1] = 1
        self.side[front-1] = 2
        self.side[right-1] = 3
        self.side[getOpposite(front)-1] = 4
        self.side[getOpposite(right)-1] = 5
        self.side[getOpposite(top)-1] = 6

# This is the drawing routine of a single box. It should be called from
# the parent cube object and the returned listId should be given to every
# new instance of a box object. All the boxes in a cube should have the
# same listId as all the boxes are in principal equal in design. If, however,
# there arises a reason for one of the boxes (or more) to have different
# color or size a new display list will have to be created for these
# "special" boxes. This is achieved with a new call to "buildBox()", but
# it's clearly not recommended as the rest of the design relies on identical
# boxes.
def buildBox(size=1,
        topColor=(1.,1.,1.,1.),
        bottomColor=(0.,1.,0.,1.),
        frontColor=(0.,0.,1.,1.),
        backColor=(1.,0.,0.,1.),
        leftColor=(1.,1.,0.,1.),
        rightColor=(1.,.3,0.,1.),
        lineColor=(0.,0.,0.,1.)
        ):

    listId = gl.glGenLists(1)

    # Offset variables to make vertex positioning easier.
    # This implementation only allows square boxes.
    o1 = (float(size) / 2)
    o2 = -1 * o1

    o1 -= 0.01
    o2 += 0.01

    gl.glNewList(listId, gl.GL_COMPILE)

    gl.glBegin(gl.GL_QUADS)

    ambient = [0.6, 0.6, 0.6, 0.0]
    specular = [0.3, 0.3, 0.3, 0.0]
    shininess = [1.0]

    # Top of box
    #gl.glColor4fv(topColor)

    gl.glMaterialfv(gl.GL_FRONT, gl.GL_AMBIENT, ambient)
    gl.glMaterialfv(gl.GL_FRONT, gl.GL_DIFFUSE, topColor)
    gl.glMaterialfv(gl.GL_FRONT, gl.GL_SPECULAR, specular)
    gl.glMaterialfv(gl.GL_FRONT, gl.GL_SHININESS, shininess)

    gl.glNormal3f(0., 1., 0.)

    gl.glVertex3f(o2, o1, o1)
    gl.glVertex3f(o1, o1, o1)
    gl.glVertex3f(o1, o1, o2)
    gl.glVertex3f(o2, o1, o2)

    # Bottom of box
    #gl.glColor4fv(bottomColor)

    gl.glMaterialfv(gl.GL_FRONT, gl.GL_AMBIENT, [0., 0.3, 0., 0.])
    gl.glMaterialfv(gl.GL_FRONT, gl.GL_DIFFUSE, bottomColor)
    gl.glMaterialfv(gl.GL_FRONT, gl.GL_SPECULAR, specular)
    gl.glMaterialfv(gl.GL_FRONT, gl.GL_SHININESS, shininess)

    gl.glNormal3f(0., -1., 0.)

    gl.glVertex3f(o2, o2, o2)
    gl.glVertex3f(o1, o2, o2)
    gl.glVertex3f(o1, o2, o1)
    gl.glVertex3f(o2, o2, o1)

    # Front of box
    #gl.glColor4fv(frontColor)

    gl.glMaterialfv(gl.GL_FRONT, gl.GL_AMBIENT, [0., 0., 0.3, 0.])
    gl.glMaterialfv(gl.GL_FRONT, gl.GL_DIFFUSE, frontColor)
    gl.glMaterialfv(gl.GL_FRONT, gl.GL_SPECULAR, specular)
    gl.glMaterialfv(gl.GL_FRONT, gl.GL_SHININESS, shininess)

    gl.glNormal3f(0., 0., 1.)

    gl.glVertex3f(o2, o1, o1)
    gl.glVertex3f(o2, o2, o1)
    gl.glVertex3f(o1, o2, o1)
    gl.glVertex3f(o1, o1, o1)

    # Back of box
    #gl.glColor4fv(backColor)

    gl.glMaterialfv(gl.GL_FRONT, gl.GL_AMBIENT, [0.3, 0., 0., 0.])
    gl.glMaterialfv(gl.GL_FRONT, gl.GL_DIFFUSE, backColor)
    gl.glMaterialfv(gl.GL_FRONT, gl.GL_SPECULAR, specular)
    gl.glMaterialfv(gl.GL_FRONT, gl.GL_SHININESS, shininess)

    gl.glNormal3f(0., 0., -1.)

    gl.glVertex3f(o1, o1, o2)
    gl.glVertex3f(o1, o2, o2)
    gl.glVertex3f(o2, o2, o2)
    gl.glVertex3f(o2, o1, o2)

    # Left of box
    #gl.glColor4fv(leftColor)

    gl.glMaterialfv(gl.GL_FRONT, gl.GL_AMBIENT, [0.3, 0.3, 0., 0.])
    gl.glMaterialfv(gl.GL_FRONT, gl.GL_DIFFUSE, leftColor)
    gl.glMaterialfv(gl.GL_FRONT, gl.GL_SPECULAR, specular)
    gl.glMaterialfv(gl.GL_FRONT, gl.GL_SHININESS, shininess)

    gl.glNormal3f(-1., 0., 0.)

    gl.glVertex3f(o2, o1, o1)
    gl.glVertex3f(o2, o1, o2)
    gl.glVertex3f(o2, o2, o2)
    gl.glVertex3f(o2, o2, o1)

    # Right of box
    #gl.glColor4fv(rightColor)

    gl.glMaterialfv(gl.GL_FRONT, gl.GL_AMBIENT, [0.3, 0.15, 0., 0.])
    gl.glMaterialfv(gl.GL_FRONT, gl.GL_DIFFUSE, rightColor)
    gl.glMaterialfv(gl.GL_FRONT, gl.GL_SPECULAR, specular)
    gl.glMaterialfv(gl.GL_FRONT, gl.GL_SHININESS, shininess)

    norm = vecNormalize(vectDotProduct([o1, o1, o2], [o1, o1, o1]))
    gl.glNormal3f(1., 0., 0.)

    gl.glVertex3f(o1, o1, o2)
    gl.glVertex3f(o1, o1, o1)
    gl.glVertex3f(o1, o2, o1)
    gl.glVertex3f(o1, o2, o2)

    gl.glEnd()
    # Done drawing planes of the box

    # Create black outlines
    gl.glColor4fv(lineColor)
    lw = float(size * 3)
    gl.glLineWidth(lw)

    gl.glMaterialfv(gl.GL_FRONT, gl.GL_AMBIENT, [0., 0., 0., 0.])
    gl.glMaterialfv(gl.GL_FRONT, gl.GL_DIFFUSE, lineColor)
    gl.glMaterialfv(gl.GL_FRONT, gl.GL_SPECULAR, [0.1, 0.1, 0.1, 0.1])
    gl.glMaterialfv(gl.GL_FRONT, gl.GL_SHININESS, [0.1])

    # Top outline
    gl.glBegin(gl.GL_LINE_LOOP)
    gl.glVertex3f(o2, o1, o2)
    gl.glVertex3f(o1, o1, o2)
    gl.glVertex3f(o1, o1, o1)
    gl.glVertex3f(o2, o1, o1)
    gl.glEnd()

    # Bottom outline
    gl.glBegin(gl.GL_LINE_LOOP)
    gl.glVertex3f(o2, o2, o1)
    gl.glVertex3f(o1, o2, o1)
    gl.glVertex3f(o1, o2, o2)
    gl.glVertex3f(o2, o2, o2)
    gl.glEnd()

    # Front outline
    gl.glBegin(gl.GL_LINE_LOOP)
    gl.glVertex3f(o2, o1, o1)
    gl.glVertex3f(o2, o2, o1)
    gl.glVertex3f(o1, o2, o1)
    gl.glVertex3f(o1, o1, o1)
    gl.glEnd()

    # Back outline
    gl.glBegin(gl.GL_LINE_LOOP)
    gl.glVertex3f(o1, o1, o2)
    gl.glVertex3f(o1, o2, o2)
    gl.glVertex3f(o2, o2, o2)
    gl.glVertex3f(o2, o1, o2)
    gl.glEnd()

    # Left outline
    gl.glBegin(gl.GL_LINE_LOOP)
    gl.glVertex3f(o2, o1, o2)
    gl.glVertex3f(o2, o1, o1)
    gl.glVertex3f(o2, o2, o1)
    gl.glVertex3f(o2, o2, o2)
    gl.glEnd()

    # Right outline
    gl.glBegin(gl.GL_LINE_LOOP)
    gl.glVertex3f(o1, o1, o1)
    gl.glVertex3f(o1, o1, o2)
    gl.glVertex3f(o1, o2, o2)
    gl.glVertex3f(o1, o2, o1)
    gl.glEnd()

    gl.glEndList()

    return listId

