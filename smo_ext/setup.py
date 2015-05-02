'''
Created on Apr 7, 2015

@author:  Atanas Pavlov
@copyright: SysMo Ltd, Bulgaria
'''
import os, sys
import numpy as np
from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize

# Build with
# python setup.py build_ext --inplace

commonIncludeDirs = ['.', np.get_include()]

DEBUG = False
CXXFLAGS = []
LDFLAGS = []


# MSVC options
if sys.platform=='win32' or os.name=='nt':
	CXXFLAGS += ['/EHsc']
else:
	opt = "-Wall "
	if DEBUG:
		opt += " -g -DDEBUG "
	else:
		opt += " -O3 "
		
	os.environ['OPT'] = opt

mathExtension = Extension(
	'smo_ext.Math', sources = [	
		'math/Interpolators.cpp',
		'math/ArrayInterfaceTest.cpp',
		'Math.pyx'
	],
	language = 'c++',
	include_dirs = commonIncludeDirs,
	extra_compile_args = CXXFLAGS,
	extra_link_args = LDFLAGS,
	libraries = []
)

mechExtension = Extension(
	'smo_ext.Mechanical', sources = [	
		"mechanical/RainflowCounter.cpp",
		"mechanical/StressTensorCalculator.cpp",
		'Mechanical.pyx'
	],
	language = 'c++',
	include_dirs = commonIncludeDirs,
	extra_compile_args = CXXFLAGS,
	extra_link_args = LDFLAGS,
	libraries = []
)

setup(
      name = "smo_ext",
      version = "1.0",
      description = "Cython extension modules for speeding up computation",
      author = "Atanas Pavlov",
      author_email="nasko.js@gmail.com",
      package_dir={'smo_ext': ''},
      packages = ['smo_ext'],
      ext_modules = cythonize([mathExtension, mechExtension])
)
