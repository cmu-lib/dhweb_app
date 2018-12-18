from django.contrib import admin

from .models import (
    Organizer,
    ConferenceSeries,
    Conference,
    SeriesMembership,
    Work,
    Version,
    Institution,
    Gender,
    Author,
    Appellation,
    Authorship,
    Department,
    DepartmentAssertion,
    InstitutionAssertion,
    GenderAssertion,
    Keyword,
    Language,
    Topic,
    Discipline,
)


class AuthorshipInline(admin.TabularInline):
    model = Authorship
    extra = 0
    autocomplete_fields = ["author", "version"]


class AppellationInline(admin.TabularInline):
    model = Appellation
    extra = 0
    autocomplete_fields = ["author", "asserted_by"]


class VersionAdmin(admin.ModelAdmin):
    inlines = [AuthorshipInline]
    autocomplete_fields = ["work"]
    search_fields = ["title"]


class WorkAdmin(admin.ModelAdmin):
    search_fields = ["versions__title"]


class DepartmentAssertionInline(admin.TabularInline):
    model = DepartmentAssertion
    extra = 0
    autocomplete_fields = ["department", "asserted_by", "author"]


class DepartmentAdmin(admin.ModelAdmin):
    inlines = [DepartmentAssertionInline]
    search_fields = ["name"]
    autocomplete_fields = ["institution"]


class InstitutionAssertionInline(admin.TabularInline):
    model = InstitutionAssertion
    extra = 0
    autocomplete_fields = ["institution", "asserted_by", "author"]


class InstitutionAdmin(admin.ModelAdmin):
    inlines = [InstitutionAssertionInline]
    search_fields = ["name", "city", "country"]


class AuthorAdmin(admin.ModelAdmin):
    inlines = [
        AppellationInline,
        AuthorshipInline,
        DepartmentAssertionInline,
        InstitutionAssertionInline,
    ]
    search_fields = ["appellations__first_name", "appellations__last_name"]


class ConferenceMembershipInline(admin.TabularInline):
    model = SeriesMembership
    extra = 0


class ConferenceSeriesAdmin(admin.ModelAdmin):
    inlines = [ConferenceMembershipInline]
    search_fields = ["title", "notes"]


class OrganizationInline(admin.TabularInline):
    model = Conference.organizers.through
    extra = 0


class OrganizerAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    filter_horizontal = ["conferences_organized"]


class ConferenceAdmin(admin.ModelAdmin):
    inlines = [ConferenceMembershipInline, OrganizationInline]
    search_fields = ["venue"]


admin.site.register(Organizer, OrganizerAdmin)
admin.site.register(ConferenceSeries, ConferenceSeriesAdmin)
admin.site.register(Conference, ConferenceAdmin)
admin.site.register(SeriesMembership)
admin.site.register(Work, WorkAdmin)
admin.site.register(Version, VersionAdmin)
admin.site.register(Institution, InstitutionAdmin)
admin.site.register(Gender)
admin.site.register(Author, AuthorAdmin)
admin.site.register(Appellation)
admin.site.register(Authorship)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(DepartmentAssertion)
admin.site.register(InstitutionAssertion)
admin.site.register(GenderAssertion)
admin.site.register(Keyword)
admin.site.register(Topic)
admin.site.register(Language)
admin.site.register(Discipline)
