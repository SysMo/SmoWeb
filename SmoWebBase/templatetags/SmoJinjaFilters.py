from django_jinja import library
from SmoWeb.settings import BASE_DIR, STATIC_URL

@library.filter
def getRestBlockUrl(module, pageView):
    return pageView.router.name + "/restblocks/html/" + module.name + ".html"

@library.filter
def getBlockUrl(block, pageView):
    return pageView.router.name + "/blocks/" + block.src

@library.filter
def isActive(view, module):
    if (isinstance(module, type)):
        return view.activeModule == module
    else:
        return  view.activeModule == module.__class__