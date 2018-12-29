from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import get_object_or_404, render
from django.views.generic import DetailView, ListView
from django.db.models import Count, Max, Min
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models.functions import Coalesce

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.object

        context["authorships"] = obj.authorships.order_by("authorship_order")
        return context


class AuthorView(DetailView):
    model = Author
    template_name = "author_detail.html"

    # def public_works(self):
    #     return (

    #     )

    # Construct a defaultdict from the initial query so that it's easy to
    # iterate over idfferent values for an assertion, and then page through
    # each of those values' source Works.
    # def public_appellation_assertions(self):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.object

        obj_authorships = obj.public_authorships

        public_works = (
            Work.objects.filter(authorships__in=obj_authorships)
            .distinct()
            .order_by("-conference__year")
        )

        appellation_assertions = [
            {
                "appellation": a,
                "works": public_works.filter(
                    authorships__in=obj_authorships.filter(appellations=a)
                ),
            }
            for a in Appellation.objects.filter(asserted_by__in=obj_authorships)
            .distinct()
            .order_by("last_name")
        ]

        all_departments = Department.objects.filter(asserted_by__in=obj_authorships)

        all_institutions = Institution.objects.filter(
            asserted_by__in=obj_authorships
        ).union(Institution.objects.filter(departments__in=all_departments))

        affiliation_assertions = [
            {
                "institution": i,
                "departments": all_departments.filter(institution=i).distinct(),
                "works": public_works.filter(
                    authorships__in=obj_authorships.filter(institutions=i)
                ).union(
                    public_works.filter(
                        authorships__in=obj_authorships.filter(
                            departments__institution=i
                        )
                    )
                ),
            }
            for i in all_institutions
        ]

        context["public_works"] = public_works
        context["appellation_assertions"] = appellation_assertions
        context["affiliation_assertions"] = affiliation_assertions
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
    author_count = (
        Author.objects.filter(authorships__work__in=public_works).distinct().count()
    )

    public_institutions = Institution.objects.filter(
        asserted_by__work__in=public_works
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
