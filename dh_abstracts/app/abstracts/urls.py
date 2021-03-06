from django.urls import include, path
import debug_toolbar
import django.contrib.auth.views as auth_views
from django.conf import settings
from . import views

urlpatterns = [
    path("__debug__/", include(debug_toolbar.urls)),
    path("", views.cache_for_anon(views.home_view), name="home_view"),
    path("works", views.cache_for_anon(views.FullWorkList.as_view()), name="work_list"),
    path(
        "works/<int:work_id>", views.cache_for_anon(views.work_view), name="work_detail"
    ),
    path(
        "works/<int:pk>/xml",
        views.cache_for_anon(views.XMLView.as_view()),
        name="work_xml",
    ),
    path(
        "authors", views.cache_for_anon(views.AuthorList.as_view()), name="author_list"
    ),
    path(
        "authors/<int:author_id>",
        views.cache_for_anon(views.author_view),
        name="author_detail",
    ),
    path("authors/<int:author_id>/merge", views.author_merge_view, name="author_merge"),
    path("authors/<int:pk>/split", views.AuthorSplit.as_view(), name="author_split"),
    path(
        "conferences",
        views.cache_for_anon(views.ConferenceSeriesList.as_view()),
        name="conference_list",
    ),
    path(
        "conference_series/<int:pk>",
        views.cache_for_anon(views.ConferenceSeriesDetail.as_view()),
        name="conference_series_detail",
    ),
    path(
        "conference_series/standalone_events",
        views.cache_for_anon(views.StandaloneList.as_view()),
        name="standalone_conference_list",
    ),
    path(
        "conference/<int:conference_id>/checkout",
        views.conference_checkout,
        name="conference_checkout",
    ),
    path(
        "conference/<int:pk>/import_xml",
        views.ConferenceXMLLoad.as_view(),
        name="conference_xml_load",
    ),
    path("downloads", views.cache_for_anon(views.download_data), name="download_data"),
    path(
        "keyword-autocomplete",
        views.cache_for_anon(views.KeywordAutocomplete.as_view()),
        name="keyword-autocomplete",
    ),
    path(
        "language-autocomplete",
        views.cache_for_anon(views.LanguageAutocomplete.as_view()),
        name="language-autocomplete",
    ),
    path(
        "topic-autocomplete",
        views.cache_for_anon(views.TopicAutocomplete.as_view()),
        name="topic-autocomplete",
    ),
    path(
        "country-autocomplete",
        views.cache_for_anon(views.CountryAutocomplete.as_view()),
        name="country-autocomplete",
    ),
    path(
        "appellation-autocomplete",
        views.cache_for_anon(views.AppellationAutocomplete.as_view()),
        name="appellation-autocomplete",
    ),
    path(
        "work-autocomplete",
        views.cache_for_anon(views.WorkAutocomplete.as_view()),
        name="work-autocomplete",
    ),
    path(
        "institution-autocomplete",
        views.cache_for_anon(views.InstitutionAutocomplete.as_view()),
        name="institution-autocomplete",
    ),
    path(
        "affiliation-autocomplete",
        views.cache_for_anon(views.AffiliationAutocomplete.as_view()),
        name="affiliation-autocomplete",
    ),
    path(
        "author-autocomplete",
        views.cache_for_anon(views.AuthorAutocomplete.as_view()),
        name="author-autocomplete",
    ),
    path(
        "conference-autocomplete",
        views.cache_for_anon(views.ConferenceAutocomplete.as_view()),
        name="conference-autocomplete",
    ),
    path(
        "author-info-json/<int:author_id>",
        views.AuthorInfoJSON,
        name="author-info-json",
    ),
    path(
        "affiliation-info-json/<int:affiliation_id>",
        views.AffiliationInfoJSON,
        name="affiliation-info-json",
    ),
    path("editor/works/create", views.WorkCreate, name="work_create"),
    path("editor/works/<int:work_id>/edit", views.WorkEdit, name="work_edit"),
    path(
        "editor/works/<int:work_id>/edit/authorship",
        views.WorkEditAuthorship,
        name="work_edit_authorship",
    ),
    path(
        "editor/works/<int:pk>/delete", views.WorkDelete.as_view(), name="work_delete"
    ),
    path(
        "editor/authors_institution",
        views.AuthorInstitutionList.as_view(),
        name="author_institution_list",
    ),
    path(
        "editor/institutions",
        views.FullInstitutionList.as_view(),
        name="full_institution_list",
    ),
    path(
        "editor/institutions/<int:pk>/edit",
        views.InstitutionEdit.as_view(),
        name="institution_edit",
    ),
    path(
        "editor/institutions/create",
        views.InstitutionCreate.as_view(),
        name="institution_create",
    ),
    path(
        "editor/institutions/<int:institution_id>/merge",
        views.institution_merge,
        name="institution_merge",
    ),
    path("editor/wipe_unused", views.wipe_unused, name="wipe_unused"),
    path(
        "editor/conferences/create",
        views.ConferenceCreate.as_view(),
        name="conference_create",
    ),
    path(
        "editor/conferences/<int:pk>/delete",
        views.ConferenceDelete.as_view(),
        name="conference_delete",
    ),
    path(
        "editor/conferences/<int:pk>/edit", views.ConferenceEdit, name="conference_edit"
    ),
    path("editor/series/create", views.SeriesCreate.as_view(), name="series_create"),
    path("editor/series/<int:pk>/edit", views.SeriesEdit.as_view(), name="series_edit"),
    path(
        "editor/series/<int:pk>/delete",
        views.SeriesDelete.as_view(),
        name="series_delete",
    ),
    path(
        "editor/organizers", views.OrganizerList.as_view(), name="full_organizer_list"
    ),
    path(
        "editor/organizers/create",
        views.OrganizerCreate.as_view(),
        name="organizer_create",
    ),
    path(
        "editor/organizers/<int:pk>/edit",
        views.OrganizerEdit.as_view(),
        name="organizer_edit",
    ),
    path(
        "editor/organizers/<int:pk>/delete",
        views.OrganizerDelete.as_view(),
        name="organizer_delete",
    ),
    path(
        "editor/affiliations/create",
        views.AffiliationCreate.as_view(),
        name="affiliation_create",
    ),
    path(
        "auto-create-affiliation",
        views.ajax_affiliation_create,
        name="ajax_affiliation_create",
    ),
    path(
        "editor/affiliations/<int:pk>/edit",
        views.AffiliationEdit.as_view(),
        name="affiliation_edit",
    ),
    path(
        "editor/affiliations/<int:affiliation_id>/merge",
        views.affiliation_merge,
        name="affiliation_merge",
    ),
    path(
        "editor/affiliations/multi_merge",
        views.affiliation_multi_merge,
        name="affiliation_multi_merge",
    ),
    path(
        "editor/institutions/multi_merge",
        views.institution_multi_merge,
        name="institution_multi_merge",
    ),
    path("editor/keywords", views.KeywordList.as_view(), name="full_keyword_list"),
    path(
        "editor/keywords/create", views.KeywordCreate.as_view(), name="keyword_create"
    ),
    path(
        "editor/keywords/<int:pk>/delete",
        views.KeywordDelete.as_view(),
        name="keyword_delete",
    ),
    path(
        "editor/keywords/<int:pk>/edit",
        views.KeywordEdit.as_view(),
        name="keyword_edit",
    ),
    path(
        "editor/keywords/<int:keyword_id>/merge",
        views.keyword_merge,
        name="keyword_merge",
    ),
    path(
        "editor/keywords/multi_merge",
        views.keyword_multi_merge,
        name="keyword_multi_merge",
    ),
    path("editor/topics", views.TopicList.as_view(), name="full_topic_list"),
    path("editor/topics/create", views.TopicCreate.as_view(), name="topic_create"),
    path(
        "editor/topics/<int:pk>/delete",
        views.TopicDelete.as_view(),
        name="topic_delete",
    ),
    path("editor/topics/<int:pk>/edit", views.TopicEdit.as_view(), name="topic_edit"),
    path("editor/topics/<int:topic_id>/merge", views.topic_merge, name="topic_merge"),
    path(
        "editor/topics/multi_merge", views.topic_multi_merge, name="topic_multi_merge"
    ),
    path("editor/languages", views.LanguageList.as_view(), name="full_language_list"),
    path(
        "editor/languages/create",
        views.LanguageCreate.as_view(),
        name="language_create",
    ),
    path(
        "editor/languages/<int:pk>/delete",
        views.LanguageDelete.as_view(),
        name="language_delete",
    ),
    path(
        "editor/languages/<int:pk>/edit",
        views.LanguageEdit.as_view(),
        name="language_edit",
    ),
    path(
        "editor/languages/<int:language_id>/merge",
        views.language_merge,
        name="language_merge",
    ),
    path("editor/work_types", views.WorkTypeList.as_view(), name="full_work_type_list"),
    path(
        "editor/work_types/create",
        views.WorkTypeCreate.as_view(),
        name="work_type_create",
    ),
    path(
        "editor/work_types/<int:pk>/delete",
        views.WorkTypeDelete.as_view(),
        name="work_type_delete",
    ),
    path(
        "editor/work_types/<int:pk>/edit",
        views.WorkTypeEdit.as_view(),
        name="work_type_edit",
    ),
    path(
        "editor/work_types/<int:work_type_id>/merge",
        views.work_type_merge,
        name="work_type_merge",
    ),
    path(
        "downloads/dh_conferences_works.csv",
        views.download_works_csv,
        name="works_download",
    ),
    path(
        "downloads/public",
        views.public_download_all_tables,
        name="public_all_tables_download",
    ),
    path(
        f"downloads/private",
        views.private_download_all_tables,
        name="private_all_tables_download",
    ),
]
