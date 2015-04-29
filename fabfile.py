import os
import glob
from fabric.api import run, sudo, env, cd, prefix, hosts
from fabric.api import local, lcd
from contextlib import contextmanager as _contextmanager
from fabric.contrib import files
from fabric.context_managers import shell_env
from smo.util.writers import SmoHTMLWriter

srvAddress = 'platform.sysmoltd.com' 

env.hosts = srvAddress
env.projectRoot = os.getcwd()
env.installDir = '/srv/SmoWeb/'
env.virtualBinDir = os.path.abspath(os.path.join(env.installDir, '../VirtualEnv/SmoWebPlatform/bin/'))
env.activate = 'source ' + os.path.join(env.virtualBinDir, 'activate')
env.projectModules = ['SmoWeb']
env.applicationModules = [
#	'DataManagement',
	'ThermoFluids',
	'SmoWebBase',
	'BioReactors'
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
		
def needsUpdate(source, destination):
	# does destination exist?
	if (not os.path.isfile(destination)):
		return True
	if (not isinstance(source, (list, tuple))):
		source = [source]
	for f in source:
		if (os.stat(f).st_mtime > os.stat(destination).st_mtime):
			return True
	return False
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
	local('unison -ignore "Name {*.pyc, *.sql*}" -ignore "Path Log/*" -ignore "Path Media/*" /srv/SmoWeb ssh://' + srvAddress + '//srv/SmoWeb')
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
		with lcd(os.path.join(env.projectRoot, 'smo', 'media', 'CoolProp')):
			local('python setup.py build_ext --inplace', shell='bash')
		print ("CoolProp module built successfully!") 
		with lcd(os.path.join(env.projectRoot, 'smo', 'media', 'CoolProp5')):
			local('python setup.py build_ext --inplace', shell='bash')
		print ("CoolProp5 module built successfully!") 

#######################################################################
def syncVirtEnv():
	"""
	Synchronize local and remote python virtual environments
	"""
	local('unison -ignore "Name {*.pyc}" /srv/VirtualEnv/ ssh://' + srvAddress + '//srv/VirtualEnv')
	sudo('chown -R www-data:www-data /srv/SmoWeb ')
	sudo('service apache2 restart')
#######################################################################
def rest2html():
	"""
	Generate documentation for the project and for the individual apps and pages
	"""
	# Project documetation - public
	with lcd(os.path.join('doc', 'public')):
		local('make html')

	
	# Project documetation - internal
	with lcd(os.path.join('doc', 'internal')):
		local('make html')
	
	# Pages documetation
	from docutils.core import publish_parts
	from docutils import io
	import codecs
	for app in env.applicationModules:
		markupFolder = os.path.join(env.projectRoot, app, 'templates', app, 'restblocks')
		if (os.path.isdir(markupFolder)):
			for sourceFilePath in glob.glob(os.path.join(markupFolder, 'reStructuredText', '*.rst')):
				sourceFile = open(sourceFilePath, 'r')
				sDir, sName = os.path.split(sourceFilePath)
				sNameBase, sNameExt = os.path.splitext(sName)
				outputFilePath = os.path.abspath(os.path.join(sDir, '..', 'html', sNameBase+'.html'))
				result = publish_parts(
					source_class=io.FileInput,
					source = sourceFile,
# 					writer_name = 'html',
					writer = SmoHTMLWriter(),				
					settings_overrides = {'math_output': 'MathJax'}
				)				
				with codecs.open(outputFilePath, 'w', 'utf-8') as fOut:
					fOut.write(result['html_body'])
				print ('Wrote output file: ' + outputFilePath)
#######################################################################

def generatePng():
	"""
	Convert all .svg files in the static folders within the project to .png files
	"""
	for app in env.applicationModules:
		srcFolder = os.path.join(env.projectRoot, app, 'static')
		for subFolderTuple in os.walk(srcFolder):
			subFolderPath = subFolderTuple[0]
			for sourceFilePath in glob.glob(os.path.join(subFolderPath, '*.svg')):
				sDir, sName = os.path.split(sourceFilePath)
				sNameBase, sNameExt = os.path.splitext(sName)
				outputFilePath = os.path.abspath(os.path.join(sDir, sNameBase +'.png'))
				if needsUpdate(sourceFilePath, outputFilePath):
					local('convert ' + sourceFilePath + ' -transparent white ' + outputFilePath)
				else:
					print('{} is up to date'.format(outputFilePath))
				
	srcFolder = os.path.join(env.projectRoot, 'doc', 'public', 'source')
	for subFolderTuple in os.walk(srcFolder):
		subFolderPath = subFolderTuple[0]
		for sourceFilePath in glob.glob(os.path.join(subFolderPath, '*.svg')):
			sDir, sName = os.path.split(sourceFilePath)
			sNameBase, sNameExt = os.path.splitext(sName)
			outputFilePath = os.path.abspath(os.path.join(sDir, sNameBase +'.png'))
			if needsUpdate(sourceFilePath, outputFilePath):
				local('convert ' + sourceFilePath + ' -transparent white ' + outputFilePath)
			else:
				print('{} is up to date'.format(outputFilePath))
				
def generateThumbnails():
	"""
	Creates .png thumbnail files from all .png module images.
	"""
	for app in env.applicationModules:
		srcFolder = os.path.join(env.projectRoot, app, 'static', app, 'img', 'ModuleImages')
		if (os.path.isdir(srcFolder)):
			for sourceFilePath in glob.glob(os.path.join(srcFolder, '*.png')):
				sDir, sName = os.path.split(sourceFilePath)
				sNameBase, sNameExt = os.path.splitext(sName)
				outputFilePath = os.path.abspath(os.path.join(sDir, 'thumbnails',
												sNameBase + '_thumb.png'))
				if needsUpdate(sourceFilePath, outputFilePath):
					local('convert ' + sourceFilePath + ' -thumbnail 150x100 ' + outputFilePath)
				else:
					print('{} is up to date'.format(outputFilePath))

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
		# Sundials solvers
		'libsundials-serial-dev',
		'libsuperlu3-dev',
		# Language agnostic inter-process communication via messages (structured data)
		'protobuf-compiler',
		'thrift-compiler',
		'libevent-dev',
		#libboost-dev libboost-test-dev libboost-program-options-dev libboost-system-dev libboost-filesystem-dev libevent-dev automake libtool flex bison pkg-config libssl-dev
		# graph visualization
		'libgraphviz-dev',
		# mesh generator
		'gmsh',
	]
	packageString = (" ").join(packageList)
	sudo('apt-get install {0}'.format(packageString))
	
	# Installing the packages necessary for building the matplotlib library
	sudo('apt-get build-dep python-matplotlib')
	sudo('apt-get install libqhull-dev')
