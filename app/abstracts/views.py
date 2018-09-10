from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import get_object_or_404, render
from django.views import generic

from .models import Version, Tag, Work, Author

class TagView(generic.DetailView):
    model = Tag
    template_name = 'tag_detail.html'

class TagList(generic.ListView):
    context_object_name = 'tag_list'
    template_name = 'tag_list.html'

    def get_queryset(self):
        return Tag.objects.all()

class WorkList(generic.ListView):
    context_object_name = 'work_list'
    template_name = 'index.html'

    def get_queryset(self):
        return Work.objects.all()[:10]

class AuthorView(generic.DetailView):
    model = Author
    template_name = 'author_detail.html'

class AuthorList(generic.ListView):
    context_object_name = 'author_list'
    template_name = 'author_list.html'

    def get_queryset(self):
        return Author.objects.all()[:10]

def work_detail(request, work_id):
    work = get_object_or_404(Work, pk = work_id)
    version_list = work.versions.all()
    context = {'work': work, 'version_list': version_list}
    return render(request, "work_detail.html", context)
