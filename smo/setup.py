'''
Created on May 2, 2015

@author:  Atanas Pavlov
@copyright: SysMo Ltd, Bulgaria
'''
import setuptools
from distutils.core import setup

setup(
	name = "smo",
	version = "1.0",
	description = "modules for creating engineering models",
	author = "Atanas Pavlov",
	author_email="nasko.js@gmail.com",
	package_dir={'smo': ''},
	packages = ['smo', 'smo.math', 'smo.mechanical', 'smo.util'],
	entry_points = {'console_scripts': [
			'damage = smo.mechanical.MultiaxialDamangeCalculator:main'
		]
	}
)
