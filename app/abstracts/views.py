from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import DetailView, ListView
from django.db.models import Count, Max, Min, Q
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models.functions import Coalesce
from django.contrib.postgres.search import SearchVector
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from dal.autocomplete import Select2QuerySetView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.db import transaction
from django.forms.models import model_to_dict
from django.forms import formset_factory, inlineformset_factory, modelformset_factory


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
    FullAuthorFilter,
    FullWorkForm,
    FullInstitutionForm,
)


class InstitutionAutocomplete(Select2QuerySetView):
    def get_queryset(self):
        qs = Institution.objects.filter(
            affiliations__asserted_by__work__state="ac"
        ).distinct()

        if self.q:
            qs = qs.filter(
                Q(name__icontains=self.q) | Q(country__names__name__icontains=self.q)
            ).distinct()

        return qs


class KeywordAutocomplete(Select2QuerySetView):
    def get_queryset(self):
        qs = Keyword.objects.filter(works__state="ac").distinct()

        if self.q:
            qs = qs.filter(works__state="ac", title__icontains=self.q).distinct()

        return qs


class TopicAutocomplete(Select2QuerySetView):
    def get_queryset(self):
        qs = Topic.objects.filter(works__state="ac").distinct()

        if self.q:
            qs = qs.filter(title__icontains=self.q).distinct()

        return qs


class LanguageAutocomplete(Select2QuerySetView):
    def get_queryset(self):
        qs = Language.objects.filter(works__state="ac").distinct()

        if self.q:
            qs = qs.filter(title__icontains=self.q).distinct()

        return qs


class DisciplineAutocomplete(Select2QuerySetView):
    def get_queryset(self):
        qs = Discipline.objects.filter(works__state="ac").distinct()

        if self.q:
            qs = qs.filter(title__icontains=self.q).distinct()

        return qs


class CountryAutocomplete(Select2QuerySetView):
    def get_queryset(self):
        qs = Country.objects.filter(
            institutions__affiliations__asserted_by__work__state="ac"
        ).distinct()

        if self.q:
            qs = qs.filter(names__name__icontains=self.q).distinct()

        return qs


class AuthorAutocomplete(Select2QuerySetView):
    def get_queryset(self):
        qs = Author.objects.filter(works__state="ac").distinct()

        if self.q:
            qs = qs.filter(
                Q(appellations__first_name__icontains=self.q)
                | Q(appellations__last_name__icontains=self.q)
            ).distinct()

        return qs


class UnrestrictedWorkAutocomplete(LoginRequiredMixin, Select2QuerySetView):
    raise_exception = True

    def get_queryset(self):
        qs = Work.objects.all()

        if self.q:
            qs = qs.filter(title__icontains=self.q).all()

        return qs


class UnrestrictedAppellationAutocomplete(LoginRequiredMixin, Select2QuerySetView):
    raise_exception = True

    def get_queryset(self):
        qs = Appellation.objects.all()

        if self.q:
            qs = qs.filter(
                Q(first_name__icontains=self.q) | Q(last_name__icontains=self.q)
            ).all()

        return qs


class UnrestrictedKeywordAutocomplete(LoginRequiredMixin, Select2QuerySetView):
    raise_exception = True

    def get_queryset(self):
        qs = Keyword.objects.all()

        if self.q:
            qs = qs.filter(title__icontains=self.q).all()

        return qs


class UnrestrictedLanguageAutocomplete(LoginRequiredMixin, Select2QuerySetView):
    raise_exception = True

    def get_queryset(self):
        qs = Language.objects.all()

        if self.q:
            qs = qs.filter(title__icontains=self.q).all()

        return qs


class UnrestrictedTopicAutocomplete(LoginRequiredMixin, Select2QuerySetView):
    raise_exception = True

    def get_queryset(self):
        qs = Topic.objects.all()

        if self.q:
            qs = qs.filter(title__icontains=self.q).all()

        return qs


class UnrestrictedDisciplineAutocomplete(LoginRequiredMixin, Select2QuerySetView):
    raise_exception = True

    def get_queryset(self):
        qs = Discipline.objects.all()

        if self.q:
            qs = qs.filter(title__icontains=self.q).all()

        return qs


class UnrestrictedCountryAutocomplete(LoginRequiredMixin, Select2QuerySetView):
    raise_exception = True

    def get_queryset(self):
        qs = Country.objects.all()

        if self.q:
            qs = qs.filter(
                Q(pref_name__icontains=self.q) | Q(names__name__icontains=self.q)
            ).distinct()

        return qs


