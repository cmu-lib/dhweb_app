from django.urls import include, path
import debug_toolbar
import django.contrib.auth.views as auth_views
from . import views

urlpatterns = [
    path("__debug__/", include(debug_toolbar.urls)),
    path("auth/login", auth_views.LoginView.as_view(), name="login"),
    path("", views.home_view, name="home_view"),
    path("works", views.WorkList.as_view(), name="work_list"),
    path("works/<int:work_id>", views.work_view, name="work_detail"),
    path("works/<int:work_id>/edit", views.WorkEdit, name="work_edit"),
    path(
        "works/<int:work_id>/edit/authorship",
        views.WorkEditAuthorship,
        name="work_edit_authorship",
    ),
    path("authors", views.AuthorList.as_view(), name="author_list"),
    path("authors/<int:author_id>", views.author_view, name="author_detail"),
    path("authors/<int:author_id>/merge", views.author_merge_view, name="author_merge"),
    path("conferences", views.ConferenceList, name="conference_list"),
    path("downloads", views.download_data, name="download_data"),
    path(
        "institution-autocomplete",
        views.InstitutionAutocomplete.as_view(),
        name="institution-autocomplete",
    ),
    path(
        "topic-autocomplete",
        views.TopicAutocomplete.as_view(),
        name="topic-autocomplete",
    ),
    path(
        "keyword-autocomplete",
        views.KeywordAutocomplete.as_view(),
        name="keyword-autocomplete",
    ),
    path(
        "language-autocomplete",
        views.LanguageAutocomplete.as_view(),
        name="language-autocomplete",
    ),
    path(
        "discipline-autocomplete",
        views.DisciplineAutocomplete.as_view(),
        name="discipline-autocomplete",
    ),
    path(
        "country-autocomplete",
        views.CountryAutocomplete.as_view(),
        name="country-autocomplete",
    ),
    path(
        "author-autocomplete",
        views.AuthorAutocomplete.as_view(),
        name="author-autocomplete",
    ),
    path(
        "unrestricted-keyword-autocomplete",
        views.UnrestrictedKeywordAutocomplete.as_view(),
        name="unrestricted-keyword-autocomplete",
    ),
    path(
        "unrestricted-language-autocomplete",
        views.UnrestrictedLanguageAutocomplete.as_view(),
        name="unrestricted-language-autocomplete",
    ),
    path(
        "unrestricted-discipline-autocomplete",
        views.UnrestrictedDisciplineAutocomplete.as_view(),
        name="unrestricted-discipline-autocomplete",
    ),
    path(
        "unrestricted-topic-autocomplete",
        views.UnrestrictedTopicAutocomplete.as_view(),
        name="unrestricted-topic-autocomplete",
    ),
    path(
        "unrestricted-country-autocomplete",
        views.UnrestrictedCountryAutocomplete.as_view(),
        name="unrestricted-country-autocomplete",
    ),
    path(
        "unrestricted-appellation-autocomplete",
        views.UnrestrictedAppellationAutocomplete.as_view(),
        name="unrestricted-appellation-autocomplete",
    ),
    path(
        "unrestricted-work-autocomplete",
        views.UnrestrictedWorkAutocomplete.as_view(),
        name="unrestricted-work-autocomplete",
    ),
    path(
        "unrestricted-institution-autocomplete",
        views.UnrestrictedInstitutionAutocomplete.as_view(),
        name="unrestricted-institution-autocomplete",
    ),
    path(
        "unrestricted-affiliation-autocomplete",
        views.UnrestrictedAffiliationAutocomplete.as_view(),
        name="unrestricted-affiliation-autocomplete",
    ),
    path(
        "unrestricted-author-autocomplete",
        views.UnrestrictedAuthorAutocomplete.as_view(),
        name="unrestricted-author-autocomplete",
    ),
    path("editor/authors", views.FullAuthorList.as_view(), name="full_author_list"),
    path("editor/works", views.FullWorkList.as_view(), name="full_work_list"),
    path(
        "editor/institutions",
        views.FullInstitutionList.as_view(),
        name="full_institution_list",
    ),
    path("editor/wipe_unused", views.wipe_unused, name="wipe_unused"),
    path(
        "editor/conferences/create",
        views.ConferenceCreate.as_view(),
        name="conference_create",
    ),
    path(
        "editor/conferences/<int:pk>/edit",
        views.ConferenceEdit.as_view(),
        name="conference_edit",
    ),
    path(
        "editor/conferences",
        views.ConferenceList.as_view(),
        name="full_conference_list",
    ),
    path("editor/series", views.SeriesList.as_view(), name="full_series_list"),
    path("editor/series/create", views.SeriesCreate.as_view(), name="series_create"),
    path("editor/series/<int:pk>/edit", views.SeriesEdit.as_view(), name="series_edit"),
]
