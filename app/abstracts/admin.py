from django.contrib import admin

from .models import (
    Organizer,
    ConferenceSeries,
    Conference,
    SeriesMembership,
    Work,
    Institution,
    Gender,
    Appellation,
    Author,
    Authorship,
    Keyword,
    Language,
    Topic,
    Discipline,
    Affiliation,
    Country,
    WorkType,
    FileImport,
    FileImportMessgaes,
    FileImportTries,
)


class KeywordAdmin(admin.ModelAdmin):
    search_fields = ["title"]


class GenderAdmin(admin.ModelAdmin):
    search_fields = ["gender"]


class CountryAdmin(admin.ModelAdmin):
    search_fields = ["name"]


class InstitutuionAdmin(admin.ModelAdmin):
    search_fields = ["name", "city", "country__name"]


class AuthorshipAdmin(admin.ModelAdmin):
    search_fields = ["author__appellations__last_name", "work__title"]
    autocomplete_fields = ["author", "work", "genders", "appellation", "affiliations"]
    list_filter = ("work__state",)


class AuthorshipInline(admin.StackedInline):
    model = Authorship
    extra = 0
    autocomplete_fields = ["author", "work", "genders", "appellation", "affiliations"]
    show_change_link = True


class AffiliationAdmin(admin.ModelAdmin):
    search_fields = ["department", "institution__name"]
    autocomplete_fields = ["institution"]


class AffiliationInline(admin.StackedInline):
    model = Affiliation
    extra = 0
    autocomplete_fields = ["institution"]


class AppellationAdmin(admin.ModelAdmin):
    search_fields = ["first_name", "last_name"]


class WorkAdmin(admin.ModelAdmin):
    inlines = [AuthorshipInline]
    autocomplete_fields = [
        "published_version",
        "keywords",
        "languages",
        "topics",
        "disciplines",
    ]
    search_fields = ["title", "authorships__appellation__last_name"]
    list_filter = ["state", "work_type", "conference"]
    list_display = ["title", "conference", "state", "work_type"]
    radio_fields = {"state": admin.HORIZONTAL}


class InstitutionAdmin(admin.ModelAdmin):
    list_display = ["pk", "name", "city", "country"]
    search_fields = ["name", "city", "country__name"]


class AuthorAdmin(admin.ModelAdmin):
    inlines = [AuthorshipInline]
    search_fields = ["appellations__first_name", "appellations__last_name"]
    list_filter = ["works__state"]


class ConferenceMembershipInline(admin.TabularInline):
    model = SeriesMembership
    extra = 0


class ConferenceSeriesAdmin(admin.ModelAdmin):
    inlines = [ConferenceMembershipInline]


class OrganizerInline(admin.TabularInline):
    model = Conference.organizers.through
    extra = 0


class OrganizerAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    filter_horizontal = ["conferences_organized"]


class ConferenceAdmin(admin.ModelAdmin):
    inlines = [ConferenceMembershipInline, OrganizerInline]
    search_fields = ["venue"]
    autocomplete = ["organizer"]


class FileImportMessagesAdmin(admin.ModelAdmin):
    list_display = ["attempt", "message", "addition_type", "warning"]
    list_filter = ["attempt__conference", "addition_type", "warning"]


admin.site.register(Authorship, AuthorshipAdmin)
admin.site.register(Organizer, OrganizerAdmin)
admin.site.register(ConferenceSeries, ConferenceSeriesAdmin)
admin.site.register(Conference, ConferenceAdmin)
admin.site.register(SeriesMembership)
admin.site.register(Work, WorkAdmin)
admin.site.register(Institution, InstitutionAdmin)
admin.site.register(Gender, GenderAdmin)
admin.site.register(Author, AuthorAdmin)
admin.site.register(Appellation, AppellationAdmin)
admin.site.register(Affiliation, AffiliationAdmin)
admin.site.register(Keyword, KeywordAdmin)
admin.site.register(Topic, KeywordAdmin)
admin.site.register(Language, KeywordAdmin)
admin.site.register(Discipline, KeywordAdmin)
admin.site.register(Country, CountryAdmin)
admin.site.register(WorkType)
admin.site.register(FileImport)
admin.site.register(FileImportTries)
admin.site.register(FileImportMessgaes, FileImportMessagesAdmin)

