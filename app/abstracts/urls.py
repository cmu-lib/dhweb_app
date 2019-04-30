from django.urls import path

from . import views

urlpatterns = [
    path("", views.home_view, name="home_view"),
    path("works", views.WorkList.as_view(), name="work_list"),
    path("works/<int:pk>", views.WorkView.as_view(), name="work_detail"),
    path("works/<int:pk>/edit", views.WorkEdit.as_view(), name="work_edit"),
    path("authors", views.AuthorList.as_view(), name="author_list"),
    path("authors/<int:pk>", views.AuthorView.as_view(), name="author_detail"),
    path("authors/merge/<int:author_id>", views.author_merge_view, name="author_merge"),
    path("conferences", views.ConferenceList.as_view(), name="conference_list"),
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
]