class UnrestrictedInstitutionAutocomplete(LoginRequiredMixin, Select2QuerySetView):
    raise_exception = True

    def get_queryset(self):
        qs = Institution.objects.all()

        if self.q:
            qs = qs.filter(name__icontains=self.q).all()

        return qs


class UnrestrictedAffiliationAutocomplete(LoginRequiredMixin, Select2QuerySetView):
    raise_exception = True

    def get_queryset(self):
        qs = Affiliation.objects.all()

        if self.q:
            qs = qs.filter(
                Q(department__icontains=self.q) | Q(institution__name__icontains=self.q)
            ).distinct()

        return qs


class UnrestrictedAuthorAutocomplete(LoginRequiredMixin, Select2QuerySetView):
    raise_exception = True

    def get_queryset(self):
        qs = Author.objects.all()

        if self.q:
            qs = qs.filter(
                Q(appellations__last_name__icontains=self.q)
                | Q(appellations__first_name__icontains=self.q)
            ).distinct()

        return qs


class WorkList(ListView):
    context_object_name = "work_list"
    template_name = "work_list.html"
    paginate_by = 10

    def get_queryset(self):
        base_result_set = Work.objects.filter(state="ac").order_by("title").distinct()

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

            institution_res = filter_form["institution"]
            if institution_res is not None:
                result_set = result_set.filter(
                    authorships__affiliations__institution=institution_res
                )

            keyword_res = filter_form["keyword"]
            if keyword_res is not None:
                result_set = result_set.filter(keywords=keyword_res)

            topic_res = filter_form["topic"]
            if topic_res is not None:
                result_set = result_set.filter(topics=topic_res)

            language_res = filter_form["topic"]
            if language_res is not None:
                result_set = result_set.filter(languages=language_res)

            discipline_res = filter_form["discipline"]
            if discipline_res is not None:
                result_set = result_set.filter(disciplines=discipline_res)

            if filter_form["full_text_available"]:
                result_set = result_set.exclude(full_text="")

            text_res = filter_form["text"]
            if text_res != "":
                result_set = result_set.filter(search_text=text_res)

            return result_set.distinct()
        else:
            for error in raw_filter_form.errors:
                messages.warning(self.request, error)
            return base_result_set

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["work_filter_form"] = WorkFilter(data=self.request.GET)
        context["available_works_count"] = Work.objects.filter(state="ac").count()
        context["filtered_works_count"] = self.get_queryset().count()
        context["redirect_url"] = reverse("work_list")
        return context


def work_view(request, work_id):
    work = get_object_or_404(Work, pk=work_id)

    # If work is unaccepted and the user isn't authenticated, boot them back to the homepage
    if work.state != "ac" and not request.user.is_authenticated:
        messages.error(
            request,
            f"Work ID {work.pk} isn't public yet. Please <a href='/admin/login'>log in</a> to continue.",
        )
        return redirect("work_list")
    else:
        authorships = work.authorships.order_by("authorship_order")
        context = {"work": work, "authorships": authorships}
        return render(request, "work_detail.html", context)


def author_view(request, author_id):
    author = get_object_or_404(Author, pk=author_id)

    if (
        not author.works.filter(state="ac").exists()
        and not request.user.is_authenticated
    ):
        messages.error(
            request,
            f"Author ID {author.pk} isn't public yet. Please <a href='/admin/login'>log in</a> to continue.",
        )
        return redirect("author_list")
    else:
        obj_authorships = author.public_authorships

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
                    authorships__in=obj_authorships.filter(appellation=a)
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

        author_admin_page = reverse("admin:abstracts_author_change", args=(author.pk,))

        context = {
            "author": author,
            "split_works": split_works,
            "appellation_assertions": appellation_assertions,
            "affiliation_assertions": affiliation_assertions,
            "author_admin_page": author_admin_page,
        }

        return render(request, "author_detail.html", context)


class AuthorList(ListView):
    context_object_name = "author_list"
    template_name = "author_list.html"
    paginate_by = 10

    def get_queryset(self):
        base_result_set = Author.objects.filter(works__state="ac")
        raw_filter_form = AuthorFilter(self.request.GET)

        if raw_filter_form.is_valid():
            result_set = base_result_set
            filter_form = raw_filter_form.cleaned_data

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
            if name_res is not None:
                result_set = result_set.filter(
                    Q(appellations__first_name__icontains=name_res)
                    | Q(appellations__last_name__icontains=name_res)
                )

            return result_set.order_by("id").distinct()
        else:
            messages.warning(
                self.request,
                "Query parameters not recognized. Check your URL and try again.",
            )
            return base_result_set

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["author_filter_form"] = AuthorFilter(data=self.request.GET)
        context["available_authors_count"] = (
            Author.objects.filter(works__state="ac").distinct().count()
        )
        context["filtered_authors_count"] = self.get_queryset().count()
        context["redirect_url"] = reverse("author_list")
        return context


