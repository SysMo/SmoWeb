'''
Created on Dec 29, 2014

@author: Atanas Pavlov
'''

from __future__ import absolute_import

from celery import shared_task, task

@task(track_started=True, bind = True)
def celeryCompute(self, model, view, parameters):
	instance = model()
	instance.fieldValuesFromJson(parameters)
	instance.computeAsynchronously(self)
	return instance.modelView2Json(view)


from time import sleep
@task(track_started=True, bind = True) # or CELERY_TRACK_STARTED=True
def do_work(self):
	for i in range(100):
		sleep(0.2)
		self.update_state(state='PROGRESS', 
									meta={'current': i, 'total': 99.})