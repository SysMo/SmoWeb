'''
Created on Apr 7, 2015

@author:  Atanas Pavlov
@copyright: SysMo Ltd, Bulgaria
'''
import os
from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize

# Build with
# python setup.py build_ext --inplace

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
CXXFLAGS = ["-I" + os.path.join(BASE_DIR, 'third-party')]
LDFLAGS = []

sources = [
		"math/Interpolators.cpp",
		"fatigue/StressCalculator.cpp",
		"SmoFlowCpp.pyx"
		]

SmoFlowCpp = Extension(
	'SmoFlowCpp',
	sources,
	language = 'c++',
	extra_compile_args = CXXFLAGS,
	extra_link_args = LDFLAGS,
	libraries = []
)

setup(
      name = "SmoFlowCpp",
      ext_modules = cythonize([
           SmoFlowCpp
      ])
)
