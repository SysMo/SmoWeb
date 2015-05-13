from __future__ import absolute_import

from celery import task
from smo.model.model import modelRegistry

@task(track_started=True, bind = True)
def celeryCompute(self, modelName, viewName, parameters):
    model = modelRegistry[modelName]
    view = model.declared_modelViews[viewName]
    instance = model()
    instance.fieldValuesFromJson(parameters)
    instance.task = self
    instance.computeAsync()
    return instance.modelView2Json(view)

# Starting worker: celery -A SmoWeb worker -l info