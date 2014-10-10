from django.shortcuts import render_to_response, RequestContext

# def home(request):
#     return render_to_response('Home.html', context_instance=RequestContext(request))

def home(request):
    return render_to_response('Base.html', context_instance=RequestContext(request))

def platform(request):
    return render_to_response('Platform.html', context_instance=RequestContext(request))
