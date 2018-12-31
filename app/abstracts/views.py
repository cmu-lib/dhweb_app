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
    Affiliation,
    ConferenceSeries,
    Country,
    Topic,
)

from .forms import WorkFilter, AuthorFilter


class WorkList(ListView):
    context_object_name = "work_list"
    template_name = "work_list.html"
    paginate_by = 10

    def get_queryset(self):
        base_result_set = Work.objects.filter(state="ac").order_by("title").distinct()

        filter_form = self.request.GET

        result_set = base_result_set

        if "work_type" in filter_form:
            work_type_res = filter_form["work_type"]
            if work_type_res != "":
                result_set = result_set.filter(work_type__pk=work_type_res)

        if "conference" in filter_form:
            conference_res = filter_form["conference"]
            if conference_res != "":
                result_set = result_set.filter(conference__pk=conference_res)

        if "institution" in filter_form:
            institution_res = filter_form["institution"]
            if institution_res != "":
                result_set = result_set.filter(
                    authorships__affiliations__institution=institution_res
                )

        if "keyword" in filter_form:
            keyword_res = filter_form["keyword"]
            if keyword_res != "":
                result_set = result_set.filter(keywords__pk=keyword_res)

        if "topic" in filter_form:
            topic_res = filter_form["topic"]
            if topic_res != "":
                result_set = result_set.filter(topics__pk=topic_res)

        if "full_text_available" in filter_form:
            full_text_available_res = filter_form["full_text_available"]
            if full_text_available_res == "on":
                result_set = result_set.exclude(full_text="")

        return result_set.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["work_filter_form"] = WorkFilter(data=self.request.GET)
        context["available_works_count"] = Work.objects.filter(state="ac").count()
        context["filtered_works_count"] = self.get_queryset().count()
        return context


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.object

        obj_authorships = obj.public_authorships

        public_works = (
            Work.objects.filter(authorships__in=obj_authorships)
            .distinct()
            .order_by("-conference__year")
        )

        split_works = [
            {"series": c, "works": public_works.filter(conference__series=c).distinct()}
            for c in ConferenceSeries.objects.filter(
                conferences__works__in=public_works
            ).distinct()
        ]

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

        all_affiliations = Affiliation.objects.filter(asserted_by__in=obj_authorships)

        affiliation_assertions = [
            {
                "institution": i,
                "departments": all_affiliations.filter(institution=i)
                .values_list("department", flat=True)
                .distinct(),
                "works": Work.objects.filter(
                    authorships__in=obj_authorships.filter(affiliations__institution=i)
                ).distinct(),
            }
            for i in Institution.objects.filter(
                affiliations__in=all_affiliations
            ).distinct()
        ]

        context["split_works"] = split_works
        context["appellation_assertions"] = appellation_assertions
        context["affiliation_assertions"] = affiliation_assertions
        return context


class AuthorList(ListView):
    context_object_name = "author_list"
    template_name = "author_list.html"
    paginate_by = 10

    def get_queryset(self):
        base_result_set = Author.objects.filter(works__state="ac").distinct()

        filter_form = self.request.GET

        result_set = base_result_set

        if "institution" in filter_form:
            institution_res = filter_form["institution"]
            if institution_res != "":
                result_set = result_set.filter(
                    authorships__affiliations__institution__pk=institution_res
                )

        if "country" in filter_form:
            country_res = filter_form["country"]
            if country_res != "":
                result_set = result_set.filter(
                    authorships__affiliations__institution__country__pk=country_res
                )

        return result_set.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["author_filter_form"] = AuthorFilter(data=self.request.GET)
        context["available_authors_count"] = Author.objects.filter(
            works__state="ac"
        ).count()
        context["filtered_authors_count"] = self.get_queryset().count()
        return context


class ConferenceList(ListView):
    context_object_name = "conference_list"
    template_name = "conference_list.html"

    def get_queryset(self):
        return ConferenceSeries.objects.order_by("title")


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
        affiliations__asserted_by__work__in=public_works
    ).distinct()
    institution_count = public_institutions.count()
    country_count = (
        Country.objects.filter(institutions__in=public_institutions).distinct().count()
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
