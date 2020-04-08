from django.urls import include, path
import debug_toolbar
import django.contrib.auth.views as auth_views
from . import views

urlpatterns = [
    path("__debug__/", include(debug_toolbar.urls)),
    path("auth/login", auth_views.LoginView.as_view(), name="login"),
    path("auth/logout", auth_views.LogoutView.as_view(), name="logout"),
    path("", views.home_view, name="home_view"),
    path("works", views.FullWorkList.as_view(), name="work_list"),
    path("works/<int:work_id>", views.work_view, name="work_detail"),
    path("authors", views.AuthorList.as_view(), name="author_list"),
    path("authors/<int:author_id>", views.author_view, name="author_detail"),
    path("authors/<int:author_id>/merge", views.author_merge_view, name="author_merge"),
    path("conferences", views.conference_list, name="conference_list"),
    path("downloads", views.download_data, name="download_data"),
    path(
        "institution-autocomplete",
        views.InstitutionAutocomplete.as_view(),
        name="institution-autocomplete",
    ),
    path(
        "affiliation-autocomplete",
        views.AffiliationAutocomplete.as_view(),
        name="affiliation-autocomplete",
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
    path("editor/series", views.SeriesList.as_view(), name="full_series_list"),
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
    path(
        "editor/disciplines",
        views.DisciplineList.as_view(),
        name="full_discipline_list",
    ),
    path(
        "editor/disciplines/create",
        views.DisciplineCreate.as_view(),
        name="discipline_create",
    ),
    path(
        "editor/disciplines/<int:pk>/delete",
        views.DisciplineDelete.as_view(),
        name="discipline_delete",
    ),
    path(
        "editor/disciplines/<int:pk>/edit",
        views.DisciplineEdit.as_view(),
        name="discipline_edit",
    ),
    path(
        "editor/disciplines/<int:discipline_id>/merge",
        views.discipline_merge,
        name="discipline_merge",
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
]
