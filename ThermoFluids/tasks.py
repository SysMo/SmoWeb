'''
Created on Dec 29, 2014

@author: Atanas Pavlov
'''

from __future__ import absolute_import

from celery import shared_task, current_task


@shared_task
def ExampleModel_compute(parameters):
	from smo.flow.heatExchange1D.CryogenicPipe import CryogenicPipe
	pipe = CryogenicPipe()
	pipe.fieldValuesFromJson(parameters)
	pipe.compute()
	return pipe.superGroupList2Json(pipe.results)
