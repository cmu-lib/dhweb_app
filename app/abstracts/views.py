from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import get_object_or_404, render
from django.views import generic

from .models import Version, Tag, Work

class DetailView(generic.DetailView):
    model = Tag
    template_name = 'tag_detail.html'

def index(request):
    version_list = Work.objects.all()[:10]
    context = {'work_list': work_list}
    return render(request, 'index.html', context)

def work_detail(request, work_id):
    work = get_object_or_404(Work, pk = work_id)
    version_list = Version.objects.filter(work_id=work)
    context = {'work': work, 'version_list': version_list}
    return render(request, "work_detail.html", context)
