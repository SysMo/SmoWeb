import os
import glob
from fabric.api import run, sudo, env, cd, prefix, local, hosts
from contextlib import contextmanager as _contextmanager
from fabric.contrib import files
from fabric.context_managers import shell_env

srvAddress = 'platform.sysmoltd.com' 

env.hosts = srvAddress
env.projectRoot = os.getcwd()
env.installDir = '/srv/SmoWeb/'
env.virtualBinDir = os.path.abspath(os.path.join(env.installDir, '../VirtualEnv/SmoWebPlatform/bin/'))
env.activate = 'source ' + os.path.join(env.virtualBinDir, 'activate')
env.projectModule = 'SmoWeb'
env.applicationModules = [
	'DataManagement',
	'ThermoFluids',
]
env.extraFolders = [
	'smo',
	'templates'
]
env.folderCopyList = [
	'manage.py',
] + [env.projectModule] \
  + env.applicationModules \
  + env.extraFolders

env.tempFolder = os.path.abspath(os.path.join(os.path.expanduser('~'), 'tmp'))

@_contextmanager
def virtualenv():
	with prefix(env.activate):
		yield

#######################################################################
# Synchronize the local and remote virtual environments
#######################################################################
def syncVirtEnv():
	local('unison -ignore "Name {*.pyc}" /srv/VirtualEnv/ ssh://' + srvAddress + '//srv/VirtualEnv')
	sudo('chown -R www-data:www-data /srv/SmoWeb ')
	sudo('service apache2 restart')

#######################################################################
# Deploy the new Django version to the server
#######################################################################
def deploy():
	print("Cleaning up old code and static files")
	local('rm -rf {0}/*'.format(os.path.join(env.installDir, 'Static')))
	local('rm -rf {0}/*'.format(os.path.join(env.installDir, 'Platform')))

	with virtualenv():
		local('python manage.py collectstatic -v0 --noinput', shell='bash')
		print("Collected static files")
		for module in env.folderCopyList:
			local('cp -r ./{0} {1}'.format(module, os.path.join(env.installDir, 'Platform')), shell='bash')
	local('unison -ignore "Name {*.pyc}" /srv/SmoWeb ssh://' + srvAddress + '//srv/SmoWeb')
	sudo('chown -R www-data:www-data /srv/SmoWeb ')
	sudo('service apache2 restart')
		
	
#######################################################################
# Generate HTML files from restructuredText documents
#######################################################################
def rest2html():
	from docutils.core import publish_parts
	from docutils import io
	import codecs
	for app in env.applicationModules:
		markupFolder = os.path.join(env.projectRoot, app, 'templates', 'documentation')
		if (os.path.isdir(markupFolder)):
			for sourceFilePath in glob.glob(os.path.join(markupFolder, 'reStructuredText', '*.rst')):
				sourceFile = open(sourceFilePath, 'r')
				sDir, sName = os.path.split(sourceFilePath)
				sNameBase, sNameExt = os.path.splitext(sName)
				outputFilePath = os.path.abspath(os.path.join(sDir, '..', 'html', sNameBase+'.html'))
				result = publish_parts(
					source_class=io.FileInput,
					source = sourceFile,
					writer_name = 'html',				
					settings_overrides = {'math_output': 'MathJax'}
				)				
				with codecs.open(outputFilePath, 'w', 'utf-8') as fOut:
					fOut.write(result['html_body'])
				print ('Wrote output file: ' + outputFilePath)

#######################################################################
# Installing all the necessary apt packages on the server
#######################################################################
def installAptPackages():
	packageList = [
		# Revision control system
		'git',
		# Header files for compiling python modules
		'python-dev',
		# Fortran compiler
		'gfortran',
		# ATLAS linear algebra library
		'libatlas-dev',
		'libatlas-base-dev',
		# MPI libraries
		'mpi-default-dev',
		# Parallel version of HDF5
		'libhdf5-openmpi-7',
		# Sparse solvers
		'libsuitesparse-dev',
		# Apache web server
		'apache2',
		# Mod wsgi for running python web applications (necessary for Django)
		'libapache2-mod-wsgi',
		# Font library, necessary for matplotlib
		'libfreetype6-dev',
		# PNG read/write; necessary for matplotlib
		'libpng-dev',
		# necessary for matplotlib
		'libqhull-dev',
		'pkg-config',		
	]
	packageString = (" ").join(packageList)
	sudo('apt-get install {0}'.format(packageString))


#######################################################################
# Installing the necessary python virtualenv packages on the server
#######################################################################
def installPipPackages():
	with virtualenv():
		packageList = [
			'argparse',
			'six',
			'python-dateutil',
			# Python wrappers for C/C++ 
			'cython',
			# Numerical libraries
			'numpy',
			'scipy',
			# Matplotlib pre-requisites
			'pytz',
			'tornado',
			'pyparsing',
			# Finite volume solver
			'ez_setup',
			'fipy',
			# Application server 
			'django',
			'django-bootstrap-toolkit',
			'django-tastypie',
			'wsgiref',
			# System administration/deployment
			'fabric',
			
		]
		for package in packageList:
			run('pip install {0}'.format(package))
		
#@hosts('localhost')
def installPySparse():
	with virtualenv(), cd(env.tempFolder):
		#if (not os.path.isdir(os.path.join(env.tempFolder, 'pysparse'))):
		if (not files.exists('pysparse')):
			run('git clone git://pysparse.git.sourceforge.net/gitroot/pysparse/pysparse')
		with cd('pysparse'):
			run('python setup.py build')
			run('python setup.py install')
		
def installMatplotlib():
	""" Plotting library"""
	with virtualenv():
		with shell_env(CFLAGS="-I/usr/include/freetype2"):
			run('pip install matplotlib')
	
	
def installHdf():
	with virtualenv():
		with shell_env(CFLAGS="-I/usr/lib/openmpi/include/"):
			run('pip install h5py')
		