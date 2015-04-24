'''
Created on Dec 29, 2014

@author: Atanas Pavlov
'''

from __future__ import absolute_import

from celery import shared_task, task, current_task



@shared_task(bind = True)
def Celery_compute(self, cls, parameters):
	self = cls()
	self.fieldValuesFromJson(parameters)
	self.compute()
	return self.superGroupList2Json(self.results)

from time import sleep
@task(track_started=True, bind = True) # or CELERY_TRACK_STARTED=True
def do_work(self):
	for i in range(100):
		sleep(0.1)
		self.update_state(state='PROGRESS', 
									meta={'current': i, 'total': 99.})