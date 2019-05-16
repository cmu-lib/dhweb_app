from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
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
    FullAuthorFilter,
    FullWorkForm,
    FullInstitutionForm,
    InstitutionMergeForm,
    AffiliationEditForm,
    AffiliationMergeForm,
    KeywordMergeForm,
    TagForm,
    TopicMergeForm,
    AffiliationMultiMergeForm,
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


class AffiliationAutocomplete(Select2QuerySetView):
    def get_queryset(self):
        qs = Affiliation.objects.filter(asserted_by__work__state="ac").distinct()

        if self.q:
            qs = qs.filter(
                Q(department__icontains=self.q) | Q(institution__name__icontains=self.q)
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
        qs = Affiliation.objects.annotate(n_works=Count("asserted_by__work")).order_by(
            "-n_works"
        )

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


class PublicWorkList(ListView):
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

            language_res = filter_form["language"]
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


class PublicAuthorList(ListView):
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


def PublicConferenceList(request):
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
                merge_results = author.merge(target_author)

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


@login_required
def download_data(request):

    context = {
        "downloads": ["works.csv", "authorships.csv", "affiliations.csv", "full.json"]
    }

    return render(request, "downloads.html", context)


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


@login_required
@transaction.atomic
def WorkEditAuthorship(request, work_id):
    work = get_object_or_404(Work, pk=work_id)
    authorships = work.authorships.all()
    AuthorshipWorkFormset = formset_factory(WorkAuthorshipForm, extra=5)

    initial_data = []

    for authorship in authorships:

        base_data = {
            "author": authorship.author,
            "authorship_order": authorship.authorship_order,
            "first_name": authorship.appellation.first_name,
            "last_name": authorship.appellation.last_name,
            "genders": [a for a in authorship.genders.all()],
        }

        if authorship.affiliations.exists():
            first_affiliation = authorship.affiliations.first()
            base_data["affiliation"]: first_affiliation
            base_data["department"]: first_affiliation.department
            base_data["institution"]: first_affiliation.institution
            base_data["country"]: first_affiliation.institution.country

        initial_data.append(base_data)

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
            if "start_new" in request.POST:
                return redirect(
                    "work_create", kwargs={"conference": work.conference.pk}
                )

            return redirect("work_detail", work_id=work.pk)
        else:
            for error in authorships_forms.errors:
                messages.error(request, error)

    context = {"authorships_form": authorships_forms, "work": work}
    return render(request, "work_edit_authorships.html", context)


@login_required
def AuthorInfoJSON(request, author_id):
    if request.method == "GET":
        author = get_object_or_404(Author, pk=author_id)
        author_aff = author.most_recent_affiliation
        author_dict = {
            "first_name": author.most_recent_appellation.first_name,
            "last_name": author.most_recent_appellation.last_name,
        }
        if author_aff is not None:
            author_dict["affiliation"] = {"name": str(author_aff), "id": author_aff.pk}
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
    extra_context = {"cancel_view": "full_work_list"}
    success_url = reverse_lazy("full_work_list")
    success_message = "%(id)s deleted."

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(WorkDelete, self).delete(request, *args, **kwargs)


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

            language_res = filter_form["language"]
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
    template_name = "full_institution_list.html"
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

            result_set = result_set.distinct()
        else:
            messages.warning(
                self.request,
                "Query parameters not recognized. Check your URL and try again.",
            )
            result_set = base_result_set

        return result_set.annotate(
            n_works=Count("affiliations__asserted_by__work")
        ).order_by("-n_works")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["institution_filter_form"] = FullInstitutionForm(data=self.request.GET)
        context["available_institutions_count"] = Institution.objects.count()
        context["filtered_institutions_count"] = self.get_queryset().count()
        context["redirect_url"] = reverse("full_institution_list")
        return context


class InstitutionEdit(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Institution
    template_name = "generic_form.html"
    fields = ["name", "city", "country"]
    extra_context = {
        "form_title": "Edit institution",
        "cancel_view": "full_institution_list",
        "merge_view": "institution_merge",
    }
    success_message = "%(name)s updated"
    success_url = reverse_lazy("full_institution_list")


class InstitutionCreate(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Institution
    template_name = "generic_form.html"
    fields = ["name", "city", "country"]
    extra_context = {
        "form_title": "Create institution",
        "cancel_view": "full_institution_list",
    }
    success_message = "%(name)s created"
    success_url = reverse_lazy("full_institution_list")


@login_required
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


@login_required
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


@login_required
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


@login_required
@transaction.atomic
def wipe_unused(request):
    deletion_dict = {
        "Author": Author.objects.filter(authorships__isnull=True).distinct(),
        "Affiliation": Affiliation.objects.filter(asserted_by__isnull=True).distinct(),
        "Institution": Institution.objects.filter(
            affiliations__asserted_by__isnull=True
        ).distinct(),
        "Keyword": Keyword.objects.filter(works__isnull=True).distinct(),
        "Topic": Topic.objects.filter(works__isnull=True).distinct(),
        "Appellation": Appellation.objects.filter(asserted_by__isnull=True).distinct(),
        "Series": ConferenceSeries.objects.filter(conferences__isnull=True).distinct(),
        "Conferences": Conference.objects.filter(works__isnull=True).distinct(),
    }

    if request.method == "POST":
        for k, v in deletion_dict.items():
            res = v.delete()
            if res[0] > 0:
                messages.success(request, f"{k}: {res[0]} objects deleted")

    any_hanging_items = any([v.exists() for k, v in deletion_dict.items()])
    context = {"deletions": deletion_dict, "hanging_items": any_hanging_items}

    return render(request, "wipe_unused.html", context)


class ConferenceCreate(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Conference
    template_name = "generic_form.html"
    extra_context = {
        "form_title": "Create conference",
        "cancel_view": "full_conference_list",
    }
    fields = ["year", "venue", "venue_abbreviation", "series", "notes", "url"]
    success_message = "Conference '%(year)s - %(venue)s' created"


class ConferenceList(LoginRequiredMixin, ListView):
    model = Conference
    template_name = "full_conference_list.html"
    context_object_name = "conference_list"


class ConferenceEdit(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Conference
    template_name = "generic_form.html"
    extra_context = {
        "form_title": "Edit conference",
        "cancel_view": "full_conference_list",
    }
    fields = ["year", "venue", "venue_abbreviation", "series", "notes", "url"]
    success_message = "Conference '%(year)s - %(venue)s' updated"


class ConferenceDelete(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Conference
    template_name = "conference_delete.html"
    extra_context = {
        "form_title": "Delete conference",
        "cancel_view": "full_conference_list",
    }
    success_message = "Conference deleted"
    success_url = reverse_lazy("full_conference_list")

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(ConferenceDelete, self).delete(request, *args, **kwargs)


class SeriesCreate(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = ConferenceSeries
    template_name = "generic_form.html"
    extra_context = {
        "form_title": "Create conference series",
        "cancel_view": "full_series_list",
    }
    fields = ["title", "abbreviation", "notes"]
    success_message = "Series '%(title)s' created"
    success_url = reverse_lazy("full_series_list")


class SeriesEdit(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = ConferenceSeries
    template_name = "generic_form.html"
    extra_context = {
        "form_title": "Update conference series",
        "cancel_view": "full_series_list",
    }
    fields = ["title", "abbreviation", "notes"]
    success_message = "Series '%(title)s' updated"
    success_url = reverse_lazy("full_series_list")


class SeriesDelete(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = ConferenceSeries
    template_name = "generic_form.html"
    extra_context = {
        "form_title": "Delete conference series",
        "cancel_view": "full_series_list",
    }
    success_message = "Series '%(title)s' deleted"
    success_url = reverse_lazy("full_series_list")

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(SeriesDelete, self).delete(request, *args, **kwargs)


class SeriesList(LoginRequiredMixin, ListView):
    model = ConferenceSeries
    template_name = "full_series_list.html"
    context_object_name = "series_list"


class OrganizerCreate(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Organizer
    template_name = "generic_form.html"
    extra_context = {
        "form_title": "Create conference organizer",
        "cancel_view": "full_organizer_list",
    }
    fields = ["name", "abbreviation", "conferences_organized", "notes", "url"]
    success_message = "Organizer '%(name)s' created"
    success_url = reverse_lazy("full_organizer_list")


class OrganizerEdit(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Organizer
    template_name = "generic_form.html"
    extra_context = {
        "form_title": "Update conference organizer",
        "cancel_view": "full_organizer_list",
    }
    fields = ["name", "abbreviation", "conferences_organized", "notes", "url"]
    success_message = "Organizer '%(name)s' updated"
    success_url = reverse_lazy("full_organizer_list")


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


class KeywordDelete(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Keyword
    template_name = "generic_form.html"
    extra_context = {"form_title": "Delete keyword", "cancel_view": "full_keyword_list"}
    success_message = "Keyword '%(title)s' deleted"
    success_url = reverse_lazy("full_keyword_list")

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(KeywordDelete, self).delete(request, *args, **kwargs)


class KeywordEdit(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
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
        "tag_list_view": "full_keyword_list",
    }

    def get_queryset(self):
        base_results_set = Keyword.objects.order_by("title")
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
        if "ordering" in self.request.GET:
            context["tag_filter_form"] = TagForm(data=self.request.GET)
        else:
            context["tag_filter_form"] = TagForm(initial={"ordering": "a"})
        context["filtered_tags_count"] = self.get_queryset().count()
        context["available_tags_count"] = Keyword.objects.count()
        return context


@login_required
@transaction.atomic
def keyword_merge(request, keyword_id):
    keyword = get_object_or_404(Keyword, pk=keyword_id)
    context = {
        "merging": keyword,
        "tag_merge_form": KeywordMergeForm,
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


class TopicCreate(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Topic
    template_name = "generic_form.html"
    extra_context = {"form_title": "Create topic", "cancel_view": "full_topic_list"}
    fields = ["title"]
    success_message = "Topic '%(title)s' created"
    success_url = reverse_lazy("full_topic_list")


class TopicDelete(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
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
        "tag_filter_form": TagForm,
        "tag_list_view": "full_topic_list",
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


@login_required
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
