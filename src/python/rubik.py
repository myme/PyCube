#!/usr/bin/env python

import sys
import OpenGL.GL as gl
import OpenGL.GLU as glu
import OpenGL.GLUT as glut

from cube import *
import solver

width = 400
height = 400
winX = 200
winY = 200

actions = []
size = 3

help = """
 Welcome to Rubik's cube in Python
 
 key  action
-----------------------------------
 n    new cube (reset)
 s    solve cube (only for 3x3x3)
 a    abort solving
 r    randomize cube
 +    increase cube size
 -    decrease cube size
 h    this text
 q    quit

 mouse movements
-----------------------------------
 - click and drag edges/corners to rotate
 - center blocks cannot be rotated
 - click and drag outside cube to rotate cube

"""

# Sets up the OpenGL environment
def initGL():
    gl.glShadeModel(gl.GL_SMOOTH)
    gl.glClearColor(1.0, 1.0, 1.0, 0.0)

    gl.glEnable(gl.GL_DEPTH_TEST)
    gl.glDepthFunc(gl.GL_LESS)

    gl.glEnable(gl.GL_BLEND)
    gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

    gl.glLightfv(gl.GL_LIGHT1, gl.GL_AMBIENT, [.1, .1, .1, .1])
    gl.glLightfv(gl.GL_LIGHT1, gl.GL_DIFFUSE, [1., 1., 1., 0.])
    gl.glLightfv(gl.GL_LIGHT1, gl.GL_SPECULAR, [1., 1., 1., 0.])
    gl.glLightfv(gl.GL_LIGHT1, gl.GL_POSITION, [10., 5., 100., 1.])

    gl.glEnable(gl.GL_LIGHT1)
    gl.glEnable(gl.GL_LIGHTING)

    gl.glCullFace(gl.GL_BACK)

    gl.glHint(gl.GL_PERSPECTIVE_CORRECTION_HINT, gl.GL_NICEST)
    #gl.glHint(gl.GL_LINE_SMOOTH_HINT, gl.GL_NICEST)

    gl.glEnable(gl.GL_DITHER)
    gl.glEnable(gl.GL_CULL_FACE)
    #gl.glEnable(gl.GL_LINE_SMOOTH)

# Called every time the scene is resized
def resizeGLScene(width, height):
    if height == 0:
        height = 1

    gl.glViewport(0, 0, width, height)

    gl.glMatrixMode(gl.GL_PROJECTION)
    gl.glLoadIdentity()

    glu.gluPerspective(45., float(width) / float(height), 1., 100.)

    gl.glMatrixMode(gl.GL_MODELVIEW)
    gl.glLoadIdentity()

# Paints the scene
def drawGLScene():
    gl.glLoadIdentity()
    gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

    cube.drawCube()

    glut.glutSwapBuffers()

# Simple keyboard mappings
def keyboard(key, x, y):
    if key == 'q':
        print "Quitting..."
        sys.exit(0)
    elif key == 's':
        solver.loadCube(cube)
        if not solver.isSolved():
            globals()['actions'] = solver.solveCube()
            print "Solving %d steps" % len(globals()['actions'])
            solve(0)
    elif key == 'a':
        globals()['actions'] = []
    elif key == 'r':
        cube.scramble()
        drawGLScene()
    elif key == 'n':
        rot = globals()['cube'].rot
        globals()['cube'] = Cube(globals()['size'])
        globals()['actions'] = []
        globals()['cube'].rot = rot
        drawGLScene()
    elif key == '+':
        cube.zoomIn()
        drawGLScene()
    elif key == '-':
        cube.zoomOut()
        drawGLScene()
    elif key == 'h':
        print help

# Called ever half second while automatically solving the cube
def solve(num):
    actions = globals()['actions']
    if len(actions) > 0:
        cube.doAction(actions[0], True, drawGLScene)
        globals()['actions'] = actions[1:]
        glut.glutTimerFunc(500, solve, 0)
        drawGLScene() 

# Takes proper mouse movement action.
def mouseMove(x, y):
    cube.mouseMove(x, y)
    drawGLScene()

# Yay! The user has clicked somethin'.
def mouseClick(button, state, x, y):
    if state == glut.GLUT_UP:
        while 1:
            drawGLScene()
            if cube.mouseUp(x, y):
                break
        drawGLScene()
    else:
        cube.mouseDown(x, y)

def main(argv):
    # Initialize glut for a nice main window
    glut.glutInit(argv)
    glut.glutInitDisplayMode(glut.GLUT_DEPTH | glut.GLUT_RGB | glut.GLUT_DOUBLE)
    glut.glutInitWindowSize(width, height)
    glut.glutInitWindowPosition(winX, winY)

    # Create the main window title
    glut.glutCreateWindow("Rubik's Cube!")

    # Initialize OpenGL
    initGL()

    size = globals()['size']

    # Set up the size of the cube
    if len(argv) == 1:
        print "No size given, assuming 3"
    elif len(argv) == 2:
        size = int(argv[1])
        globals()['size'] = size
        print "Creating a cube of size %d*%d*%d" % (size, size, size)
    else:
        print "%s [size]" % argv[0]

    # Create the cube
    globals()['cube'] = Cube(size)

    # Register callback functions
    glut.glutDisplayFunc(drawGLScene)
    glut.glutReshapeFunc(resizeGLScene)
    glut.glutKeyboardFunc(keyboard)
    glut.glutMouseFunc(mouseClick)
    glut.glutMotionFunc(mouseMove)

    print help

    # Run the main event loop
    glut.glutMainLoop()

if __name__ == '__main__':
    main(sys.argv)

