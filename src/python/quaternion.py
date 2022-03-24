from numpy import *
from math import *

def length(v):
    """Get the length of a vector.
    """
    return sqrt( v[0]**2 + v[1]**2 + v[2]**2 )

def vecNormalize(v):
    """Normalize a vector.
    """
    len = length(v)
    return ( asarray(v) / len )

def vectDotProduct(v1, v2):
    """Calculates the dot product of two vectors.
    """
    return ( v1[1] * v2[2] - v1[2] * v2[1],
             v1[2] * v2[0] - v1[0] * v2[2],
             v1[0] * v2[1] - v1[1] * v2[0] )

def fromXYZR( v, r ):
    """Creates a quaternion object instance from a rotation
    around a vector.
    """
    r = radians(r * 0.5)
    v = vecNormalize(asarray(v))

    sinR = sin(r)

    return Quaternion( [cos(r), v[0]*sinR, v[1]*sinR, v[2]*sinR] )

def fromEuler( x=0, y=0, z=0 ):
    """Creates a quaternion object instance from a rotation
    with Euler angles.
    """
    if x:
        base = fromXYZR( [1, 0, 0], x )
        if y:
            base = base * fromXYZR( [0, 1, 0], y )
        if z:
            base = base * fromXYZR( [0, 0, 1], z )
    elif y:
        base = fromXYZR( [0, 1, 0], y )
        if z:
            base = base * fromXYZR( [0, 0, 1], z )
    else:
        base = fromXYZR( [0, 0, 1], z )

    return base

class Quaternion:
    """Quaternion class implementing methods useful for OpenGL
    redering.
    """
    def __init__(self, elements=[1., 0., 0., 0.]):
        self.elements = asarray(elements, dtype=float)
        self.normalize()

    def __mul__(self, rhs):
        """Quaternion multiplication is the equivalence of stacking
        rotations to form a single rotation around an arbitrary axis.
        """
        w1, x1, y1, z1 = self.elements
        w2, x2, y2, z2 = rhs.elements

        w = w1*w2 - x1*x2 - y1*y2 - z1*z2
        x = w1*x2 + x1*w2 + y1*z2 - z1*y2
        y = w1*y2 + y1*w2 + z1*x2 - x1*z2
        z = w1*z2 + z1*w2 + x1*y2 - y1*x2

        return self.__class__( [w, x, y, z] )

    def __getitem__(self, index):
        return self.elements[index]

    def normalize(self):
        """Normalize the quaternion to make sure we're always dealing
        with a unit quaternion. Meaning a vector starting in the origin
        and ending in the coordinate specified by the vector [x, y, z]
        has length 1.
        """
        w, x, y, z = self.elements
        mag2 = ( w**2 + x**2 + y**2 + z**2 )
        if ( fabs( mag2 - 1.0 ) > 0.0000001 ):
            mag = sqrt(mag2)
            self.elements /= mag

    def getConjugate(self):
        """Since we're dealing with unit quaternions the inverse is equal
        to the conjugate of the quaternion. Don't ask me why.
        """
        w, x, y, z = self.elements
        return self.__class__( [w, -x, -y, -z] )

    def vertex(self, vect):
        vect = vecNormalize(vect)
        vectQuat = self.__class__( [0.0, vect[0], vect[1], vect[2]] )

        resQuat = vectQuat * self.getConjugate()
        resQuat = self * resQuat

        return (resQuat.elements[1], resQuat.elements[2], resQuat.elements[3])

    def matrix(self):
        w, x, y, z = self.elements

        return array([
            [ 1-2*y*y-2*z*z, 2*x*y+2*w*z, 2*x*z-2*w*y, 0.0],
            [ 2*x*y-2*w*z, 1-2*x*x-2*z*z, 2*y*z+2*w*x, 0.0],
            [ 2*x*z+2*w*y, 2*y*z-2*w*x, 1-2*x*x-2*y*y, 0.0],
            [ 0.0,0.0,0.0,1],
        ])

    def rotateEuler(self, rot):
        self.elements = (fromEuler( rot[0], rot[1], rot[2] ) * self).elements

    def rotateVect(self, vect, rot):
        self.elements = (fromXYZR( vect, rot ) * self).elements

    def rotate90(self, dir):
        if dir == "left":
            vect = ( 0., 1., 0. )
            angle = -90.
        elif dir == "right":
            vect = ( 0., 1., 0. )
            angle = 90.
        elif dir == "up":
            vect = ( 1., 0., 0. )
            angle = -90.
        elif dir == "down":
            vect = ( 1., 0., 0. )
            angle = 90.

        self.elements = (fromXYZR( vect, angle ) * self).elements

    def getAngleAxis(self):
        w, x, y, z = self.elements
        try:
            aw = acos(w)
        except ValueError:
            # catches errors where w == 1.00000000002
            aw = 0.0
        scale = sin(aw)
        if not scale:
            return (0.0,0.0,1.0,0.0)

        return (x / scale, y / scale, z / scale, degrees(2 * aw) )

    def slerp( self, other, fraction = 0, minimalStep= 0.0001):
        cosValue = sum(self.elements * other.elements)
        # if the cosValue is negative, use negative target and cos values?
        # not sure why, it's just done this way in the sample code
        if cosValue < 0.0:
            cosValue = -cosValue
            target = -other.elements
        else:
            target = other.elements[:]
        if (1.0- cosValue) > minimalStep:
            # regular spherical linear interpolation
            angle = acos( cosValue )
            angleSin = sin( angle )
            sourceScale = sin( (1.0- fraction) * angle ) / angleSin
            targetScale = sin( fraction * angle ) / angleSin
        else:
            sourceScale = 1.0-fraction
            targetScale = fraction
        return self.__class__( (sourceScale * self.elements)+(targetScale * target) )


if __name__ == '__main__':
    q = Quaternion()
    print(q.vertex( (0., 0., 1.) ))

    q.rotate90("left")
    print(q.vertex( (0., 0., 1.) ))
