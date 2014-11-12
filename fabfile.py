# Call with
# fab -H localhost deploy

import os
import fabric
from fabric.api import *
from contextlib import contextmanager as _contextmanager

env.projectRoot = os.getcwd()
env.installDir = '/srv/SmoWeb/'
env.activate = 'source {0}'.format(os.path.join(env.installDir, '../VirtualEnv/SmoWebPlatform/bin//activate'))
env.djangoModules = [
	'SmoWeb',
	'DataManagement',
	'ThermoFluids',
	'manage.py',
	'smo',
	'templates'
]

@_contextmanager
def virtualenv():
	with cd(env.projectRoot):
		with prefix(env.activate):
			yield


def deploy():
	with virtualenv():
		local('python manage.py collectstatic -v0 --noinput', shell='bash')
		print("Collected static files")
		for module in env.djangoModules:
			local('cp -r ./{0} {1}'.format(module, os.path.join(env.installDir, 'Platform')), shell='bash')
	local('unison /srv/SmoWeb ssh://platform.sysmoltd.com//srv/SmoWeb')
	sudo('chown -R www-data:www-data /srv/SmoWeb ')
	sudo('service apache2 restart')
		
