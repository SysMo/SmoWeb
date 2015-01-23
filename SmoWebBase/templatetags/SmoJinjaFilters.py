from django_jinja import library
from SmoWeb.settings import BASE_DIR, STATIC_URL

@library.filter
def getModelDocUrl(module):
    return "documentation/html/" + module.name + ".html"

@library.filter
def getHtmlBlockUrl(block, pageView):
    return pageView.router.name + "/subtemplates/" + block.src

@library.filter
def getJsBlockUrl(block, pageView):
    return pageView.router.name + "/jsblocks/" + block.src

@library.filter
def generateHtml(src):
    context = {"static": STATIC_URL}
    return src.format(**context)

@library.filter
def isActive(view, module):
    if (isinstance(module, type)):
        return view.activeModule == module
    else:
        return  view.activeModule == module.__class__