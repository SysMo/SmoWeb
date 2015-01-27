import os
import glob
from fabric.api import run, sudo, env, cd, prefix, hosts
from fabric.api import local, lcd
from contextlib import contextmanager as _contextmanager
from fabric.contrib import files
from fabric.context_managers import shell_env

srvAddress = 'platform.sysmoltd.com' 

env.hosts = srvAddress
env.projectRoot = os.getcwd()
env.installDir = '/srv/SmoWeb/'
env.virtualBinDir = os.path.abspath(os.path.join(env.installDir, '../VirtualEnv/SmoWebPlatform/bin/'))
env.activate = 'source ' + os.path.join(env.virtualBinDir, 'activate')
env.projectModules = ['SmoWeb', 'SmoWebBase']
env.applicationModules = [
	'DataManagement',
	'ThermoFluids',
]
env.extraFolders = [
	'smo',
]
env.folderCopyList = [
	'manage.py',
] + env.projectModules \
  + env.applicationModules \
  + env.extraFolders

env.tempFolder = os.path.abspath(os.path.join(os.path.expanduser('~'), 'tmp'))
#######################################################################
@_contextmanager
def virtualenv():
	with prefix(env.activate):
		yield
#######################################################################
def deploy():
	"""
	Deploy the local site version on the server 
	"""
	print("Cleaning up old code and static files")
	local('rm -rf {0}/*'.format(os.path.join(env.installDir, 'Static')))
	local('rm -rf {0}/*'.format(os.path.join(env.installDir, 'Platform')))

	with virtualenv():
		local('python manage.py collectstatic -v0 --noinput', shell='bash')
		print("Collected static files")
		for module in env.folderCopyList:
			local('cp -r ./{0} {1}'.format(module, os.path.join(env.installDir, 'Platform')), shell='bash')
	local('unison -ignore "Name {*.pyc, *.sql*}" -ignore "Path Log/*" /srv/SmoWeb ssh://' + srvAddress + '//srv/SmoWeb')
	sudo('chown -R www-data:www-data /srv/SmoWeb ')
	sudo('service apache2 restart')
#######################################################################
def buildExtModules():
	"""
	Builds external C/C++ Cython modules used in the project
		* CoolProp interface module
		
	"""
	with virtualenv():
		print ("Building CoolProp extension module.....") 
		with lcd(os.path.join(env.projectRoot, 'smo', 'smoflow3d', 'CoolProp')):
			local('python setup.py build_ext --inplace', shell='bash')
		print ("CoolProp module built successfully!") 

#######################################################################
def syncVirtEnv():
	"""
	Synchronize local and remote python virtual environments
	"""
	local('unison -ignore "Name {*.pyc}" /srv/VirtualEnv/ ssh://' + srvAddress + '//srv/VirtualEnv')
	sudo('chown -R www-data:www-data /srv/SmoWeb ')
	sudo('service apache2 restart')
#######################################################################
def docs():
	"""
	Generate documentation for the project and for the individual apps and pages
	"""
	# Project documetation
	with lcd('doc'):
		local('make html')
	
	# Pages documetation
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

def convertToPng():
	"""
	Convert all .svg files for the project and for the individual apps and pages to .png files
	"""
	for app in env.applicationModules:
		srcFolder = os.path.join(env.projectRoot, app, 'static', app, 'img')
		if (os.path.isdir(srcFolder)):
			for sourceFilePath in glob.glob(os.path.join(srcFolder, '*.svg')):
				sDir, sName = os.path.split(sourceFilePath)
				sNameBase, sNameExt = os.path.splitext(sName)
				outputFilePath = os.path.abspath(os.path.join(sDir, sNameBase +'.png'))
				local('convert ' + sourceFilePath + ' -transparent white ' + outputFilePath)
				