# CSV exporting

from import_export import resources
from import_export.fields import Field
from import_export.widgets import ManyToManyWidget


class WorkResource(resources.ModelResource):
    id_field = Field(attribute="id", column_name="work_id")
    conference_venue_field = Field(
        attribute="conference__venue", column_name="conference_venue"
    )
    conference_year_field = Field(
        attribute="conference__year", column_name="conference_year"
    )
    conference_organizers_field = Field(
        attribute="conference__organizers",
        column_name="conference_organizers",
        widget=ManyToManyWidget(model=Organizer, separator=";", field="name"),
    )
    conference_series_field = Field(
        attribute="conference__series",
        column_name="conference_series",
        widget=ManyToManyWidget(model=ConferenceSeries, separator=";", field="title"),
    )
    conference_series_number_field = Field(
        attribute="conference__series_memberships",
        column_name="conference_series_number",
        widget=ManyToManyWidget(model=SeriesMembership, separator=";", field="number"),
    )
    title_field = Field(attribute="title", column_name="work_title")
    work_type_field = Field(attribute="work_type__title", column_name="work_type")
    work_state_field = Field(attribute="state", column_name="work_state")
    full_text_field = Field(attribute="full_text", column_name="work_full_text")
    full_text_type_field = Field(
        attribute="full_text_type", column_name="work_full_text_type"
    )
    keywords_field = Field(
        attribute="keywords",
        column_name="keywords",
        widget=ManyToManyWidget(model=Keyword, separator=";", field="title"),
    )
    languages_field = Field(
        attribute="languages",
        column_name="languages",
        widget=ManyToManyWidget(model=Language, separator=";", field="title"),
    )
    disciplines_field = Field(
        attribute="disciplines",
        column_name="disciplines",
        widget=ManyToManyWidget(model=Discipline, separator=";", field="title"),
    )
    topics_field = Field(
        attribute="topics",
        column_name="topics",
        widget=ManyToManyWidget(model=Topic, separator=";", field="title"),
    )
    published_version = Field(
        attribute="published_version__pk", column_name="published_verison"
    )

    class Meta:
        model = Work
        fields = [
            "id_field",
            "onference_venue_field",
            "conference_year_field",
            "conference_organizers_field",
            "conference_series_field",
            "conference_series_number_field",
            "title_field",
            "work_type_field",
            "work_state_field",
            "full_text_field",
            "full_text_type_field",
            "keywords_field",
            "languages_field",
            "disciplines_field",
            "topics_field",
            "published_version",
        ]


class AuthorshipResource(resources.ModelResource):
    id_field = Field(attribute="id", column_name="authorship_id")
    work_id_field = Field(attribute="work__pk", column_name="work_id")
    author_field = Field(attribute="author__pk", column_name="author_id")
    author_first_name_field = Field(
        attribute="appellation__first_name", column_name="author_first_name"
    )
    author_last_name_field = Field(
        attribute="appellation__last_name", column_name="author_last_name"
    )
    author_first_name_field = Field(
        attribute="appellation__first_name", column_name="author_first_name"
    )
    authorship_order_field = Field(
        attribute="authorship_order", column_name="authorship_order"
    )
    affiliations_field = Field(
        attribute="affiliations",
        column_name="affiliations",
        widget=ManyToManyWidget(model=Affiliation, separator=";"),
    )
    genders_field = Field(
        attribute="genders",
        column_name="genders",
        widget=ManyToManyWidget(model=Gender, separator=";", field="gender"),
    )

    class Meta:
        model = Authorship
        fields = [
            "id_field",
            "work_id_field",
            "author_field",
            "author_first_name_field",
            "author_last_name_field",
            "authorship_order_field",
            "affiliations_field",
            "genders_field",
        ]


class AffiliationResource(resources.ModelResource):
    id_field = Field(attribute="id", column_name="affiliation_id")
    departments_field = Field(attribute="department", column_name="department")
    institutions_field = Field(attribute="institution__name", column_name="institution")
    city_field = Field(attribute="institution__city", column_name="city")
    country_field = Field(attribute="institution__country__name", column_name="country")

    class Meta:
        model = Affiliation
        fields = [
            "id_field",
            "departments_field",
            "institutions_field",
            "city_field",
            "country_field",
        ]
