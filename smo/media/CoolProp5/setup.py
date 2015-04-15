from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize
import os

coolPropSrcFolder = '/data/Workspace/Projects/SysMo/SmoWeb/coolprop' 
CXXFLAGS = ["-I/" + coolPropSrcFolder + '/include']
LDFLAGS = ["-L/data/Workspace/Projects/SysMo/SmoWeb/coolprop/build/release/"]

pyCoolProp = Extension(
		"CoolProp",
		#['CoolProp.pyx', 'SmoFlowMediaExt.cpp'],
		['AbstractState.pyx'],
	   language="c++",
	   extra_compile_args = CXXFLAGS,
	   extra_link_args = LDFLAGS,
	   libraries = ["CoolProp"]
)

setup(
      name = "CoolProp",
      ext_modules = cythonize([
           pyCoolProp
      ])
)

# Build with
# python setup.py build_ext --inplace
