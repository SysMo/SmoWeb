from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize
import os

print __file__
coolPropSrcFolder = os.path.dirname(os.path.realpath(__file__)) + '/../../../../../coolprop'
print coolPropSrcFolder
coolPropSrcFolder = os.path.abspath(coolPropSrcFolder)
print coolPropSrcFolder
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
