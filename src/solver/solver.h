#ifndef _SOLVER_H_
#define _SOLVER_H_

#include <Python.h>
#include <string>
#include <iostream>

#include "cubex.h"

using namespace std;

/* The cube */
Cubex cube;

/* Cube size */
int N = Cubex::N;

/* Helpers for returining true/false */
/* Removes those nasty memory leaks! */
PyObject *pyTrue() {
    PyObject *ret = Py_True;
    Py_INCREF(ret);
    return ret;
}
PyObject *pyFalse() {
    PyObject *ret = Py_False;
    Py_INCREF(ret);
    return ret;
}

/* Helper function from cubex.cpp */
void insertValues(string data)
{
    cube.cubeinit = false;
    for (int i = -1; i <= 1; i++) {
        for (int j = -1; j <= 1; j++) {
            *cube.face(j, 2, -i) = data.at(i*3+j+4)-48;
            *cube.face(-2, -i, -j) = data.at(i*3+j+13)-48;
            *cube.face(j, -i, -2) = data.at(i*3+j+22)-48;
            *cube.face(2, -i, j) = data.at(i*3+j+31)-48;
            *cube.face(-j, -i, 2) = data.at(i*3+j+40)-48;
            *cube.face(j, -2, i) = data.at(i*3+j+49)-48;
        }
    }
    cube.cubeinit = true;
}

/* Map Python-Cube id to C++-cube id */
/* This will map each box to multiple faces */
unsigned char idMap[] = {
     0,  9, 18,  1, 10, 19,  2, 11, 20, /* top */
     0,  1,  2,  3,  4,  5,  6,  7,  8, /* front */
     2, 11, 20,  5, 14, 23,  8, 17, 26, /* right */
    20, 19, 18, 23, 22, 21, 26, 25, 24, /* back */
    18,  9,  0, 21, 12,  3, 24, 15,  6, /* left */
     8, 17, 26,  7, 16, 25,  6, 15, 24  /* bottom */
};

#endif

