'''
Created on Dec 29, 2014

@author: Atanas Pavlov
'''

from __future__ import absolute_import

from celery import shared_task


@shared_task(bind = True)
def Celery_compute(self, cls, parameters):
	self = cls()
	self.fieldValuesFromJson(parameters)
	self.compute()
	return self.superGroupList2Json(self.results)
