from django.contrib import admin

from .models import (
    Organizer,
    ConferenceSeries,
    Conference,
    ConferenceDocument,
    SeriesMembership,
    Work,
    Institution,
    Appellation,
    Author,
    Authorship,
    Keyword,
    Language,
    Topic,
    Affiliation,
    Country,
    CountryLabel,
    WorkType,
    FileImport,
    FileImportMessgaes,
    FileImportTries,
    License,
)


class KeywordAdmin(admin.ModelAdmin):
    search_fields = ["title"]


class CountryAdmin(admin.ModelAdmin):
    search_fields = ["pref_name"]
    ordering = ["pref_name"]


class AuthorshipAdmin(admin.ModelAdmin):
    readonly_fields = ["last_updated", "user_last_updated"]
    search_fields = ["author__appellations__last_name", "work__title"]
    autocomplete_fields = ["author", "work", "appellation", "affiliations"]
    list_display = [
        "author",
        "work",
        "appellation",
        "last_updated",
        "user_last_updated",
    ]


class AuthorshipInline(admin.StackedInline):
    model = Authorship
    extra = 0
    autocomplete_fields = ["author", "work", "appellation", "affiliations"]
    readonly_fields = ["last_updated", "user_last_updated"]
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
    readonly_fields = ["last_updated", "user_last_updated"]
    inlines = [AuthorshipInline]
    autocomplete_fields = ["keywords", "languages", "topics"]
    search_fields = ["title", "authorships__appellation__last_name"]
    list_filter = ["work_type", "full_text_type", "conference"]
    list_display = [
        "title",
        "conference",
        "work_type",
        "last_updated",
        "user_last_updated",
    ]


class InstitutionAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "city",
        "state_province_region",
        "country",
        "last_updated",
        "user_last_updated",
    ]
    search_fields = ["name", "city", "state_province_region", "country__pref_name"]
    readonly_fields = ["last_updated", "user_last_updated"]
    list_filter = ["user_last_updated", "country"]
    ordering = ["name"]


class AuthorAdmin(admin.ModelAdmin):
    inlines = [AuthorshipInline]
    search_fields = ["appellations__first_name", "appellations__last_name"]
    readonly_fields = ["last_updated", "user_last_updated"]
    list_display = ["pk", "__str__", "last_updated", "user_last_updated"]


class ConferenceMembershipInline(admin.TabularInline):
    model = SeriesMembership
    extra = 0


class SeriesMembershipAdmin(admin.ModelAdmin):
    list_display = ["series", "conference", "number"]
    model = SeriesMembership


class ConferenceSeriesAdmin(admin.ModelAdmin):
    inlines = [ConferenceMembershipInline]


class OrganizerInline(admin.TabularInline):
    model = Conference.organizers.through
    extra = 0


class OrganizerAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    filter_horizontal = ["conferences_organized"]
    readonly_fields = ["last_updated", "user_last_updated"]
    list_display = ["name", "last_updated", "user_last_updated"]
    list_filter = ["user_last_updated"]


class ConferenceDocumentInline(admin.TabularInline):
    model = ConferenceDocument
    extra = 1


class ConferenceAdmin(admin.ModelAdmin):
    inlines = [ConferenceDocumentInline, ConferenceMembershipInline, OrganizerInline]
    search_fields = ["short_title"]
    autocomplete_fields = ["organizers", "hosting_institutions", "country"]
    list_display = [
        "__str__",
        "short_title",
        "theme_title",
        "city",
        "year",
        "program_available",
        "abstracts_available",
        "entry_status",
        "editing_user",
    ]
    list_filter = [
        "entry_status",
        "program_available",
        "abstracts_available",
        "editing_user",
        "series",
    ]


class FileImportMessagesAdmin(admin.ModelAdmin):
    list_display = ["attempt", "message", "addition_type", "warning"]
    list_filter = ["attempt__conference", "addition_type", "warning"]


admin.site.register(Authorship, AuthorshipAdmin)
admin.site.register(Organizer, OrganizerAdmin)
admin.site.register(ConferenceSeries, ConferenceSeriesAdmin)
admin.site.register(Conference, ConferenceAdmin)
admin.site.register(SeriesMembership, SeriesMembershipAdmin)
admin.site.register(Work, WorkAdmin)
admin.site.register(Institution, InstitutionAdmin)
admin.site.register(Author, AuthorAdmin)
admin.site.register(Appellation, AppellationAdmin)
admin.site.register(Affiliation, AffiliationAdmin)
admin.site.register(Keyword, KeywordAdmin)
admin.site.register(Topic, KeywordAdmin)
admin.site.register(Language, KeywordAdmin)
admin.site.register(Country, CountryAdmin)
admin.site.register(CountryLabel)
admin.site.register(WorkType)
admin.site.register(FileImport)
admin.site.register(FileImportTries)
admin.site.register(License)
admin.site.register(FileImportMessgaes, FileImportMessagesAdmin)
