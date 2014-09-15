from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize
import os

coolPropSrcFolder = '/data/Workspace/Projects/SysMo/SmoFlow3D/coolprop/' 
smoFlowSrcFolder = '/data/Workspace/Projects/SysMo/SmoFlow3D/smoflow3d/com.sysmo.smoflow3d/src/'
smoFlowLibFolder = '/data/SysMo/SoftwareLibs/SmoFlow3D/'

os.environ['LD_RUN_PATH'] = smoFlowLibFolder
CXXFLAGS = ["-I" + os.path.abspath(os.path.join(smoFlowSrcFolder)),  
			"-I" + os.path.abspath(os.path.join(coolPropSrcFolder))]
LDFLAGS = ["-L" + smoFlowLibFolder]


smoMedia = Extension(
       "Media", 
       ['Media.pyx'],
       language="c++",
       extra_compile_args = CXXFLAGS,
       extra_link_args = LDFLAGS,
       libraries = ["SmoFlow"]
)

setup(
      name = "SmoFlow3D",
      ext_modules = cythonize([
           smoMedia
      ])
)

# Build with
# python setup.py build_ext --inplace
