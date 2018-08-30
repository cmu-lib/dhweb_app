from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

from .models import Version

# Create your views here.
def index(request):
    version_list = Version.objects.all()
    template = loader.get_template("index.html")
    context = {
        'version_list': version_list,
    }
    return HttpResponse(template.render(context, request))
    
