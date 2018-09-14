from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import get_object_or_404, render
from django.views.generic import DetailView, ListView
from django.db.models import Count, Max, Min
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator

from .models import Version, Tag, Work, Author, Conference, Institution, Gender, Appellation, Department

class TagView(DetailView):
    model = Tag
    template_name = 'tag_detail.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        obj = super().get_object()
        context['tag_works'] = Work.objects.filter(versions__tags=obj)[:50]
        return context

class TagList(ListView):
    context_object_name = 'tag_list'
    template_name = 'tag_list.html'

    def get_queryset(self):
        return Tag.objects.annotate(num_works=Count('versions__work__distinct')).order_by("title")

class WorkList(ListView):
    context_object_name = 'work_list'
    template_name = 'index.html'

    def get_queryset(self):
        return Work.objects.all()[:10]

class WorkView(DetailView):
    model = Work
    template_name = 'work_detail.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        obj = super().get_object()
        # Add in a QuerySet of all the books
        context['work_versions'] = obj.versions.all()
        context['work_authorships'] = obj.versions.first().authorships.order_by("authorship_order")
        return context

class AuthorView(DetailView):
    model = Author
    template_name = 'author_detail.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        obj = super().get_object()

        context['authored_works'] = Work.objects.filter(
            versions__authorships__author=obj).distinct().order_by("-conference__year")

        context['appellations'] = Appellation.objects.filter(assertions__author=obj).distinct()

        context['gender_memberships'] = obj.gender_memberships.order_by("-asserted_by__work__conference__year")

        context['departments'] = Department.objects.filter(assertions__author=obj).distinct()

        context['institutions'] = Institution.objects.filter(assertions__author=obj).distinct()

        context['authored_versions'] = Version.objects.filter(authorships__author=obj).order_by("-work__conference__year")


        context['institution_choices'] = Institution.objects.order_by("name")

        context['gender_choices'] = Gender.objects.order_by("?")

        return context

class AuthorList(ListView):
    context_object_name = 'author_list'
    template_name = 'author_list.html'
    paginate_by = 10

    def get_queryset(self):
        return Author.objects.annotate(last_name=Max("appellations__last_name")).order_by("last_name")

class ConferenceView(DetailView):
    model = Conference
    template_name = 'conference_detail.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        obj = super().get_object()
        context['works'] = obj.works.all()
        return(context)

class ConferenceList(ListView):
    context_object_name = 'conference_list'
    template_name = 'conference_list.html'

    def get_queryset(self):
        return Conference.objects.order_by("-year")

class InstitutionView(DetailView):
    model = Institution
    template_name = 'institution_detail.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        obj = super().get_object()
        context['members'] = obj.member_assertions.all()
        return(context)

class InstitutionList(ListView):
    context_object_name = 'institution_list'
    template_name = 'institution_list.html'

    def get_queryset(self):
        return Institution.objects.annotate(num_members=Count("member_assertions")).order_by("-num_members")

def home_view(request):
    conference_count = Conference.objects.count()
    work_count = Work.objects.count()
    author_count = Author.objects.count()
    institution_count = Institution.objects.count()
    country_count = Institution.objects.values("country").distinct().count()
    context = {
        'conference_count': conference_count,
        'work_count': work_count,
        'author_count': author_count,
        'institution_count': institution_count,
        'country_count': country_count,
        }
    return render(request, "index.html", context)
