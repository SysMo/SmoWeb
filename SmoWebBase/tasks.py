from __future__ import absolute_import

from celery import shared_task, task

@task(track_started=True, bind = True)
def celeryCompute(self, model, view, parameters):
    instance = model()
    instance.fieldValuesFromJson(parameters)
    instance.computeAsynchronously(self)
    return instance.modelView2Json(view)