from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import get_object_or_404, render
from django.views.generic import DetailView, ListView

from .models import Version, Tag, Work, Author

class TagView(DetailView):
    model = Tag
    template_name = 'tag_detail.html'

class TagList(ListView):
    context_object_name = 'tag_list'
    template_name = 'tag_list.html'

    def get_queryset(self):
        return Tag.objects.all()

class WorkList(ListView):
    context_object_name = 'work_list'
    template_name = 'index.html'

    def get_queryset(self):
        return Work.objects.all()[:10]

class WorkView(DetailView):
    model = Work
    template_name = 'work_detail.html'

class AuthorView(DetailView):
    model = Author
    template_name = 'author_detail.html'

class AuthorList(ListView):
    context_object_name = 'author_list'
    template_name = 'author_list.html'

    def get_queryset(self):
        return Author.objects.all()[:10]
