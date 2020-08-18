from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, StreamingHttpResponse, FileResponse
from django.template import loader
from django.shortcuts import get_object_or_404, render, redirect
from django.views import View
from django.views.generic import DetailView, ListView
from django.db.models import (
    Count,
    Max,
    Min,
    Q,
    F,
    Prefetch,
    Subquery,
    OuterRef,
    ExpressionWrapper,
    FloatField,
    BooleanField,
)
from django.db.models.functions import Concat, FirstValue, Cast
from django.core import management
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models.functions import Coalesce
from django.contrib.postgres.search import SearchRank, SearchQuery
from django.contrib.postgres.aggregates import StringAgg
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required, user_passes_test
from dal.autocomplete import Select2QuerySetView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.db import transaction, IntegrityError
from django.forms.models import model_to_dict
from django.forms import formset_factory, inlineformset_factory, modelformset_factory
from django.conf import settings
from django.utils.html import format_html
from django.views.decorators.cache import cache_page
import glob
from os.path import basename, getmtime
from datetime import datetime
import csv
import sys
from operator import attrgetter

from . import models

from .models import (
    Work,
    WorkType,
    Author,
    Conference,
    Institution,
    Appellation,
    Affiliation,
    ConferenceSeries,
    SeriesMembership,
    Organizer,
    Country,
    Keyword,
    Topic,
    Discipline,
    Language,
    CountryLabel,
    Authorship,
)

from .forms import (
    WorkFilter,
    AuthorFilter,
    AuthorMergeForm,
    WorkForm,
    WorkAuthorshipForm,
    FullInstitutionForm,
    InstitutionMergeForm,
    AffiliationEditForm,
    AffiliationMergeForm,
    KeywordMergeForm,
    TagForm,
    TopicMergeForm,
    AffiliationMultiMergeForm,
    KeywordMultiMergeForm,
    ConferenceForm,
    ConferenceCheckoutForm,
    ConferenceSeriesInline,
    LanguageMergeForm,
    DisciplineMergeForm,
    WorkTypeMergeForm,
    InstitutionMultiMergeForm,
    TopicMultiMergeForm,
)


PERMISSIONS_ERROR_TEXT = (
    "Please contact the lead project editors to edit this part of the database."
)


def cache_for_anon(func):
    """
    On these views, call the cache if the user is not authenticated
    """

    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated:
            return func(request, *args, **kwargs)
        else:
            return cache_page(60)(func)(request, *args, **kwargs)

    return wrap


def user_is_staff(func):
    def wrap(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f"{reverse('login')}?next={request.path}")
        if request.user.is_staff:
            return func(request, *args, **kwargs)
        else:
            messages.warning(request, PERMISSIONS_ERROR_TEXT)
            return redirect("home_view")

    return wrap


