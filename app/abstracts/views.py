from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import get_object_or_404, render
from django.views.generic import DetailView, ListView
from django.db.models import Count, Max, Min
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator

from .models import (
    Work,
    Author,
    Conference,
    Institution,
    Gender,
    Appellation,
    Department,
    ConferenceSeries,
)


class WorkList(ListView):
    context_object_name = "work_list"
    template_name = "index.html"

    def get_queryset(self):
        return Work.objects.filter(state="ac")[:10]


class WorkView(DetailView):
    model = Work
    template_name = "work_detail.html"


class AuthorView(DetailView):
    model = Author
    template_name = "author_detail.html"

    def public_appellations(self):
        return self.appellation_assertions.filter(
            asserted_by__work__state="ac"
        ).distinct()

    def public_institutions(self):
        return self.institution_assertions.filter(
            asserted_by__work__state="ac"
        ).distinct()

    def public_departments(self):
        return self.department_assertions.filter(
            asserted_by__work__state="ac"
        ).distinct()

    def public_affilliations(self):
        return self.public_institutions().union(
            Institution.objects.filter(departments__in=self.public_departments())
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["appellation_assertions"] = self.public_appellations()
        return context


class AuthorList(ListView):
    context_object_name = "author_list"
    template_name = "author_list.html"
    paginate_by = 10

    def get_queryset(self):
        """
        Only return authors who have at least one public work
        """
        return (
            Author.objects.filter(works__state="ac")
            .distinct()
            .annotate(last_name=Max("appellations__last_name"))
            .order_by("last_name")
        )


class ConferenceView(DetailView):
    model = Conference
    template_name = "conference_detail.html"


class ConferenceList(ListView):
    context_object_name = "conference_list"
    template_name = "conference_list.html"

    def get_queryset(self):
        return Conference.objects.order_by("-year")


class SeriesList(ListView):
    context_object_name = "series_list"
    template_name = "series_list.html"

    def get_queryset(self):
        return ConferenceSeries.objects.order_by("title")


class SeriesView(DetailView):
    model = ConferenceSeries
    template_name = "series_detail.html"


class InstitutionView(DetailView):
    model = Institution
    template_name = "institution_detail.html"


class InstitutionList(ListView):
    context_object_name = "institution_list"
    template_name = "institution_list.html"

    def get_queryset(self):
        """
        Only show those instutitons that are cited in at least one public work
        """
        return (
            Institution.objects.filter(members__works__state="ac")
            .annotate(num_members=Count("members", distinct=True))
            .order_by("-num_members")
        )


def home_view(request):
    public_works = Work.objects.filter(state="ac").distinct()

    conference_count = (
        Conference.objects.filter(works__in=public_works).distinct().count()
    )

    work_count = public_works.count()
    author_count = Author.objects.filter(works__in=public_works).distinct().count()

    public_institutions = Institution.objects.filter(
        members__works__in=public_works
    ).distinct()
    institution_count = public_institutions.count()
    country_count = (
        public_institutions.values_list("country", flat=True).distinct().count()
    )

    context = {
        "site": {
            "conference_count": conference_count,
            "work_count": work_count,
            "author_count": author_count,
            "institution_count": institution_count,
            "country_count": country_count,
        }
    }

    return render(request, "index.html", context)
