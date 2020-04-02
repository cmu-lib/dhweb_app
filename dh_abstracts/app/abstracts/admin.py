from django.contrib import admin

from .models import (
    Organizer,
    ConferenceSeries,
    Conference,
    SeriesMembership,
    Work,
    Institution,
    Appellation,
    Author,
    Authorship,
    Keyword,
    Language,
    Topic,
    Discipline,
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
    search_fields = ["name"]


class InstitutuionAdmin(admin.ModelAdmin):
    search_fields = ["name", "city", "country__names__name"]


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
    autocomplete_fields = ["keywords", "languages", "topics", "disciplines"]
    search_fields = ["title", "authorships__appellation__last_name"]
    list_filter = ["work_type", "conference"]
    list_display = [
        "title",
        "conference",
        "work_type",
        "last_updated",
        "user_last_updated",
    ]


class InstitutionAdmin(admin.ModelAdmin):
    list_display = ["pk", "name", "city", "country"]
    search_fields = ["name", "city", "country__names__name"]


class AuthorAdmin(admin.ModelAdmin):
    inlines = [AuthorshipInline]
    search_fields = ["appellations__first_name", "appellations__last_name"]


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
admin.site.register(Author, AuthorAdmin)
admin.site.register(Appellation, AppellationAdmin)
admin.site.register(Affiliation, AffiliationAdmin)
admin.site.register(Keyword, KeywordAdmin)
admin.site.register(Topic, KeywordAdmin)
admin.site.register(Language, KeywordAdmin)
admin.site.register(Discipline, KeywordAdmin)
admin.site.register(Country, CountryAdmin)
admin.site.register(CountryLabel)
admin.site.register(WorkType)
admin.site.register(FileImport)
admin.site.register(FileImportTries)
admin.site.register(License)
admin.site.register(FileImportMessgaes, FileImportMessagesAdmin)