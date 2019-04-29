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
        "work-autocomplete", views.WorkAutocomplete.as_view(), name="work-autocomplete"
    ),
]