def createThumbnails():
	"""
	Creates .png thumbnail files from all numerical model images.
	"""
	for app in env.applicationModules:
		srcFolder = os.path.join(env.projectRoot, app, 'static', app, 'img')
		if (os.path.isdir(srcFolder)):
			for sourceFilePath in glob.glob(os.path.join(srcFolder, '*.svg')):
				sDir, sName = os.path.split(sourceFilePath)
				sNameBase, sNameExt = os.path.splitext(sName)
				outputFilePath = os.path.abspath(os.path.join(sDir.replace('img', os.path.join('img', 'thumbnails')), 
												sNameBase + '_thumb.png'))
				local('convert ' + sourceFilePath + ' -thumbnail 170x160 -transparent white ' + outputFilePath)

#######################################################################
def installAptPackages():
	"""
	Install the packages from the Ubuntu repository, which are necessary for proper server functioning
	"""
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
		# The Mongo-DB database
		'mongodb',
		# RabbitMQ message broker
		'rabbitmq-server',
	]
	packageString = (" ").join(packageList)
	sudo('apt-get install {0}'.format(packageString))
	
	# Installing the packages necessary for building the matplotlib library
	sudo('apt-get build-dep python-matplotlib')
#######################################################################
def installPipPackages():
	"""
	Install the python packages from the Pip repository, which are necessary for proper server functioning. Alternatively use syncVirtEnv
	"""
	with virtualenv():
		packageList = [
			'argparse',
			'six',
			'python-dateutil',
			# Template library
			'jinja2',
			# Python wrappers for C/C++ 
			'cython',
			# Numerical libraries
			'numpy',
			'scipy',
			# Matplotlib pre-requisites
			'pytz',
			'tornado',
			'pyparsing',
			# Matplotlib
			'matplotlib',
			'mpld3',
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
			# PyMongo non-relational database
			'pymongo',
			# Celery distributed task queue
			'celery',
			# Documentation utility for python
			'sphinx'
		]
		for package in packageList:
			run('pip install {0}'.format(package))
#######################################################################
def installPySparse():
	"""
	Downloads, builds and installs PySparse (sparse linear solvers)
	"""
	with virtualenv(), cd(env.tempFolder):
		#if (not os.path.isdir(os.path.join(env.tempFolder, 'pysparse'))):
		if (not files.exists('pysparse')):
			run('git clone git://pysparse.git.sourceforge.net/gitroot/pysparse/pysparse')
		with cd('pysparse'):
			run('python setup.py build')
			run('python setup.py install')
#######################################################################
def installHdf():
	"""
	Builds and installs HDF5 (Hierarchical Data Format) library
	"""
	with virtualenv():
		with shell_env(CFLAGS="-I/usr/lib/openmpi/include/"):
			run('pip install h5py')
#######################################################################
def configureApache():
	"""
	Configures Apache (not functional)
	"""
	platformConfig="""
<VirtualHost *:80>
	ServerAdmin nasko.js@gmail.com
	ErrorLog ${APACHE_LOG_DIR}/SmowWeb_error.log
	CustomLog ${APACHE_LOG_DIR}/SmoWeb_access.log combined
	LogLevel info

	ServerName platform.sysmoltd.com
	ServerAlias platform.sysmoltd.com
	WSGIScriptAlias / /srv/SmoWeb/Platform/SmoWeb/wsgi.py
	WSGIDaemonProcess platform.sysmoltd.com python-path=/srv/SmoWeb/Platform:/srv/VirtualEnv/SmoWebPlatform/lib/python2.7/site-packages
	WSGIProcessGroup platform.sysmoltd.com
	WSGIApplicationGroup %{GLOBAL}
	<Directory /srv/SmoWeb/Platform/SmoWeb/ >
	  <Files wsgi.py>
	  	 Require all granted
	  </Files>
	</Directory>

	Alias /static/ /srv/SmoWeb/Static/
	<Directory /srv/SmoWeb/Static>
	    Require all granted
	</Directory>
</VirtualHost>
"""
#######################################################################
