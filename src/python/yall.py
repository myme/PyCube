#!/usr/bin/env python

import quaternion as q

q1 = q.Quaternion((1., 0., 0., 0.))
q2 = q.fromEuler(90., 0., 0.)

print (q1 * q2).getAngleAxis()

