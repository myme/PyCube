#include "solver.h"

/*
 * A wrapper for the C++ class Cubex (Cubex written by Eric Dietz)
 * Written in C++ against Python C-API for flexebility
 *
 * Source code can be found at: http://www.wrongway.org/work/cubex.zip
 */

/* More or less just to see what we can access from Python */
static PyObject *init( PyObject * self, PyObject * args ); 
static PyObject *solveCube( PyObject * self, PyObject * args ); 
static PyObject *loadCube( PyObject * self, PyObject * args ); 
static PyObject *isSolved( PyObject * self, PyObject * args ); 
 
/* Python module stuff */
PyDoc_STRVAR( solver_module__doc__, "A Rubik's cube solver wrapper written in C++" ); 
PyDoc_STRVAR( solver__doc__, "A Rubik's cube solver wrapper written in C++" ); 

/* Methods accessable from module */
static PyMethodDef SolverMethods[] = {
    { "init", init, METH_VARARGS, solver__doc__ }, 
    { "solveCube", solveCube, METH_VARARGS, solver__doc__ }, 
    { "loadCube", loadCube, METH_VARARGS, solver__doc__ }, 
    { "isSolved", isSolved, METH_VARARGS, solver__doc__ }, 
    { NULL, NULL, 0, NULL } 
}; 
 
/* Setup method for the module */
PyMODINIT_FUNC initsolver( void ) 
{ 
    (void) Py_InitModule3( "solver", SolverMethods, solver_module__doc__ ); 
} 

/* Init method, not _really_ neccassary */
PyObject *init( PyObject * self, PyObject * args )
{
    Py_DECREF(args);

    /* Starting position */
    insertValues("111111111222222222333333333444444444555555555666666666");
    
    if (cube.cubeinit) return pyTrue();
    else return pyFalse();
}

/* Check if cube is solved */
PyObject *isSolved( PyObject * self, PyObject * args )
{
    Py_DECREF(args);

    if ( cube.IsSolved() ) return pyTrue();
    else return pyFalse();
}

/* Load cube from Python into the Cubex class */
PyObject *loadCube ( PyObject * self, PyObject * args )
{
    /* Python object of type Cube */
    PyObject *pyCube;
    PyArg_ParseTuple(args, "O", &pyCube);

    /* Get boxes list */
    PyObject *boxes = PyObject_GetAttrString(pyCube, "boxes");

    /* We only support 3^3 cubes at this time, get of our back! */
    if (PyList_Size(boxes) != N*N*N) {
        Py_DECREF(boxes);
        return pyFalse();
    }
    
    /* Number of faces */
    int length = N*N*6;
    char values[length];
    
    int level = 0;
    for ( int i = 0; i < length; i++ ) {
        /* New side */
        if (( i % 9 == 0 ) && ( i != 0 )) level++;
        
        /* Figure out how the box is oriented */
        PyObject *item = PyList_GetItem(boxes, idMap[i]);
        Py_INCREF(item);

        PyObject *sides = PyObject_GetAttrString( item, "side" );
        /* Grab orientation for this side */
        int side = PyInt_AsLong( PyList_GetItem(sides, level) );
        
        /* Making a Cubex-compatable string */
        values[i] = ((char) side + '0');

        Py_DECREF(sides);
    }
    
    /* Insert the values into the Cubex class */
    insertValues( string(values, length) );

    Py_DECREF(boxes);    
    return pyTrue();
}

/* Solve the cube loaded into the Cubex class */
PyObject *solveCube( PyObject * self, PyObject * args )
{
    /* Try to solve cube */
    if (cube.SolveCube() != 0) {
        /* Return empty list on failure */
        return PyList_New(0);
    }
    
    /* Grab solution */
    char *solution = (char*) cube.solution.c_str();
    char move[3] = {'\0', '\0', '\0'};
    
    /* Empty list */
    PyObject *list = PyList_New(0);
    
    if ( strlen(solution) > 0 ) do {
        /* Get next move from string (two chars) */
        move[0] = (solution++)[0];
        move[1] = (solution++)[0];

        /* Append this move to the list */
        PyObject *pyString = PyString_FromString(move);
        PyList_Append( list, pyString );
    } while ( (++solution)[0] != '\0' );

    Py_DECREF(args);
    return list;
}