class StaffRequiredMixin:
    def dispatch(self, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return redirect(f"{reverse('login')}?next={self.request.path}")
        if self.request.user.is_staff:
            return super().dispatch(*args, **kwargs)
        else:
            messages.warning(self.request, PERMISSIONS_ERROR_TEXT)
            return redirect("home_view")


class ItemLabelAutocomplete(Select2QuerySetView):
    def get_selected_result_label(self, item):
        return self.get_result_label(item)


class WorkAutocomplete(ItemLabelAutocomplete):
    raise_exception = True

    def get_queryset(self):

        qs = Work.objects.all()

        parents_only = self.forwarded.get("parents_only", None)
        if parents_only:
            qs = qs.filter(work_type__is_parent=True)

        conference = self.forwarded.get("conference", None)
        if conference:
            qs = qs.filter(conference=conference)

        if self.q:
            qs = qs.filter(title__icontains=self.q)

        return qs.all()


class AppellationAutocomplete(ItemLabelAutocomplete):
    raise_exception = True

    def get_queryset(self):
        qs = Appellation.objects.all()

        if self.q:
            qs = qs.filter(
                Q(first_name__icontains=self.q) | Q(last_name__icontains=self.q)
            ).all()

        return qs


class KeywordAutocomplete(ItemLabelAutocomplete):
    raise_exception = True

    def get_queryset(self):
        qs = Keyword.objects.annotate(n_works=Count("works")).order_by("-n_works")

        if self.q:
            qs = qs.filter(title__icontains=self.q).all()

        return qs

    def get_result_label(self, item):
        return f"{item} ({item.n_works} works)"


class LanguageAutocomplete(ItemLabelAutocomplete):
    raise_exception = True

    def get_queryset(self):
        qs = Language.objects.annotate(n_works=Count("works")).order_by("-n_works")

        if self.q:
            qs = qs.filter(title__icontains=self.q).all()

        return qs

    def get_result_label(self, item):
        return f"{item} ({item.n_works} works)"


class TopicAutocomplete(ItemLabelAutocomplete):
    raise_exception = True

    def get_queryset(self):
        qs = Topic.objects.annotate(n_works=Count("works")).order_by("-n_works")

        if self.q:
            qs = qs.filter(title__icontains=self.q).all()

        return qs

    def get_result_label(self, item):
        return f"{item} ({item.n_works} works)"


class DisciplineAutocomplete(ItemLabelAutocomplete):
    raise_exception = True

    def get_queryset(self):
        qs = Discipline.objects.annotate(n_works=Count("works")).order_by("-n_works")

        if self.q:
            qs = qs.filter(title__icontains=self.q).all()

        return qs

    def get_result_label(self, item):
        return f"{item} ({item.n_works} works)"


class CountryAutocomplete(ItemLabelAutocomplete):
    raise_exception = True

    def get_queryset(self):
        qs = Country.objects.annotate(
            n_works=Count(
                "institutions__affiliations__asserted_by__work", distinct=True
            )
        ).order_by("-n_works")

        if self.q:
            qs = qs.filter(
                Q(pref_name__icontains=self.q) | Q(names__name__icontains=self.q)
            )

        return qs.distinct()

        def get_result_label(self, item):
            return f"{item} ({item.n_works} works)"


class InstitutionAutocomplete(ItemLabelAutocomplete):
    raise_exception = True

    def get_queryset(self):
        qs = (
            Institution.objects.annotate(
                n_works=Count("affiliations__asserted_by__work", distinct=True)
            )
            .select_related("country")
            .order_by("-n_works")
        )

        if self.q:
            qs = qs.filter(name__icontains=self.q).all()

        return qs

    def get_result_label(self, item):
        if item.country is not None:
            c_label = item.country.pref_name
        else:
            c_label = ""
        location_statement = ", ".join(
            [l for l in [item.state_province_region, c_label] if l != ""]
        )
        return f"{item} ({item.n_works} works)<br><small text-class='muted'>{location_statement}</small>"


class AffiliationAutocomplete(ItemLabelAutocomplete):
    raise_exception = True

    def get_queryset(self):
        qs = (
            Affiliation.objects.annotate(
                n_works=Count("asserted_by__work", distinct=True)
            )
            .select_related("institution", "institution__country")
            .order_by("-n_works")
        )

        inst_filter = self.forwarded.get("institution", None)
        if inst_filter:
            qs = qs.filter(institution=inst_filter)

        if self.q:
            qs = qs.filter(
                Q(department__icontains=self.q) | Q(institution__name__icontains=self.q)
            ).distinct()

        return qs

    def get_result_label(self, item):
        if item.institution.country is not None:
            c_label = item.institution.country.pref_name
        else:
            c_label = ""
        location_statement = ", ".join(
            [l for l in [item.institution.state_province_region, c_label] if l != ""]
        )
        return f"{item} ({item.n_works} works)<br><small text-class='muted'>{location_statement}</small>"


class ConferenceAutocomplete(ItemLabelAutocomplete):
    raise_exception = True

    def get_queryset(self):
        qs = Conference.objects.annotate(
            main_series=StringAgg(
                "series_memberships__series__abbreviation",
                delimiter=" / ",
                distinct=True,
            )
        ).order_by("year", "main_series", "short_title", "theme_title")

        if self.q:
            qs = qs.filter(
                Q(short_title__icontains=self.q)
                | Q(theme_title__icontains=self.q)
                | Q(main_series=self.q)
            ).distinct()

        return qs

    def get_result_label(self, item):
        if item.main_series:
            return f"{item.main_series} - {item.year} - {item.short_title}"
        elif item.short_title:
            return f"{item.year} - {item.short_title}"
        else:
            return f"{item.year} - {item.theme_title}"


class AuthorAutocomplete(ItemLabelAutocomplete):
    raise_exception = True

    def get_queryset(self):
        qs = Author.objects.annotate(
            n_works=Count("authorships", distinct=True),
            main_last_name=Max("appellations__last_name"),
            main_first_name=Max("appellations__first_name"),
        ).order_by("main_last_name", "main_first_name", "-n_works")

        if self.q:
            qs = qs.filter(appellations_index__icontains=self.q).distinct()

        return qs

    def get_result_label(self, item):
        return format_html(
            f"{item.most_recent_appellation} ({item.n_works} works)<br><small text-class='muted'>(All names: {item.appellations_index})</small>"
        )


def work_view(request, work_id):
    related_conference = Conference.objects.annotate(
        n_works=Count("works", distinct=True),
        n_authors=Count("works__authors", distinct=True),
        main_series=StringAgg(
            "series_memberships__series__abbreviation", delimiter=" / ", distinct=True
        ),
    )
    work = get_object_or_404(
        Work.objects.select_related(
            "work_type", "parent_session", "full_text_license"
        ).prefetch_related(
            Prefetch("conference", queryset=related_conference),
            "conference__series",
            "conference__organizers",
            "keywords",
            "topics",
            "disciplines",
            "languages",
            "session_papers",
            "session_papers__authorships__appellation",
            "parent_session__authorships__appellation",
        ),
        pk=work_id,
    )

    authorships = (
        Authorship.objects.filter(work__id=work_id)
        .order_by("authorship_order")
        .distinct()
        .select_related("work", "author", "appellation")
        .prefetch_related(
            "affiliations",
            "affiliations__institution",
            "affiliations__institution__country",
        )
    )
    context = {"work": work, "authorships": authorships}
    return render(request, "work_detail.html", context)


def author_view(request, author_id):
    author = get_object_or_404(Author, pk=author_id)

    sorted_authorships = (
        Authorship.objects.filter(author=author)
        .order_by("work__conference__year")
        .prefetch_related("work", "work__conference")
    )

    appellations = (
        Appellation.objects.filter(asserted_by__author=author)
        .distinct()
        .annotate(latest_year=Max("asserted_by__work__conference__year"))
        .order_by("-latest_year")
        .prefetch_related(Prefetch("asserted_by", queryset=sorted_authorships))
    )

    affiliations = (
        Affiliation.objects.filter(asserted_by__author=author)
        .distinct()
        .annotate(latest_year=Max("asserted_by__work__conference__year"))
        .order_by("-latest_year")
        .prefetch_related(
            Prefetch("asserted_by", queryset=sorted_authorships),
            "institution",
            "institution__country",
        )
    )

    works = (
        Work.objects.filter(authorships__author=author)
        .order_by("conference__year")
        .distinct()
        .select_related("conference", "parent_session", "work_type")
        .prefetch_related(
            "conference__series",
            "conference__organizers",
            "session_papers",
            "keywords",
            "topics",
            "disciplines",
            "languages",
            "authorships",
            "authorships__appellation",
            "authorships__author__appellations",
        )
    )

    author_admin_page = reverse("admin:abstracts_author_change", args=(author.pk,))

    context = {
        "author": author,
        "works": works,
        "appellations": appellations,
        "affiliations": affiliations,
        "author_admin_page": author_admin_page,
    }

    return render(request, "author_detail.html", context)


class AuthorSplit(DetailView, StaffRequiredMixin):
    model = Author
    template_name = "author_split.html"
    context_object_name = "original_author"

    def get_context_data(self, **kwargs):
        authorships = Authorship.objects.filter(author=self.get_object()).order_by(
            "work__conference__year"
        )
        return {self.context_object_name: self.get_object(), "authorships": authorships}

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        """
        Create new author and transfer authorships
        """
        authorships_to_move = request.POST.getlist("splitselect")
        try:
            print(authorships_to_move)
            new_author = Author.objects.create()
            Authorship.objects.filter(id__in=authorships_to_move).update(
                author=new_author
            )
            # Force-update appellations
            self.get_object().save()
            new_author.save()
            messages.success(
                request,
                f"{len(authorships_to_move)} authorships moved to new author id {new_author.id}",
            )
            return redirect("author_detail", new_author.id)
        except:
            messages.error(request, str(authorships_to_move))
            return redirect("author_split", self.get_object().id)


class XMLView(DetailView, LoginRequiredMixin):
    model = Work
    context_object_name = "work"

    def get(self, request, *args, **kwargs):
        response = HttpResponse(self.get_object().full_text, content_type="xhtml+xml")
        response[
            "Content-Disposition"
        ] = f"attachment; filename={self.get_object().id}.xml"
        return response


class AuthorList(ListView):
    context_object_name = "author_list"
    template_name = "author_list.html"
    paginate_by = 50

    def get_queryset(self):
        base_result_set = Author.objects.exclude(appellations__isnull=True)
        raw_filter_form = AuthorFilter(self.request.GET)

        if raw_filter_form.is_valid():
            filter_form = raw_filter_form.cleaned_data

            order_res = filter_form["ordering"]
            if order_res is None or order_res == "":
                order_res = "last_name"

            result_set = base_result_set.annotate(
                last_name=Max("appellations__last_name"),
                n_works=Count("authorships", distinct=True),
            ).order_by(order_res)

            author_res = filter_form["author"]
            if author_res is not None:
                result_set = result_set.filter(id=author_res.id)

            affiliation_res = filter_form["affiliation"]
            if affiliation_res is not None:
                result_set = result_set.filter(
                    authorships__affiliations=affiliation_res
                )

            institution_res = filter_form["institution"]
            if institution_res is not None:
                result_set = result_set.filter(
                    authorships__affiliations__institution=institution_res
                )

            country_res = filter_form["country"]
            if country_res is not None:
                result_set = result_set.filter(
                    authorships__affiliations__institution__country=country_res
                )

            name_res = filter_form["name"]
            if name_res != "":
                result_set = result_set.filter(appellations_index__icontains=name_res)

            first_name_res = filter_form["first_name"]
            if first_name_res != "":
                result_set = result_set.filter(
                    authorships__appellation__first_name__icontains=first_name_res
                )

            last_name_res = filter_form["last_name"]
            if last_name_res != "":
                result_set = result_set.filter(
                    authorships__appellation__last_name__icontains=last_name_res
                )

            # Newest affiliations

            newest_authorship = Authorship.objects.filter(
                author=OuterRef("pk")
            ).order_by("-work__conference__year")

            annotated_authors = result_set.annotate(
                main_affiliation_department=Subquery(
                    newest_authorship.values("affiliations__department")[:1]
                ),
                main_affiliation_institution=Subquery(
                    newest_authorship.values("affiliations__institution__name")[:1]
                ),
                main_affiliation_institution_city=Subquery(
                    newest_authorship.values("affiliations__institution__city")[:1]
                ),
                main_affiliation_institution_state=Subquery(
                    newest_authorship.values(
                        "affiliations__institution__state_province_region"
                    )[:1]
                ),
                main_affiliation_institution_country=Subquery(
                    newest_authorship.values(
                        "affiliations__institution__country__pref_name"
                    )[:1]
                ),
                most_recent_first_name=Subquery(
                    newest_authorship.values("appellation__first_name")[:1]
                ),
                most_recent_last_name=Subquery(
                    newest_authorship.values("appellation__last_name")[:1]
                ),
                n_works=Count("authorships", distinct=True),
            )

            return annotated_authors

        else:
            messages.warning(
                self.request,
                "Query parameters not recognized. Check your URL and try again.",
            )
            return base_result_set

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["author_filter_form"] = AuthorFilter(data=self.request.GET)
        context["available_authors_count"] = Author.objects.count()
        context["redirect_url"] = reverse("author_list")
        return context


def annotate_multiple_series(qs):
    return qs.annotate(
        n_conferences=Count("conferences", distinct=True),
        earliest_year=Min("conferences__year"),
        latest_year=Max("conferences__year"),
        n_complete=Count(
            "conferences", filter=Q(conferences__entry_status="c"), distinct=True
        ),
        n_in_progress=Count(
            "conferences", filter=Q(conferences__entry_status="i"), distinct=True
        ),
        n_in_review=Count(
            "conferences", filter=Q(conferences__entry_status="r"), distinct=True
        ),
        n_remaining=F("n_conferences")
        - F("n_complete")
        - F("n_in_progress")
        - F("n_in_review"),
        pct_complete=(
            Cast(F("n_complete"), FloatField()) / Cast(F("n_conferences"), FloatField())
        )
        * 100,
        pct_in_progress=(
            Cast(F("n_in_progress"), FloatField())
            / Cast(F("n_conferences"), FloatField())
        )
        * 100,
        pct_in_review=(
            Cast(F("n_in_review"), FloatField())
            / Cast(F("n_conferences"), FloatField())
        )
        * 100,
    ).order_by("title")


def annotate_single_series(qs):
    res = qs.aggregate(
        earliest_year=Min("year"),
        latest_year=Max("year"),
        n_conferences=Count("id", distinct=True),
        n_complete=Count("id", filter=Q(entry_status="c"), distinct=True),
        n_in_progress=Count("id", filter=Q(entry_status="i"), distinct=True),
        n_in_review=Count("id", filter=Q(entry_status="r"), distinct=True),
    )

    res["n_remaining"] = (
        res["n_conferences"]
        - res["n_complete"]
        - res["n_in_progress"]
        - res["n_in_review"]
    )

    if res["n_conferences"] > 0:
        res["pct_complete"] = (res["n_complete"] / res["n_conferences"]) * 100
        res["pct_in_progress"] = (res["n_in_progress"] / res["n_conferences"]) * 100
        res["pct_in_review"] = (res["n_in_review"] / res["n_conferences"]) * 100
    else:
        res["pct_complete"] = 0
        res["pct_in_progress"] = 0
        res["pct_in_review"] = 0

    return res


def conference_series_qs():
    return annotate_multiple_series(
        ConferenceSeries.objects.exclude(conferences__isnull=True)
    )


class ConferenceSeriesList(ListView):
    context_object_name = "series_list"
    template_name = "conference_series_list.html"

    def get_queryset(self):
        base_result_set = conference_series_qs()
        return base_result_set

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sa_conf = Conference.objects.filter(series__isnull=True)
        context["standalone_conferences"] = annotate_single_series(sa_conf)
        context["standalone_conference_count"] = sa_conf.count()
        return context


class ConferenceSeriesDetail(DetailView):
    model = ConferenceSeries
    template_name = "conference_series_detail.html"
    context_object_name = "series"

    def get_member_conferences(self):
        return Conference.objects.filter(series_memberships__series=self.get_object())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["series_progress"] = annotate_single_series(
            self.get_member_conferences()
        )
        series_order_subquery = SeriesMembership.objects.filter(
            conference=OuterRef("pk"), series=self.get_object()
        ).order_by("number")
        context["conference_list"] = (
            self.get_member_conferences()
            .annotate(
                main_series=StringAgg(
                    "series_memberships__series__abbreviation",
                    delimiter=" / ",
                    distinct=True,
                ),
                n_works=Count("works", distinct=True),
                n_authors=Count("works__authors", distinct=True),
                series_order=Subquery(series_order_subquery.values("number")[:1]),
            )
            .order_by("series_order")
            .prefetch_related(
                "series_memberships",
                "series_memberships__series",
                "organizers",
                "country",
                "hosting_institutions",
                "hosting_institutions__country",
                "documents",
            )
        )
        context["series_list"] = conference_series_qs()
        return context


class StandaloneList(View):
    template_name = "conference_series_detail.html"

    def get_standalone_list(self):
        qs = (
            Conference.objects.filter(series__isnull=True)
            .annotate(
                main_series=StringAgg(
                    "series_memberships__series__abbreviation",
                    delimiter=" / ",
                    distinct=True,
                ),
                n_works=Count("works", distinct=True),
                n_authors=Count("works__authors", distinct=True),
            )
            .order_by("year", "short_title", "theme_title")
            .prefetch_related(
                "series_memberships",
                "series_memberships__series",
                "organizers",
                "country",
                "hosting_institutions",
                "hosting_institutions__country",
                "documents",
            )
        )
        return qs

    def get(self, request):
        faux_series = {
            "title": "Standalone Events",
            "notes": "Digital humanities events not belonging to a larger series, such symposia or workshops.",
            "n_conferences": self.get_standalone_list().count(),
        }
        context = {
            "conference_list": self.get_standalone_list(),
            "series": faux_series,
            "series_list": conference_series_qs(),
            "series_progress": annotate_single_series(self.get_standalone_list()),
        }
        return render(request, self.template_name, context)


def home_view(request):

    conference_count = Conference.objects.count()

    years_count = Conference.objects.aggregate(year_range=Max("year") - Min("year"))[
        "year_range"
    ]

    work_count = Work.objects.count()

    author_count = Author.objects.exclude(authorships__work__isnull=True).count()

    institution_count = Institution.objects.count()

    country_count = (
        Country.objects.filter(
            Q(institutions__affiliations__asserted_by__work__isnull=False)
            | Q(institutions__conferences__isnull=False)
            | Q(conferences__isnull=False)
        )
        .distinct()
        .count()
    )

    context = {
        "site": {
            "conference_count": conference_count,
            "years_count": years_count,
            "work_count": work_count,
            "author_count": author_count,
            "institution_count": institution_count,
            "country_count": country_count,
        }
    }

    return render(request, "index.html", context)


@user_is_staff
@transaction.atomic
def author_merge_view(request, author_id):

    author = get_object_or_404(Author, pk=author_id)

    if request.method == "GET":
        """
        Initial load of the merge form displays all the authorships of the current author that will be affected
        """
        context = {"merging": author, "author_merge_form": AuthorMergeForm}
        return render(request, "author_merge.html", context)

    elif request.method == "POST":
        """
        Posting the new author id causes all of the old author's authorships to be reassigned.
        """

        raw_form = AuthorMergeForm(request.POST)
        if raw_form.is_valid():
            target_author = raw_form.cleaned_data["into"]

            if author == target_author:
                """
                If the user chooses the existing author, don't merge, but instead error out.
                """
                messages.error(
                    request,
                    f"You cannot merge an author into themselves. Please select a different author.",
                )
                return redirect("author_merge", author_id=author_id)
            else:
                old_author_string = str(author)
                merge_results = author.merge(target_author)
                target_author.user_last_updated = request.user
                target_author.save()
                messages.success(
                    request,
                    f"Author {old_author_string} has been merged into {target_author}, and the old author entry has been deleted.",
                )
                messages.success(
                    request, f"{merge_results['update_results']} authorships updated"
                )
                return redirect("author_detail", author_id=target_author.pk)
        else:
            for error in raw_form.errors:
                messages.error(request, error)
            return render(request, "author_merge.html", context)


def field_required(field):
    if field.get_internal_type() in ("CharField", "TextField") and field.blank:
        return False
    if field.null:
        return False
    return True


def download_data(request):
    data_dictionary = []
    if request.user.is_authenticated:
        dt_config = settings.PRIVATE_DATA_TABLE_CONFIG
        zip_url = reverse("private_all_tables_download")
    else:
        dt_config = settings.PUBLIC_DATA_TABLE_CONFIG
        zip_url = reverse("public_all_tables_download")
    denormalized_url = reverse("works_download")
    denormalized_last_updated = datetime.fromtimestamp(
        getmtime(f"{settings.DATA_OUTPUT_PATH}/{settings.DENORMALIZED_WORKS_NAME}.zip")
    )

    for m in dt_config["CONFIGURATION"]:
        model = attrgetter(m["model"])(models)
        if "manual_model_description" in m:
            model_description = m["manual_model_description"]
        else:
            try:
                model_description = model.model_description
            except:
                model_description = None
        all_model_fields = [
            {
                "name": f.name,
                "relation": f.is_relation,
                "help_text": f.help_text,
                "related_model": str(f.related_model)
                .replace("<class 'abstracts.models.", "")
                .replace("'>", ""),
                "type": f.get_internal_type(),
                "required": field_required(f),
            }
            for f in model._meta.fields
            if not f.one_to_many and f.name not in m["exclude_fields"]
        ]
        if m.get("include_string", False):
            all_model_fields.append(
                {
                    "name": "label",
                    "relation": None,
                    "help_text": "General label for this object",
                    "related_model": None,
                    "type": "CharField",
                    "required": True,
                }
            )
        data_dictionary.append(
            {
                "model": m["model"],
                "model_description": model_description,
                "csv_name": m["csv_name"],
                "fields": all_model_fields,
            }
        )
    normalized_last_updated = datetime.fromtimestamp(
        getmtime(f"{settings.DATA_OUTPUT_PATH}/{dt_config['DATA_ZIP_NAME']}")
    )

    context = {
        "zip_url": zip_url,
        "denormalized_url": denormalized_url,
        "denormalized_last_updated": denormalized_last_updated,
        "normalized_last_updated": normalized_last_updated,
        "data_dictionary": data_dictionary,
        "denormalized_data_dictionary": settings.DENORMALIZED_HEADERS,
    }

    return render(request, "downloads.html", context)


def download_works_csv(request):
    target_zip = f"{settings.DATA_OUTPUT_PATH}/{settings.DENORMALIZED_WORKS_NAME}.zip"
    response = FileResponse(open(target_zip, "rb"))
    return response


def public_download_all_tables(request):
    target_zip = f"{settings.DATA_OUTPUT_PATH}/{settings.PUBLIC_DATA_TABLE_CONFIG['DATA_ZIP_NAME']}"
    response = FileResponse(open(target_zip, "rb"))
    return response


@login_required
def private_download_all_tables(request):
    target_zip = f"{settings.DATA_OUTPUT_PATH}/{settings.PRIVATE_DATA_TABLE_CONFIG['DATA_ZIP_NAME']}"
    response = FileResponse(open(target_zip, "rb"))
    return response


@login_required
def WorkCreate(request):

    if request.method == "GET":
        if "conference" in request.GET:
            conf = get_object_or_404(Conference, pk=int(request.GET["conference"]))
            work_form = WorkForm(initial={"conference": conf.pk})
        else:
            work_form = WorkForm()
    if request.method == "POST":
        work_form = WorkForm(request.POST)
        if work_form.is_valid():
            new_work = work_form.save()
            new_work.user_last_updated = request.user
            new_work.save()
            messages.success(request, f"{new_work} created.")
            return redirect("work_edit_authorship", work_id=new_work.pk)
        else:
            for err in work_form.errors:
                messages.error(request, err)

    context = {"work_form": work_form}
    return render(request, "work_create.html", context)


@login_required
def WorkEdit(request, work_id):
    work = get_object_or_404(Work, pk=work_id)

    if request.method == "POST":
        print(request.user)
        work_form = WorkForm(request.POST, instance=work)
        if work_form.is_valid():
            work.user_last_updated = request.user
            work_form.save()
            messages.success(request, f'"{work.title}" sucessfully updated.')
            return redirect("work_detail", work_id=work.pk)
        else:
            for f, e in work_form.errors.items():
                messages.error(request, f"{f}: {e}")

    work_initial_data = model_to_dict(work)
    context = {"work_form": WorkForm(initial=work_initial_data), "work": work}
    return render(request, "work_edit.html", context)


@login_required
@transaction.atomic
def WorkEditAuthorship(request, work_id):
    work = get_object_or_404(Work, pk=work_id)
    authorships = work.authorships.all()
    AuthorshipWorkFormset = formset_factory(
        WorkAuthorshipForm, can_delete=True, extra=0
    )

    initial_data = []

    for authorship in authorships:

        base_data = {
            "author": authorship.author,
            "authorship_order": authorship.authorship_order,
            "first_name": authorship.appellation.first_name,
            "last_name": authorship.appellation.last_name,
            "affiliations": [aff for aff in authorship.affiliations.all()],
        }

        initial_data.append(base_data)

    if request.method == "GET":
        authorships_forms = AuthorshipWorkFormset(initial=initial_data)
    elif request.method == "POST":
        authorships_forms = AuthorshipWorkFormset(request.POST)
        if authorships_forms.is_valid():
            for d_form in authorships_forms.deleted_forms:
                d_form_data = d_form.cleaned_data
                attached_author = d_form_data["author"]
                Authorship.objects.filter(
                    work=work, author=d_form_data["author"]
                ).delete()
                # Refresh the author in DB to update appellations index
                attached_author.save()
            for aform in authorships_forms:
                if aform not in authorships_forms.deleted_forms:
                    aform_data = aform.cleaned_data
                    appellation = Appellation.objects.get_or_create(
                        first_name=aform_data["first_name"],
                        last_name=aform_data["last_name"],
                    )[0]

                    affiliations = aform_data["affiliations"]
                    authorship_order = aform_data["authorship_order"]

                    try:
                        if aform_data["author"] is None:
                            author_id = Author.objects.create()
                        else:
                            author_id = aform_data["author"]
                        auth = Authorship.objects.update_or_create(
                            work=work,
                            author=author_id,
                            defaults={
                                "authorship_order": authorship_order,
                                "appellation": appellation,
                                "user_last_updated": request.user,
                            },
                        )[0]
                        author_id.user_last_updated = request.user
                        author_id.save()
                    except IntegrityError as e:
                        messages.error(
                            request, f"{e}: Ensure authorship order numbers are unique"
                        )
                        return redirect("work_edit_authorship", work.pk)

                    auth.affiliations.clear()
                    if affiliations is not None:
                        auth.affiliations.set(affiliations)

            messages.success(
                request, f'"{work.title}" authorships successfully updated.'
            )
            if "start_new" in request.POST:
                return redirect(
                    f"{reverse('work_create')}?conference={work.conference.pk}"
                )

            return redirect("work_detail", work_id=work.pk)
        else:
            for error in authorships_forms.errors:
                messages.error(request, error)

    context = {
        "authorships_form": authorships_forms,
        "work": work,
        "affiliation_form": AffiliationEditForm,
    }
    return render(request, "work_edit_authorships.html", context)


@login_required
def AuthorInfoJSON(request, author_id):
    if request.method == "GET":
        author = get_object_or_404(Author, pk=author_id)
        author_aff = Affiliation.objects.filter(asserted_by__author=author).distinct()
        author_dict = {
            "first_name": author.most_recent_appellation.first_name,
            "last_name": author.most_recent_appellation.last_name,
            "work_titles": [w.title for w in author.works.all()][:4],
            "works_count": author.works.count(),
        }
        if author_aff is not None:
            author_dict["affiliations"] = [
                {"name": str(aff), "id": aff.pk} for aff in author_aff
            ]
        return JsonResponse(author_dict)


@login_required
def AffiliationInfoJSON(request, affiliation_id):
    if request.method == "GET":
        affiliation = get_object_or_404(Affiliation, pk=affiliation_id)
        affiliation_dict = {
            "institution": {
                "name": str(affiliation.institution),
                "id": affiliation.institution.id,
            }
        }
        if affiliation.department is not None:
            affiliation_dict["department"] = affiliation.department
        return JsonResponse(affiliation_dict)


class WorkDelete(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Work
    template_name = "work_delete.html"
    extra_context = {"cancel_view": "work_list"}
    success_url = reverse_lazy("work_list")

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, f"'{self.get_object().title}' deleted")
        return super().delete(request, *args, **kwargs)


class FullWorkList(ListView):
    context_object_name = "work_list"
    template_name = "work_list.html"
    paginate_by = 10

    def get_queryset(self):
        base_result_set = Work.objects.all()
        raw_filter_form = WorkFilter(self.request.GET)

        if raw_filter_form.is_valid():
            result_set = base_result_set
            filter_form = raw_filter_form.cleaned_data

            work_type_res = filter_form["work_type"]
            if work_type_res is not None:
                result_set = result_set.filter(work_type=work_type_res)

            conference_res = filter_form["conference"]
            if conference_res is not None:
                result_set = result_set.filter(conference=conference_res)

            affiliation_res = filter_form["affiliation"]
            if len(affiliation_res) > 0:
                result_set = result_set.filter(
                    authorships__affiliations__in=affiliation_res
                ).distinct()

            institution_res = filter_form["institution"]
            if len(institution_res) > 0:
                result_set = result_set.filter(
                    authorships__affiliations__institution__in=institution_res
                ).distinct()

            author_res = filter_form["author"]
            if len(author_res) > 0:
                result_set = result_set.filter(authorships__author__in=author_res)

            keyword_res = filter_form["keywords"]
            if len(keyword_res) > 0:
                result_set = result_set.filter(keywords__in=keyword_res)

            topic_res = filter_form["topics"]
            if len(topic_res) > 0:
                result_set = result_set.filter(topics__in=topic_res)

            language_res = filter_form["languages"]
            if len(language_res) > 0:
                result_set = result_set.filter(languages__in=language_res)

            discipline_res = filter_form["disciplines"]
            if len(discipline_res) > 0:
                result_set = result_set.filter(disciplines__in=discipline_res)

            if filter_form["full_text_available"]:
                result_set = result_set.exclude(full_text="")

            if filter_form["full_text_viewable"]:
                result_set = result_set.exclude(full_text="").filter(
                    Q(full_text_license__isnull=False)
                    | Q(conference__full_text_public=True)
                )

            text_res = filter_form["text"]
            if text_res != "":
                result_set = (
                    result_set.annotate(
                        rank=SearchRank(F("search_text"), SearchQuery(text_res)),
                        # Does the search text show up only in the full text?
                        search_in_ft_only=ExpressionWrapper(
                            ~Q(title__icontains=text_res), output_field=BooleanField()
                        ),
                    )
                    .filter(rank__gt=0)
                    .order_by("-rank")
                )
                order_res = "rank"

            # To find the last name of the first author, we develop a subquery that will pull the first authorship for a given work. We can then call the appellation__last_name
            first_author_subquery = Authorship.objects.filter(
                work=OuterRef("pk")
            ).order_by("authorship_order")

            order_res = filter_form["ordering"]
            if order_res is None or order_res == "":
                order_res = "year"
            if order_res == "year":
                result_set = result_set.order_by("conference__year", "title")
            elif order_res == "-year":
                result_set = result_set.order_by("-conference__year", "title")
            elif order_res == "title":
                result_set = result_set.order_by("title")
            elif order_res == "-title":
                result_set = result_set.order_by("-title")
            elif order_res == "last_name":
                result_set = result_set.annotate(
                    first_author_last_name=Subquery(
                        first_author_subquery.values("appellation__last_name")[:1]
                    )
                ).order_by("first_author_last_name", "title")
            elif order_res == "-last_name":
                result_set = result_set.annotate(
                    first_author_last_name=Subquery(
                        first_author_subquery.values("appellation__last_name")[:1]
                    )
                ).order_by("-first_author_last_name", "title")

            return (
                result_set.select_related("conference", "work_type", "parent_session")
                .annotate(
                    main_series=StringAgg(
                        "conference__series_memberships__series__abbreviation",
                        delimiter=" / ",
                        distinct=True,
                    ),
                    main_institution=StringAgg(
                        "conference__hosting_institutions__name",
                        delimiter=" / ",
                        distinct=True,
                    ),
                )
                .prefetch_related(
                    "conference__organizers",
                    "conference__series_memberships",
                    "conference__series_memberships__series",
                    "session_papers",
                    "authorships",
                    "authorships__appellation",
                    "authorships__author",
                    "keywords",
                    "topics",
                    "languages",
                    "disciplines",
                )
            )
        else:
            for error in raw_filter_form.errors:
                messages.warning(self.request, error)
            return base_result_set

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        raw_filter_form = WorkFilter(self.request.GET)
        if raw_filter_form.is_valid():
            filter_form = raw_filter_form.cleaned_data
            conference_res = filter_form["conference"]
            if conference_res is not None:
                conferences_data = (
                    Conference.objects.filter(id=conference_res.id)
                    .annotate(
                        n_works=Count("works", distinct=True),
                        n_authors=Count("works__authors", distinct=True),
                        main_series=StringAgg(
                            "series_memberships__series__abbreviation",
                            delimiter=" / ",
                            distinct=True,
                        ),
                    )
                    .select_related("country")
                    .prefetch_related(
                        "organizers", "series_memberships", "series_memberships__series"
                    )
                    .all()
                )
                context["selected_conferences"] = conferences_data

        context["work_filter_form"] = WorkFilter(data=self.request.GET)
        context["available_works_count"] = Work.objects.count()
        context["filtered_works_count"] = self.get_queryset().count()
        context["redirect_url"] = reverse("work_list")
        return context


class FullInstitutionList(LoginRequiredMixin, ListView):
    context_object_name = "institution_list"
    template_name = "full_institution_list.html"
    paginate_by = 10

    def get_queryset(self):
        annotated_affiliations = Affiliation.objects.annotate(
            n_works=Count("asserted_by__work", distinct=True)
        )
        result_set = (
            Institution.objects.annotate(
                n_works=Count("affiliations__asserted_by__work", distinct=True)
            )
            .prefetch_related(
                Prefetch("affiliations", annotated_affiliations), "country"
            )
            .order_by("-n_works")
        )

        if self.request.GET:
            raw_filter_form = FullInstitutionForm(self.request.GET)
            if raw_filter_form.is_valid():
                filter_form = raw_filter_form.cleaned_data

                department_res = filter_form["department"]
                if department_res != "":
                    result_set = result_set.filter(
                        affiliations__department__icontains=department_res
                    )

                affiliation_res = filter_form["affiliation"]
                if affiliation_res is not None:
                    result_set = result_set.filter(affiliations=affiliation_res)

                institution_res = filter_form["institution"]
                if institution_res is not None:
                    result_set = result_set.filter(pk=institution_res.pk)

                country_res = filter_form["country"]
                if country_res is not None:
                    result_set = result_set.filter(country=country_res)

                if filter_form["no_department"]:
                    result_set = result_set.filter(affiliations__department="")

                if filter_form["ordering"] == "n_dsc":
                    result_set = result_set.order_by("-n_works")
                elif filter_form["ordering"] == "n_asc":
                    result_set = result_set.order_by("n_works")
                elif filter_form["ordering"] == "a":
                    result_set = result_set.order_by("affiliations__institution__name")
            else:
                for f, e in raw_filter_form.errors.items():
                    messages.error(self.request, f"{f}: {e}")

        return result_set

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["institution_filter_form"] = FullInstitutionForm(
            initial=self.request.GET
        )
        context["available_institutions_count"] = Institution.objects.count()
        context["filtered_institutions_count"] = self.get_queryset().count()
        context["redirect_url"] = reverse("full_institution_list")
        return context


class AuthorInstitutionList(FullInstitutionList):
    template_name = "author_institution_list.html"

    def get_queryset(self):
        base_result_set = Institution.objects.annotate(
            n_authors=Count("affiliations__asserted_by__author")
        ).distinct()
        result_set = base_result_set

        if self.request.GET:
            raw_filter_form = FullInstitutionForm(self.request.GET)
            if raw_filter_form.is_valid():
                filter_form = raw_filter_form.cleaned_data

                department_res = filter_form["department"]
                if department_res != "":
                    result_set = result_set.filter(
                        affiliations__department__icontains=department_res
                    )

                affiliation_res = filter_form["affiliation"]
                if affiliation_res is not None:
                    result_set = result_set.filter(affiliations=affiliation_res)

                institution_res = filter_form["institution"]
                if institution_res is not None:
                    result_set = result_set.filter(pk=institution_res.pk)

                country_res = filter_form["country"]
                if country_res is not None:
                    result_set = result_set.filter(country=country_res)

                if filter_form["no_department"]:
                    result_set = result_set.filter(affiliations__department="")

                if filter_form["ordering"] == "n_dsc":
                    result_set = result_set.order_by("-n_authors")
                elif filter_form["ordering"] == "n_asc":
                    result_set = result_set.order_by("n_authors")
                elif filter_form["ordering"] == "a":
                    result_set = result_set.order_by("affiliations__institution__name")
            else:
                for f, e in raw_filter_form.errors.items():
                    messages.error(self.request, f"{f}: {e}")
                result_set = base_result_set
        else:
            # Otherwise default to sorting by n_dsc
            result_set = result_set.order_by("-n_authors")

        return result_set.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["redirect_url"] = reverse("author_institution_list")
        return context


class InstitutionEdit(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Institution
    template_name = "generic_form.html"
    fields = ["name", "city", "state_province_region", "country"]
    extra_context = {
        "form_title": "Edit institution",
        "cancel_view": "full_institution_list",
        "merge_view": "institution_merge",
    }
    success_message = "%(name)s updated"
    success_url = reverse_lazy("full_institution_list")

    def form_valid(self, form):
        response = super(InstitutionEdit, self).form_valid(form)
        self.object.user_last_updated = self.request.user
        self.object.save()
        return response


class InstitutionCreate(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Institution
    template_name = "generic_form.html"
    fields = ["name", "city", "state_province_region", "country"]
    extra_context = {
        "form_title": "Create institution",
        "cancel_view": "full_institution_list",
    }
    success_message = "%(name)s created"
    success_url = reverse_lazy("full_institution_list")

    def form_valid(self, form):
        response = super(InstitutionCreate, self).form_valid(form)
        self.object.user_last_updated = self.request.user
        self.object.save()
        return response


@user_is_staff
@transaction.atomic
def institution_merge(request, institution_id):
    institution = get_object_or_404(Institution, pk=institution_id)
    context = {"merging": institution, "institution_merge_form": InstitutionMergeForm}

    if request.method == "GET":
        """
        Initial load of the merge form displays all the authors and works associated with this institution.
        """
        return render(request, "institution_merge.html", context)

    elif request.method == "POST":
        """
        Posting the new author id causes all of the old author's authorships to be reassigned.
        """

        raw_form = InstitutionMergeForm(request.POST)
        if raw_form.is_valid():
            target_institution = raw_form.cleaned_data["into"]

            if institution == target_institution:
                """
                If the user chooses the existing institution, don't merge, but instead error out.
                """
                messages.error(
                    request,
                    f"You cannot merge an institution into itself. Please select a different institution.",
                )
                return redirect("institution_merge", institution_id=institution_id)
            else:
                old_institution_id = str(institution)
                merge_results = institution.merge(target_institution)
                target_institution.user_last_updated = request.user
                target_institution.save()

                messages.success(
                    request,
                    f"Author {old_institution_id} has been merged into {target_institution}, and the old institution entry has been deleted.",
                )
                messages.success(
                    request, f"{merge_results['update_results']} affiliations updated"
                )
                return redirect("institution_edit", pk=target_institution.pk)
        else:
            for error in raw_form.errors:
                messages.error(request, error)
            return render(request, "institution_merge.html", context)


@user_is_staff
@transaction.atomic
def institution_multi_merge(request):
    context = {"form": InstitutionMultiMergeForm}

    if request.method == "POST":
        raw_form = InstitutionMultiMergeForm(request.POST)
        if raw_form.is_valid():
            target_institution = raw_form.cleaned_data["into"]
            source_institutions = raw_form.cleaned_data["sources"].exclude(
                pk=target_institution.pk
            )

            for institution in source_institutions:
                old_institution_id = str(institution)
                merge_results = institution.merge(target_institution)
                target_institution.user_last_updated = request.user
                target_institution.save()

                messages.success(
                    request,
                    f"Institution {old_institution_id} has been merged into {target_institution}, and the old institution entry has been deleted.",
                )
                messages.success(
                    request, f"{merge_results['update_results']} institutions updated"
                )
            return redirect("institution_edit", pk=target_institution.pk)
        else:
            for error in raw_form.errors:
                messages.error(request, error)

    return render(request, "institution_multi_merge.html", context)


class AffiliationEdit(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Affiliation
    template_name = "generic_form.html"
    form_class = AffiliationEditForm
    extra_context = {
        "form_title": "Edit affiliation",
        "cancel_view": "full_institution_list",
        "merge_view": "affiliation_merge",
    }
    success_message = "%(department)s updated"
    success_url = reverse_lazy("full_institution_list")


class AffiliationCreate(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Affiliation
    template_name = "generic_form.html"
    form_class = AffiliationEditForm
    extra_context = {
        "form_title": "Create affiliation",
        "cancel_view": "full_institution_list",
    }
    success_message = "%(department)s created"
    success_url = reverse_lazy("full_institution_list")

    def get_initial(self, **kwargs):
        super().get_initial(**kwargs)

        if "institution" in self.request.GET:
            self.initial = {"institution": int(self.request.GET["institution"])}

        return self.initial


@login_required
def ajax_affiliation_create(request):
    newaff = Affiliation.objects.get_or_create(
        department=request.POST["department"],
        institution=Institution.objects.get(pk=int(request.POST["institution"])),
    )[0]
    return JsonResponse({"name": str(newaff), "id": newaff.pk})


@user_is_staff
@transaction.atomic
def affiliation_merge(request, affiliation_id):
    affiliation = get_object_or_404(Affiliation, pk=affiliation_id)
    context = {"merging": affiliation, "affiliation_merge_form": AffiliationMergeForm}

    if request.method == "GET":
        """
        Initial load of the merge form displays all the authors and works associated with this affiliation.
        """
        return render(request, "affiliation_merge.html", context)

    elif request.method == "POST":
        """
        Posting the new author id causes all of the old author's authorships to be reassigned.
        """

        raw_form = AffiliationMergeForm(request.POST)
        if raw_form.is_valid():
            target_affiliation = raw_form.cleaned_data["into"]

            if affiliation == target_affiliation:
                """
                If the user chooses the existing affiliation, don't merge, but instead error out.
                """
                messages.error(
                    request,
                    f"You cannot merge an affiliation into itself. Please select a different affiliation.",
                )
                return redirect("affiliation_merge", affiliation_id=affiliation_id)
            else:
                old_affiliation_id = str(affiliation)
                merge_results = affiliation.merge(target_affiliation)

                messages.success(
                    request,
                    f"Affiliation {old_affiliation_id} has been merged into {target_affiliation}, and the old affiliation entry has been deleted.",
                )
                messages.success(
                    request, f"{merge_results['update_results']} affiliations updated"
                )
                return redirect("affiliation_edit", pk=target_affiliation.pk)
        else:
            for error in raw_form.errors:
                messages.error(request, error)
            return render(request, "affiliation_merge.html", context)


@user_is_staff
@transaction.atomic
def affiliation_multi_merge(request):
    context = {"form": AffiliationMultiMergeForm}

    if request.method == "POST":
        raw_form = AffiliationMultiMergeForm(request.POST)
        if raw_form.is_valid():
            target_affiliation = raw_form.cleaned_data["into"]
            source_affiliations = raw_form.cleaned_data["sources"].exclude(
                pk=target_affiliation.pk
            )

            for affiliation in source_affiliations:
                old_affiliation_id = str(affiliation)
                merge_results = affiliation.merge(target_affiliation)

                messages.success(
                    request,
                    f"Affiliation {old_affiliation_id} has been merged into {target_affiliation}, and the old affiliation entry has been deleted.",
                )
                messages.success(
                    request, f"{merge_results['update_results']} affiliations updated"
                )
            return redirect("affiliation_edit", pk=target_affiliation.pk)
        else:
            for error in raw_form.errors:
                messages.error(request, error)

    return render(request, "affiliation_multi_merge.html", context)


@user_is_staff
@transaction.atomic
def wipe_unused(request):
    deletion_dict = {
        "Author": Author.objects.exclude(authorships__isnull=False).distinct(),
        "Affiliation": Affiliation.objects.exclude(
            asserted_by__isnull=False
        ).distinct(),
        "Institution": Institution.objects.exclude(
            Q(affiliations__asserted_by__isnull=False) | Q(conferences__isnull=False)
        ).distinct(),
        "Keyword": Keyword.objects.exclude(works__isnull=False).distinct(),
        "Appellation": Appellation.objects.exclude(
            asserted_by__isnull=False
        ).distinct(),
    }

    if request.method == "POST":
        for k, v in deletion_dict.items():
            res = v.delete()
            if res[0] > 0:
                messages.success(request, f"{k}: {res[0]} objects deleted")

    any_hanging_items = any([v.exists() for k, v in deletion_dict.items()])
    context = {"deletions": deletion_dict, "hanging_items": any_hanging_items}

    return render(request, "wipe_unused.html", context)


class ConferenceCreate(StaffRequiredMixin, SuccessMessageMixin, CreateView):
    model = Conference
    template_name = "conference_create.html"
    form_class = ConferenceForm
    extra_context = {
        "form_title": "Create conference",
        "cancel_view": "conference_list",
    }
    success_message = "Conference '%(year)s - %(short_title)s' created"

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        form_instance = self.get_form()
        if form_instance.is_valid():
            for organizer in form_instance.cleaned_data["organizers"]:
                self.object.organizers.add(organizer)
            self.object.save()
            if "goto_abstracts" in request.POST:
                return redirect(reverse("work_list") + f"?conference={self.object.id}")
        else:
            for err in form_instance.errors:
                messages.error(request, err)
                return response


@user_is_staff
@transaction.atomic
def ConferenceEdit(request, pk):
    conference = get_object_or_404(Conference, pk=pk)
    # populate the conference form, including pulling in the related organizers
    conference_dict = model_to_dict(conference)
    conference_dict["organizers"] = conference.organizers.all()
    form = ConferenceForm(initial=conference_dict)
    ConferenceSeriesFormSet = formset_factory(
        ConferenceSeriesInline, can_delete=True, extra=0
    )
    initial_series = [
        {"series": memb.series, "number": memb.number}
        for memb in SeriesMembership.objects.filter(conference=conference).all()
    ]
    context = {
        "conference": conference,
        "form": form,
        "series_membership_form": ConferenceSeriesFormSet(initial=initial_series),
        "form_title": "Edit conference",
        "cancel_view": "conference_list",
    }
    if request.method == "POST":
        form = ConferenceForm(data=request.POST, instance=conference)
        if form.is_valid():
            clean_form = form.cleaned_data
            conference.year = clean_form["year"]
            conference.short_title = clean_form["short_title"]
            conference.notes = clean_form["notes"]
            conference.url = clean_form["url"]

            # Clear existing relations and update according to the form
            conference.organizers.clear()
            for organizer in clean_form["organizers"]:
                conference.organizers.add(organizer)
            conference.hosting_institutions.clear()
            for hosting_institution in clean_form["hosting_institutions"]:
                conference.hosting_institutions.add(hosting_institution)

            conference.save()

            series_forms = ConferenceSeriesFormSet(data=request.POST)
            if series_forms.is_valid():
                # Delete memberships first
                for d_form in series_forms.deleted_forms:
                    d_form_data = d_form.cleaned_data
                    SeriesMembership.objects.filter(
                        conference=conference,
                        series=d_form_data["series"],
                        number=d_form_data["number"],
                    ).delete()
                # Then update new ones
                for s_form in series_forms.forms:
                    if s_form not in series_forms.deleted_forms:
                        s_form_data = s_form.cleaned_data
                        SeriesMembership.objects.update_or_create(
                            conference=conference,
                            series=s_form_data["series"],
                            defaults={"number": s_form_data["number"]},
                        )
                messages.success(request, f"Conference {conference} updated.")
                if "goto_abstracts" in request.POST:
                    return redirect(
                        reverse("work_list") + f"?conference={conference.id}"
                    )
                if "goto_series" in request.POST:
                    first_series = conference.series.first()
                    if first_series is None:
                        return redirect("standalone_conferences")
                    else:
                        return redirect("conference_series_detail", pk=first_series.id)
                return redirect("conference_edit", pk=conference.pk)
            else:
                for f, e in series_forms.errors.items():
                    messages.error(request, f"{f}: {e}")
        else:
            for f, e in form.errors.items():
                messages.error(request, f"{f}: {e}")

    return render(request, "conference_edit.html", context)


class ConferenceDelete(StaffRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Conference
    template_name = "conference_delete.html"
    extra_context = {
        "form_title": "Delete conference",
        "cancel_view": "conference_list",
    }
    success_message = "Conference deleted"
    success_url = reverse_lazy("conference_list")

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(ConferenceDelete, self).delete(request, *args, **kwargs)


@login_required
@transaction.atomic
def conference_checkout(request, conference_id):
    conference = get_object_or_404(Conference, pk=conference_id)

    if request.method == "GET":
        """
        Load the current form and display current attached user
        """

        context = {
            "conference": conference,
            "form": ConferenceCheckoutForm(
                {"entry_status": conference.entry_status, "editing_user": "self"}
            ),
        }
        return render(request, "conference_checkout.html", context)
    elif request.method == "POST":
        """
        Get the form and update the status if the user has the authority to do so
        """

        raw_form = ConferenceCheckoutForm(request.POST)
        if raw_form.is_valid():
            clean_form = raw_form.cleaned_data
            if clean_form["entry_status"] == "c" and not request.user.is_staff:
                messages.error(
                    request,
                    "Only an administrator can mark this conference as completed.",
                )
                return redirect("conference_checkout", conference_id=conference.id)
            else:
                if clean_form["assign_user"] == "self":
                    conference.entry_status = clean_form["entry_status"]
                    conference.editing_user = request.user
                    conference.save()
                    messages.success(request, "Conference checked out")
                elif clean_form["assign_user"] == "clear":
                    conference.entry_status = clean_form["entry_status"]
                    conference.editing_user = None
                    conference.save()
                    messages.success(request, "Conference cleared")
                return redirect(reverse("work_list") + f"?conference={conference.id}")


class SeriesCreate(StaffRequiredMixin, SuccessMessageMixin, CreateView):
    model = ConferenceSeries
    template_name = "generic_form.html"
    extra_context = {
        "form_title": "Create conference series",
        "cancel_view": "conference_list",
    }
    fields = ["title", "abbreviation", "notes"]
    success_message = "Series '%(title)s' created"
    success_url = reverse_lazy("conference_list")


class SeriesEdit(StaffRequiredMixin, SuccessMessageMixin, UpdateView):
    model = ConferenceSeries
    template_name = "generic_form.html"
    extra_context = {
        "form_title": "Update conference series",
        "cancel_view": "conference_list",
    }
    fields = ["title", "abbreviation", "notes"]
    success_message = "Series '%(title)s' updated"
    success_url = reverse_lazy("conference_list")


class SeriesDelete(StaffRequiredMixin, SuccessMessageMixin, DeleteView):
    model = ConferenceSeries
    template_name = "generic_form.html"
    extra_context = {
        "form_title": "Delete conference series",
        "cancel_view": "conference_list",
    }
    success_message = "Series '%(title)s' deleted"
    success_url = reverse_lazy("conference_list")

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(SeriesDelete, self).delete(request, *args, **kwargs)


class OrganizerCreate(StaffRequiredMixin, SuccessMessageMixin, CreateView):
    model = Organizer
    template_name = "generic_form.html"
    extra_context = {
        "form_title": "Create conference organizer",
        "cancel_view": "full_organizer_list",
    }
    fields = ["name", "abbreviation", "conferences_organized", "notes", "url"]
    success_message = "Organizer '%(name)s' created"
    success_url = reverse_lazy("full_organizer_list")

    def form_valid(self, form):
        response = super(OrganizerCreate, self).form_valid(form)
        self.object.user_last_updated = self.request.user
        self.object.save()
        return response


class OrganizerEdit(StaffRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Organizer
    template_name = "generic_form.html"
    extra_context = {
        "form_title": "Update conference organizer",
        "cancel_view": "full_organizer_list",
    }
    fields = ["name", "abbreviation", "conferences_organized", "notes", "url"]
    success_message = "Organizer '%(name)s' updated"
    success_url = reverse_lazy("full_organizer_list")

    def form_valid(self, form):
        response = super(OrganizerEdit, self).form_valid(form)
        self.object.user_last_updated = self.request.user
        self.object.save()
        return response


class OrganizerDelete(StaffRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Organizer
    template_name = "generic_form.html"
    extra_context = {
        "form_title": "Delete organizer",
        "cancel_view": "full_organizer_list",
    }
    success_message = "Organizer %(name)s deleted."
    success_url = reverse_lazy("full_organizer_list")

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(OrganizerDelete, self).delete(request, *args, **kwargs)


class OrganizerList(LoginRequiredMixin, ListView):
    model = Organizer
    template_name = "full_organizer_list.html"
    context_object_name = "organizer_list"


class KeywordCreate(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Keyword
    template_name = "generic_form.html"
    extra_context = {"form_title": "Create keyword", "cancel_view": "full_keyword_list"}
    fields = ["title"]
    success_message = "Keyword '%(title)s' created"
    success_url = reverse_lazy("full_keyword_list")


class KeywordDelete(StaffRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Keyword
    template_name = "generic_form.html"
    extra_context = {"form_title": "Delete keyword", "cancel_view": "full_keyword_list"}
    success_message = "Keyword '%(title)s' deleted"
    success_url = reverse_lazy("full_keyword_list")

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(KeywordDelete, self).delete(request, *args, **kwargs)


class KeywordEdit(StaffRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Keyword
    template_name = "generic_form.html"
    extra_context = {
        "form_title": "Update keyword",
        "cancel_view": "full_keyword_list",
        "merge_view": "keyword_merge",
        "delete_view": "keyword_delete",
    }
    fields = ["title"]
    success_message = "Keyword '%(title)s' updated"
    success_url = reverse_lazy("full_keyword_list")


class KeywordList(LoginRequiredMixin, ListView):
    model = Keyword
    template_name = "tag_list.html"
    context_object_name = "tag_list"
    extra_context = {
        "tag_category": "Keywords",
        "tag_edit_view": "keyword_edit",
        "tag_create_view": "keyword_create",
        "tag_list_view": "full_keyword_list",
        "multi_merge": "keyword_multi_merge",
        "filter_param_name": "keyword",
    }

    def get_queryset(self):
        base_results_set = Keyword.objects.order_by("title")
        results_set = base_results_set.annotate(n_works=Count("works"))

        if self.request.GET:
            raw_filter_form = TagForm(self.request.GET)
            if raw_filter_form.is_valid():
                filter_form = raw_filter_form.cleaned_data

                if filter_form["name"] != "":
                    results_set = results_set.filter(
                        title__icontains=filter_form["name"]
                    )

                if filter_form["ordering"] == "a":
                    results_set = results_set.order_by("title")
                elif filter_form["ordering"] == "n_asc":
                    results_set = results_set.order_by("n_works")
                elif filter_form["ordering"] == "n_dsc":
                    results_set = results_set.order_by("-n_works")
            else:
                for f, e in raw_filter_form.errors.items():
                    messages.error(self.request, f"{f}: {e}")
        else:
            results_set = results_set.order_by("title")

        return results_set

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tag_filter_form"] = TagForm(initial=self.request.GET)
        context["filtered_tags_count"] = self.get_queryset().count()
        context["available_tags_count"] = Keyword.objects.count()
        return context


@user_is_staff
@transaction.atomic
def keyword_merge(request, keyword_id):
    keyword = get_object_or_404(Keyword, pk=keyword_id)
    affected_works = Work.objects.filter(keywords=keyword).all()
    sample_works = affected_works[:15]
    count_elements = affected_works.count() - 15
    context = {
        "merging": keyword,
        "tag_merge_form": KeywordMergeForm,
        "sample_elements": sample_works,
        "tag_category": "Keyword",
        "merge_view": "keyword_merge",
    }

    if request.method == "GET":
        """
        Initial load of the merge form displays all the authors and works associated with this keyword.
        """
        return render(request, "tag_merge.html", context)

    elif request.method == "POST":
        """
        Posting the new author id causes all of the old author's authorships to be reassigned.
        """

        raw_form = KeywordMergeForm(request.POST)
        if raw_form.is_valid():
            target_keyword = raw_form.cleaned_data["into"]

            if keyword == target_keyword:
                """
                If the user chooses the existing keyword, don't merge, but instead error out.
                """
                messages.error(
                    request,
                    f"You cannot merge a keyword into itself. Please select a different keyword.",
                )
                return redirect("keyword_merge", keyword_id=keyword_id)
            else:
                old_keyword_id = str(keyword)
                merge_results = keyword.merge(target_keyword)

                messages.success(
                    request,
                    f"Keyword {old_keyword_id} has been merged into {target_keyword}, and the old keyword entry has been deleted.",
                )
                messages.success(
                    request, f"{merge_results['update_results']} keywords updated"
                )
                return redirect("keyword_edit", pk=target_keyword.pk)
        else:
            for error in raw_form.errors:
                messages.error(request, error)
            return render(request, "tag_merge.html", context)


@user_is_staff
@transaction.atomic
def keyword_multi_merge(request):
    context = {
        "tag_merge_form": KeywordMultiMergeForm,
        "tag_category": "Keyword",
        "multi_merge_view": "keyword_multi_merge",
    }

    if request.method == "POST":
        """
        Posting the new author id causes all of the old author's authorships to be reassigned.
        """
        raw_form = KeywordMultiMergeForm(request.POST)
        if raw_form.is_valid():
            target_keyword = raw_form.cleaned_data["into"]
            source_keywords = raw_form.cleaned_data["sources"].exclude(
                pk=target_keyword.pk
            )

            for keyword in source_keywords:
                old_keyword_id = keyword.title
                merge_results = keyword.merge(target_keyword)
                messages.success(
                    request,
                    f"Keyword {old_keyword_id} has been merged into {target_keyword}, and the old keyword entry has been deleted.",
                )
                messages.success(
                    request, f"{merge_results['update_results']} keywords updated"
                )
            return redirect("keyword_edit", pk=target_keyword.pk)
        else:
            for error in raw_form.errors:
                messages.error(request, error)

    return render(request, "tag_multi_merge.html", context)


class TopicCreate(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Topic
    template_name = "generic_form.html"
    extra_context = {"form_title": "Create topic", "cancel_view": "full_topic_list"}
    fields = ["title"]
    success_message = "Topic '%(title)s' created"
    success_url = reverse_lazy("full_topic_list")


class TopicDelete(StaffRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Topic
    template_name = "generic_form.html"
    extra_context = {"form_title": "Delete topic", "cancel_view": "full_topic_list"}
    success_message = "Topic '%(title)s' deleted"
    success_url = reverse_lazy("full_topic_list")

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(TopicDelete, self).delete(request, *args, **kwargs)


class TopicEdit(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Topic
    template_name = "generic_form.html"
    extra_context = {
        "form_title": "Update topic",
        "cancel_view": "full_topic_list",
        "merge_view": "topic_merge",
        "delete_view": "topic_delete",
    }
    fields = ["title"]
    success_message = "Topic '%(title)s' updated"
    success_url = reverse_lazy("full_topic_list")


class TopicList(LoginRequiredMixin, ListView):
    model = Topic
    template_name = "tag_list.html"
    context_object_name = "tag_list"
    extra_context = {
        "tag_category": "Topics",
        "tag_edit_view": "topic_edit",
        "tag_create_view": "topic_create",
        "tag_filter_form": TagForm,
        "tag_list_view": "full_topic_list",
        "multi_merge": "topic_multi_merge",
        "filter_param_name": "topic",
    }

    def get_queryset(self):
        base_results_set = Topic.objects.order_by("title")
        results_set = base_results_set.annotate(n_works=Count("works"))

        raw_filter_form = TagForm(self.request.GET)
        if raw_filter_form.is_valid():
            filter_form = raw_filter_form.cleaned_data

            if filter_form["name"] != "":
                results_set = results_set.filter(title__icontains=filter_form["name"])

            if filter_form["ordering"] == "a":
                results_set = results_set.order_by("title")
            elif filter_form["ordering"] == "n_asc":
                results_set = results_set.order_by("n_works")
            elif filter_form["ordering"] == "n_dsc":
                results_set = results_set.order_by("-n_works")

        return results_set

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filtered_tags_count"] = self.get_queryset().count()
        context["available_tags_count"] = Topic.objects.count()
        return context


@user_is_staff
@transaction.atomic
def topic_merge(request, topic_id):
    topic = get_object_or_404(Topic, pk=topic_id)
    affected_elements = topic.works.all()
    count_elements = affected_elements.count() - 10
    sample_elements = affected_elements[:10]
    context = {
        "merging": topic,
        "tag_merge_form": TopicMergeForm,
        "tag_category": "Topic",
        "merge_view": "topic_merge",
        "sample_elements": sample_elements,
        "count_elements": count_elements,
    }

    if request.method == "GET":
        """
        Initial load of the merge form displays all the authors and works associated with this topic.
        """
        return render(request, "tag_merge.html", context)

    elif request.method == "POST":
        """
        Posting the new author id causes all of the old author's authorships to be reassigned.
        """

        raw_form = TopicMergeForm(request.POST)
        if raw_form.is_valid():
            target_topic = raw_form.cleaned_data["into"]

            if topic == target_topic:
                """
                If the user chooses the existing topic, don't merge, but instead error out.
                """
                messages.error(
                    request,
                    f"You cannot merge a topic into itself. Please select a different topic.",
                )
                return redirect("topic_merge", topic_id=topic_id)
            else:
                old_topic_id = str(topic)
                merge_results = topic.merge(target_topic)

                messages.success(
                    request,
                    f"Topic {old_topic_id} has been merged into {target_topic}, and the old topic entry has been deleted.",
                )
                messages.success(
                    request, f"{merge_results['update_results']} topics updated"
                )
                return redirect("topic_edit", pk=target_topic.pk)
        else:
            for error in raw_form.errors:
                messages.error(request, error)
            return render(request, "tag_merge.html", context)


@user_is_staff
@transaction.atomic
def topic_multi_merge(request):
    context = {
        "tag_merge_form": TopicMultiMergeForm,
        "tag_category": "Topic",
        "multi_merge_view": "topic_multi_merge",
    }

    if request.method == "POST":
        """
        Posting the new author id causes all of the old author's authorships to be reassigned.
        """
        raw_form = TopicMultiMergeForm(request.POST)
        if raw_form.is_valid():
            target_topic = raw_form.cleaned_data["into"]
            source_topics = raw_form.cleaned_data["sources"].exclude(pk=target_topic.pk)

            for topic in source_topics:
                old_topic_id = topic.title
                merge_results = topic.merge(target_topic)
                messages.success(
                    request,
                    f"Topic {old_topic_id} has been merged into {target_topic}, and the old topic entry has been deleted.",
                )
                messages.success(
                    request, f"{merge_results['update_results']} topics updated"
                )
            return redirect("topic_edit", pk=target_topic.pk)
        else:
            for error in raw_form.errors:
                messages.error(request, error)

    return render(request, "tag_multi_merge.html", context)


class LanguageCreate(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Language
    template_name = "generic_form.html"
    extra_context = {
        "form_title": "Create language",
        "cancel_view": "full_language_list",
    }
    fields = ["title"]
    success_message = "Language '%(title)s' created"
    success_url = reverse_lazy("full_language_list")


class LanguageDelete(StaffRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Language
    template_name = "generic_form.html"
    extra_context = {
        "form_title": "Delete language",
        "cancel_view": "full_language_list",
    }
    success_message = "Language '%(title)s' deleted"
    success_url = reverse_lazy("full_language_list")

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(LanguageDelete, self).delete(request, *args, **kwargs)


class LanguageEdit(StaffRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Language
    template_name = "generic_form.html"
    extra_context = {
        "form_title": "Update language",
        "cancel_view": "full_language_list",
        "merge_view": "language_merge",
        "delete_view": "language_delete",
    }
    fields = ["title"]
    success_message = "Language '%(title)s' updated"
    success_url = reverse_lazy("full_language_list")


class LanguageList(LoginRequiredMixin, ListView):
    model = Language
    template_name = "tag_list.html"
    context_object_name = "tag_list"
    extra_context = {
        "tag_category": "Languages",
        "tag_edit_view": "language_edit",
        "tag_create_view": "language_create",
        "tag_filter_form": TagForm,
        "tag_list_view": "full_language_list",
        "filter_param_name": "language",
    }

    def get_queryset(self):
        base_results_set = Language.objects.order_by("title")
        results_set = base_results_set.annotate(n_works=Count("works"))

        raw_filter_form = TagForm(self.request.GET)
        if raw_filter_form.is_valid():
            filter_form = raw_filter_form.cleaned_data

            if filter_form["name"] != "":
                results_set = results_set.filter(title__icontains=filter_form["name"])

            if filter_form["ordering"] == "a":
                results_set = results_set.order_by("title")
            elif filter_form["ordering"] == "n_asc":
                results_set = results_set.order_by("n_works")
            elif filter_form["ordering"] == "n_dsc":
                results_set = results_set.order_by("-n_works")

        return results_set

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filtered_tags_count"] = self.get_queryset().count()
        context["available_tags_count"] = Language.objects.count()
        return context


@user_is_staff
@transaction.atomic
def language_merge(request, language_id):
    language = get_object_or_404(Language, pk=language_id)
    affected_elements = language.works.all()
    count_elements = affected_elements.count() - 10
    sample_elements = affected_elements[:10]
    context = {
        "merging": language,
        "tag_merge_form": LanguageMergeForm,
        "tag_category": "Language",
        "merge_view": "language_merge",
        "sample_elements": sample_elements,
        "count_elements": count_elements,
    }

    if request.method == "GET":
        """
        Initial load of the merge form displays all the authors and works associated with this language.
        """
        return render(request, "tag_merge.html", context)

    elif request.method == "POST":
        """
        Posting the new author id causes all of the old author's authorships to be reassigned.
        """

        raw_form = LanguageMergeForm(request.POST)
        if raw_form.is_valid():
            target_language = raw_form.cleaned_data["into"]

            if language == target_language:
                """
                If the user chooses the existing language, don't merge, but instead error out.
                """
                messages.error(
                    request,
                    f"You cannot merge a language into itself. Please select a different language.",
                )
                return redirect("language_merge", language_id=language_id)
            else:
                old_language_id = str(language)
                merge_results = language.merge(target_language)

                messages.success(
                    request,
                    f"Language {old_language_id} has been merged into {target_language}, and the old language entry has been deleted.",
                )
                messages.success(
                    request, f"{merge_results['update_results']} languages updated"
                )
                return redirect("language_edit", pk=target_language.pk)
        else:
            for error in raw_form.errors:
                messages.error(request, error)
            return render(request, "tag_merge.html", context)


class DisciplineCreate(StaffRequiredMixin, SuccessMessageMixin, CreateView):
    model = Discipline
    template_name = "generic_form.html"
    extra_context = {
        "form_title": "Create discipline",
        "cancel_view": "full_discipline_list",
    }
    fields = ["title"]
    success_message = "Discipline '%(title)s' created"
    success_url = reverse_lazy("full_discipline_list")


class DisciplineDelete(StaffRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Discipline
    template_name = "generic_form.html"
    extra_context = {
        "form_title": "Delete discipline",
        "cancel_view": "full_discipline_list",
    }
    success_message = "Discipline '%(title)s' deleted"
    success_url = reverse_lazy("full_discipline_list")

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(DisciplineDelete, self).delete(request, *args, **kwargs)


class DisciplineEdit(StaffRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Discipline
    template_name = "generic_form.html"
    extra_context = {
        "form_title": "Update discipline",
        "cancel_view": "full_discipline_list",
        "merge_view": "discipline_merge",
        "delete_view": "discipline_delete",
    }
    fields = ["title"]
    success_message = "Discipline '%(title)s' updated"
    success_url = reverse_lazy("full_discipline_list")


class DisciplineList(LoginRequiredMixin, ListView):
    model = Discipline
    template_name = "tag_list.html"
    context_object_name = "tag_list"
    extra_context = {
        "tag_category": "Disciplines",
        "tag_edit_view": "discipline_edit",
        "tag_create_view": "discipline_create",
        "tag_filter_form": TagForm,
        "tag_list_view": "full_discipline_list",
        "filter_param_name": "discipline",
    }

    def get_queryset(self):
        base_results_set = Discipline.objects.order_by("title")
        results_set = base_results_set.annotate(n_works=Count("works"))

        raw_filter_form = TagForm(self.request.GET)
        if raw_filter_form.is_valid():
            filter_form = raw_filter_form.cleaned_data

            if filter_form["name"] != "":
                results_set = results_set.filter(title__icontains=filter_form["name"])

            if filter_form["ordering"] == "a":
                results_set = results_set.order_by("title")
            elif filter_form["ordering"] == "n_asc":
                results_set = results_set.order_by("n_works")
            elif filter_form["ordering"] == "n_dsc":
                results_set = results_set.order_by("-n_works")

        return results_set

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filtered_tags_count"] = self.get_queryset().count()
        context["available_tags_count"] = Discipline.objects.count()
        return context


@user_is_staff
@transaction.atomic
def discipline_merge(request, discipline_id):
    discipline = get_object_or_404(Discipline, pk=discipline_id)
    affected_elements = discipline.works.all()
    count_elements = affected_elements.count() - 10
    sample_elements = affected_elements[:10]
    context = {
        "merging": discipline,
        "tag_merge_form": DisciplineMergeForm,
        "tag_category": "Discipline",
        "merge_view": "discipline_merge",
        "sample_elements": sample_elements,
        "count_elements": count_elements,
    }

    if request.method == "GET":
        """
        Initial load of the merge form displays all the authors and works associated with this discipline.
        """
        return render(request, "tag_merge.html", context)

    elif request.method == "POST":
        """
        Posting the new author id causes all of the old author's authorships to be reassigned.
        """

        raw_form = DisciplineMergeForm(request.POST)
        if raw_form.is_valid():
            target_discipline = raw_form.cleaned_data["into"]

            if discipline == target_discipline:
                """
                If the user chooses the existing discipline, don't merge, but instead error out.
                """
                messages.error(
                    request,
                    f"You cannot merge a discipline into itself. Please select a different discipline.",
                )
                return redirect("discipline_merge", discipline_id=discipline_id)
            else:
                old_discipline_id = str(discipline)
                merge_results = discipline.merge(target_discipline)

                messages.success(
                    request,
                    f"Discipline {old_discipline_id} has been merged into {target_discipline}, and the old discipline entry has been deleted.",
                )
                messages.success(
                    request, f"{merge_results['update_results']} disciplines updated"
                )
                return redirect("discipline_edit", pk=target_discipline.pk)
        else:
            for error in raw_form.errors:
                messages.error(request, error)
            return render(request, "tag_merge.html", context)


class WorkTypeCreate(StaffRequiredMixin, SuccessMessageMixin, CreateView):
    model = WorkType
    template_name = "generic_form.html"
    extra_context = {
        "form_title": "Create work_type",
        "cancel_view": "full_work_type_list",
    }
    fields = ["title", "is_parent"]
    success_message = "Abstract type '%(title)s' created"
    success_url = reverse_lazy("full_work_type_list")


class WorkTypeDelete(StaffRequiredMixin, SuccessMessageMixin, DeleteView):
    model = WorkType
    template_name = "generic_form.html"
    extra_context = {
        "form_title": "Delete work_type",
        "cancel_view": "full_work_type_list",
    }
    success_message = "Abstract type '%(title)s' deleted"
    success_url = reverse_lazy("full_work_type_list")

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(WorkTypeDelete, self).delete(request, *args, **kwargs)


class WorkTypeEdit(StaffRequiredMixin, SuccessMessageMixin, UpdateView):
    model = WorkType
    template_name = "generic_form.html"
    extra_context = {
        "form_title": "Update abstract type",
        "cancel_view": "full_work_type_list",
        "merge_view": "work_type_merge",
        "delete_view": "work_type_delete",
    }
    fields = ["title", "is_parent"]
    success_message = "Abstract '%(title)s' updated"
    success_url = reverse_lazy("full_work_type_list")


class WorkTypeList(LoginRequiredMixin, ListView):
    model = WorkType
    template_name = "tag_list.html"
    context_object_name = "tag_list"
    extra_context = {
        "tag_category": "Abstract Types",
        "tag_edit_view": "work_type_edit",
        "tag_create_view": "work_type_create",
        "tag_filter_form": TagForm,
        "tag_list_view": "full_work_type_list",
        "filter_param_name": "work_type",
    }

    def get_queryset(self):
        base_results_set = WorkType.objects.order_by("title")
        results_set = base_results_set.annotate(n_works=Count("works"))

        raw_filter_form = TagForm(self.request.GET)
        if raw_filter_form.is_valid():
            filter_form = raw_filter_form.cleaned_data

            if filter_form["name"] != "":
                results_set = results_set.filter(title__icontains=filter_form["name"])

            if filter_form["ordering"] == "a":
                results_set = results_set.order_by("title")
            elif filter_form["ordering"] == "n_asc":
                results_set = results_set.order_by("n_works")
            elif filter_form["ordering"] == "n_dsc":
                results_set = results_set.order_by("-n_works")

        return results_set

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filtered_tags_count"] = self.get_queryset().count()
        context["available_tags_count"] = WorkType.objects.count()
        return context


@user_is_staff
@transaction.atomic
def work_type_merge(request, work_type_id):
    work_type = get_object_or_404(WorkType, pk=work_type_id)
    affected_elements = work_type.works.all()
    count_elements = affected_elements.count() - 10
    sample_elements = affected_elements[:10]
    context = {
        "merging": work_type,
        "tag_merge_form": WorkTypeMergeForm,
        "tag_category": "Abstract Type",
        "merge_view": "work_type_merge",
        "sample_elements": sample_elements,
        "count_elements": count_elements,
    }

    if request.method == "GET":
        """
        Initial load of the merge form displays all the authors and works associated with this work_type.
        """
        return render(request, "tag_merge.html", context)

    elif request.method == "POST":
        """
        Posting the new author id causes all of the old author's authorships to be reassigned.
        """

        raw_form = WorkTypeMergeForm(request.POST)
        if raw_form.is_valid():
            target_work_type = raw_form.cleaned_data["into"]

            if work_type == target_work_type:
                """
                If the user chooses the existing work_type, don't merge, but instead error out.
                """
                messages.error(
                    request,
                    f"You cannot merge a work_type into itself. Please select a different work_type.",
                )
                return redirect("work_type_merge", work_type_id=work_type_id)
            else:
                old_work_type_id = str(work_type)
                merge_results = work_type.merge(target_work_type)

                messages.success(
                    request,
                    f"WorkType {old_work_type_id} has been merged into {target_work_type}, and the old work_type entry has been deleted.",
                )
                messages.success(
                    request, f"{merge_results['update_results']} work_types updated"
                )
                return redirect("work_type_edit", pk=target_work_type.pk)
        else:
            for error in raw_form.errors:
                messages.error(request, error)
            return render(request, "tag_merge.html", context)