def ConferenceList(request):
    context_object_name = "conference_list"
    template_name = "conference_list.html"

    affiliated_conferences = ConferenceSeries.objects.filter(
        conferences__works__state="ac"
    ).distinct()

    unaffiliated_conferences = Conference.objects.filter(
        works__state="ac", series__isnull=True
    ).distinct()

    context = {
        "conference_list": affiliated_conferences,
        "standalone_conferences": unaffiliated_conferences,
    }

    return render(request, "conference_list.html", context)


def home_view(request):
    public_works = Work.objects.filter(state="ac").distinct()

    conference_count = (
        Conference.objects.filter(works__in=public_works)
        .values_list("year")
        .distinct()
        .count()
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


@login_required
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
                author.merge(target_author)

                messages.success(
                    request,
                    f"Author {old_author_string} has been merged into {target_author}, and the old author entry has been deleted.",
                )
                return redirect("author_detail", author_id=target_author.pk)
        else:
            for error in raw_form.errors:
                messages.error(request, error)
            return render(request, "author_merge.html", context)


@login_required
def download_data(request):

    context = {
        "downloads": ["works.csv", "authorships.csv", "affiliations.csv", "full.json"]
    }

    return render(request, "downloads.html", context)


@login_required
def WorkEdit(request, work_id):
    work = get_object_or_404(Work, pk=work_id)

    if request.method == "GET":
        work_initial_data = model_to_dict(work)
        context = {"work_form": WorkForm(initial=work_initial_data), "work": work}
        return render(request, "work_edit.html", context)
    elif request.method == "POST":
        work_form = WorkForm(request.POST, instance=work)
        if work_form.is_valid():
            work_form.save()
            messages.success(request, f'"{work.title}" sucessfully updated.')
            return redirect("work_detail", work_id=work.pk)
        else:
            messages.error(request, "This form is invalid.")
            return redirect("work_edit", work_id=work_id)

    # form_class = WorkForm
    # template_name = "work_edit.html"
    # success_message = "%(title)s was updated successfully"


@login_required
@transaction.atomic
def WorkEditAuthorship(request, work_id):
    work = get_object_or_404(Work, pk=work_id)
    authorships = work.authorships.all()
    AuthorshipWorkFormset = formset_factory(WorkAuthorshipForm, extra=0)
    initial_data = [
        {
            "author": authorship.author,
            "authorship_order": authorship.authorship_order,
            "first_name": authorship.appellation.first_name,
            "last_name": authorship.appellation.last_name,
            "affiliation": authorship.affiliations.first(),
            "department": authorship.affiliations.first().department,
            "institution": authorship.affiliations.first().institution,
            "country": authorship.affiliations.first().institution.country,
            "genders": [a for a in authorship.genders.all()],
        }
        for authorship in authorships
    ]
    if request.method == "GET":
        authorships_forms = AuthorshipWorkFormset(initial=initial_data)
    elif request.method == "POST":
        authorships_forms = AuthorshipWorkFormset(request.POST, initial=initial_data)
        if authorships_forms.is_valid():
            for aform in authorships_forms:
                aform_data = aform.cleaned_data
                appellation = Appellation.objects.get_or_create(
                    first_name=aform_data["first_name"],
                    last_name=aform_data["last_name"],
                )[0]

                if aform_data["affiliation"] is not None:
                    affiliation = aform_data["affiliation"]
                else:
                    affiliation = Affiliation.objects.get_or_create(
                        department=aform_data["department"],
                        institution=aform_data["institution"],
                    )[0]

                genders = aform_data["genders"]

                authorship_order = aform_data["authorship_order"]

                auth = Authorship.objects.update_or_create(
                    work=work,
                    author=aform_data["author"],
                    defaults={
                        "authorship_order": authorship_order,
                        "appellation": appellation,
                    },
                )[0]

                auth.affiliations.set([affiliation])
                auth.genders.set(genders)
            messages.success(
                request, f'"{work.title}" authorships sucessfully updated.'
            )
            return redirect("work_detail", work_id=work.pk)
        else:
            for error in authorships_forms.errors:
                messages.error(request, error)

    context = {"authorships_form": authorships_forms, "work": work}
    return render(request, "work_edit_authorships.html", context)


class FullAuthorList(LoginRequiredMixin, ListView):
    context_object_name = "author_list"
    template_name = "author_list.html"
    paginate_by = 10

    def get_queryset(self):
        base_result_set = Author.objects.all()
        raw_filter_form = FullAuthorFilter(self.request.GET)
        if raw_filter_form.is_valid():
            filter_form = raw_filter_form.cleaned_data
            result_set = base_result_set

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
            if name_res is not None:
                result_set = result_set.filter(
                    Q(appellations__first_name__icontains=name_res)
                    | Q(appellations__last_name__icontains=name_res)
                )

            first_name_res = filter_form["first_name"]
            if first_name_res is not None:
                result_set = result_set.filter(
                    appellations__first_name__icontains=first_name_res
                )

            last_name_res = filter_form["last_name"]
            if last_name_res is not None:
                result_set = result_set.filter(
                    appellations__last_name__icontains=last_name_res
                )

            return result_set.order_by("id").distinct()
        else:
            messages.warning(
                self.request,
                "Query parameters not recognized. Check your URL and try again.",
            )
            return base_result_set

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["author_filter_form"] = FullAuthorFilter(data=self.request.GET)
        context["available_authors_count"] = Author.objects.count()
        context["filtered_authors_count"] = self.get_queryset().count()
        context["redirect_url"] = reverse("full_author_list")
        return context


class FullWorkList(LoginRequiredMixin, ListView):
    context_object_name = "work_list"
    template_name = "work_list.html"
    paginate_by = 10

    def get_queryset(self):
        base_result_set = Work.objects.order_by("title").all()
        raw_filter_form = FullWorkForm(self.request.GET)

        if raw_filter_form.is_valid():
            result_set = base_result_set
            filter_form = raw_filter_form.cleaned_data

            state_res = filter_form["state"]
            if state_res != "":
                result_set = result_set.filter(state=state_res)

            work_type_res = filter_form["work_type"]
            if work_type_res is not None:
                result_set = result_set.filter(work_type=work_type_res)

            conference_res = filter_form["conference"]
            if conference_res is not None:
                result_set = result_set.filter(conference=conference_res)

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

            keyword_res = filter_form["keyword"]
            if keyword_res is not None:
                result_set = result_set.filter(keywords=keyword_res)

            topic_res = filter_form["topic"]
            if topic_res is not None:
                result_set = result_set.filter(topics=topic_res)

            language_res = filter_form["topic"]
            if language_res is not None:
                result_set = result_set.filter(languages=language_res)

            discipline_res = filter_form["discipline"]
            if discipline_res is not None:
                result_set = result_set.filter(disciplines=discipline_res)

            if filter_form["full_text_available"]:
                result_set = result_set.exclude(full_text="")

            text_res = filter_form["text"]
            if text_res != "":
                result_set = result_set.filter(search_text=text_res)

            n_author_res = filter_form["n_authors"]
            if n_author_res is not None:
                result_set = result_set.annotate(n_authors=Count("authorships")).filter(
                    n_authors=n_author_res
                )

            return result_set.distinct()
        else:
            for error in raw_filter_form.errors:
                messages.warning(self.request, error)
            return base_result_set

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["work_filter_form"] = FullWorkForm(data=self.request.GET)
        context["available_works_count"] = Work.objects.count()
        context["filtered_works_count"] = self.get_queryset().count()
        context["redirect_url"] = reverse("full_work_list")
        return context


class FullInstitutionList(LoginRequiredMixin, ListView):
    context_object_name = "institution_list"
    template_name = "institution_list.html"
    paginate_by = 10

    def get_queryset(self):
        base_result_set = Institution.objects.all()
        raw_filter_form = FullInstitutionForm(self.request.GET)
        if raw_filter_form.is_valid():
            filter_form = raw_filter_form.cleaned_data
            result_set = base_result_set

            department_res = filter_form["department"]
            if department_res != "":
                result_set = result_set.filter(
                    affiliations__department__icontains=department_res
                )

            institution_res = filter_form["institution"]
            if institution_res is not None:
                result_set = result_set.filter(pk=institution_res.pk)

            country_res = filter_form["country"]
            if country_res is not None:
                result_set = result_set.filter(country=country_res)

            if filter_form["no_department"]:
                result_set = result_set.filter(affiliations__department="")

            return result_set.distinct()
        else:
            messages.warning(
                self.request,
                "Query parameters not recognized. Check your URL and try again.",
            )
            return base_result_set

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["institution_filter_form"] = FullInstitutionForm(data=self.request.GET)
        context["available_institutions_count"] = Institution.objects.count()
        context["filtered_institutions_count"] = self.get_queryset().count()
        context["redirect_url"] = reverse("full_institution_list")
        return context
