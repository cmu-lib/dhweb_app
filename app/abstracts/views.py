from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import get_object_or_404, render

from .models import Version

# Create your views here.
def index(request):
    version_list = Version.objects.all()
    context = {'version_list': version_list}
    return render(request, 'index.html', context)
    
def version_detail(request, version_id):
    version = get_object_or_404(Version, pk = version_id)
    context = {'version': Version}
    return render(request, "version_detail.html", context)
