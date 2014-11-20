import json
from django.shortcuts import render_to_response, RequestContext
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from smo.numerical_model.quantity import Quantities

# def home(request):
#     return render_to_response('Home.html', context_instance=RequestContext(request))

def home(request):
    return render_to_response('Base.html', context_instance=RequestContext(request))

def unitConverterView(request):
    if request.method == 'GET':
        return render_to_response('UnitConverter.html', 
                                context_instance=RequestContext(request))
    elif request.method == 'POST':
        postData = json.loads(request.body)
        action = postData['action']
        parameters = postData['parameters']
        if (action == 'getInputs'):
            print json.dumps(Quantities, True)
            return JsonResponse(Quantities)
        else:
            raise ValueError('Unknown post action "{0}" for URL: {1}'.format(action, 'UnitConverter.html'))