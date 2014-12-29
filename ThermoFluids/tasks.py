'''
Created on Dec 29, 2014

@author: Atanas Pavlov
'''

from __future__ import absolute_import

from celery import shared_task


@shared_task(bind = True)
def Celery_compute(self, cls, parameters):
	instance = cls()
	instance.fieldValuesFromJson(parameters)
	instance.compute()
	return instance.superGroupList2Json(instance.results)