#######################################################################
def installPipPackages():
	"""
	Install the python packages from the Pip repository, which are necessary for proper server functioning. Alternatively use syncVirtEnv
	"""
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
		# Blist, provides some data structures based on B-trees
		# like improved list, sortedlist, sortedset etc.
		'blist',
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
		'sphinx',
		# Utilities to read/write Excel files
		'xlrd',
		'xlwt',
		'openpyxl',
		'xlsxwriter',
		# Data processing utilities
		'numexpr',
		'tables', # PyTables
		'pandas', # Pandas
		# IPC
		'thrift',
		# graph visualization
		'pygraphviz',
		# Flower: Real-time Celery web-monitor
		'flower'
	]
	with virtualenv():
		with shell_env(CFLAGS="-I/usr/lib/openmpi/include/"): # Necessary for HDF5 based packages
			for package in packageList:
				run('pip install {0}'.format(package))
#######################################################################
def listExtraPyPackages():
	"""
	List of all extra python packages
	"""
	print ("""Extra python packages:
	pydelay - for solving a system of delay differential equations (DDEs)
	""")

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
			
def installAssimulo():
	"""
	Downloads, builds and installs Assimulo
	"""	
	import urllib2
	import shutil
	tmpDir = '/tmp/assimulo'
	sourceUrl = 'https://pypi.python.org/packages/source/A/Assimulo/Assimulo-2.7b1.tar.gz'
	if (os.path.isdir(tmpDir)):
		shutil.rmtree(tmpDir)
	os.mkdir(tmpDir)

	with virtualenv(), lcd(tmpDir):
		webArchive = urllib2.urlopen(sourceUrl)
		archiveFile = open(os.path.join(tmpDir, 'assimulo.tar.gz'),'wb')
		archiveFile.write(webArchive.read())
		archiveFile.close()
		local('tar -xzf assimulo.tar.gz', shell='bash')
		with lcd('Assimulo-2.7b1'):
			local('python setup.py install --sundials-home=/usr', shell='bash')
	
	
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
