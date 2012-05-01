#!/usr/bin/env python

import os
from distutils.core import setup, Extension
from distutils.sysconfig import get_python_inc

source_dir = 'src'
solver_sources = ['solver.cpp', 'cubex.cpp']

cpp_dir = os.path.join(source_dir, 'solver')
python_dir = os.path.join(source_dir, 'python')

solver_mod = Extension( 'solver',
          sources = map(lambda x: os.path.join(cpp_dir, x), solver_sources)
        )

setup( name = "rubik",
        version = '1.0',
        author = "Martin Myrseth, Torkild Retvedt",
        author_email = "martinom@ifi.uio.no, torkildr@ifi.uio.no",
        description = "An OpenGL python and C implemented Rubik's cube.",
        package_dir = { '' : python_dir },
        py_modules = ['box', 'rubik', 'cube', 'quaternion', 'test'],
        ext_modules = [solver_mod])

