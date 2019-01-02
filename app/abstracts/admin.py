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

# CSV exporting

from import_export import resources


class WorkResource(resources.ModelResource):
    class Meta:
        model = Work
        fields = ("id", "topics__title")

