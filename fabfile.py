# Call with
# fab -H localhost deploy

import os
import glob
from fabric.api import *
from contextlib import contextmanager as _contextmanager

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

@_contextmanager
def virtualenv():
	with cd(env.projectRoot):
		with prefix(env.activate):
			yield


def deploy():
	with virtualenv():
		local('python manage.py collectstatic -v0 --noinput', shell='bash')
		print("Collected static files")
		for module in env.folderCopyList:
			local('cp -r ./{0} {1}'.format(module, os.path.join(env.installDir, 'Platform')), shell='bash')
	local('unison -ignore "Name {*.pyc}" /srv/SmoWeb ssh://' + srvAddress + '//srv/SmoWeb')
	sudo('chown -R www-data:www-data /srv/SmoWeb ')
	sudo('service apache2 restart')
		
def syncVirtEnv():
	local('unison -ignore "Name {*.pyc}" /srv/VirtualEnv/ ssh://' + srvAddress + '//srv/VirtualEnv')
	sudo('chown -R www-data:www-data /srv/SmoWeb ')
	sudo('service apache2 restart')
	
def rest2html():
	from docutils.core import publish_parts
	from docutils import io
	from docutils.writers import html4css1
	import codecs
	for app in env.applicationModules:
		markupFolder = os.path.join(env.projectRoot, app, 'templates', 'markup')
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
		
