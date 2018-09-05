from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import get_object_or_404, render
from django.views import generic

from .models import Version, Tag, Work, Author

class DetailView(generic.DetailView):
    model = Tag
    template_name = 'tag_detail.html'

class IndexView(generic.ListView):
    context_object_name = 'tag_list'
    template_name = 'tag_list.html'

    def get_queryset(self):
        return Tag.objects.all()

class IndexView(generic.ListView):
    context_object_name = 'work_list'
    template_name = 'index.html'

    def get_queryset(self):
        return Work.objects.all()[:10]

class DetailView(generic.DetailView):
    model = Author
    template_name = 'author_detail.html'

class IndexView(generic.ListView):
    context_object_name = 'author_list'
    template_name = 'author_list.html'

    def get_queryset(self):
        return Author.objects.all()[:10]

def work_detail(request, work_id):
    work = get_object_or_404(Work, pk = work_id)
    version_list = Version.objects.filter(work_id=work)
    context = {'work': work, 'version_list': version_list}
    return render(request, "work_detail.html", context)
