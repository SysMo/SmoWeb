from __future__ import absolute_import

from celery import task

@task(track_started=True, bind = True)
def celeryCompute(self, model, view, parameters):
    instance = model()
    instance.fieldValuesFromJson(parameters)
    instance.task = self
    instance.computeAsync()
    return instance.modelView2Json(view)

# Starting worker: celery -A SmoWeb worker -l info