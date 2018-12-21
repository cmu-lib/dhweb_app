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
    Department,
    DepartmentAssertion,
    InstitutionAssertion,
    GenderAssertion,
    Keyword,
    Language,
    Topic,
    Discipline,
)


class AuthorshipAdmin(admin.ModelAdmin):
    search_fields = ["author__last_name", "work__title"]


class AuthorshipInline(admin.TabularInline):
    model = Authorship
    extra = 0
    autocomplete_fields = ["author", "work"]


class AppellationAdmin(admin.ModelAdmin):
    search_fields = ["first_name", "last_name"]


class AppellationInline(admin.TabularInline):
    model = Appellation
    extra = 0
    autocomplete_fields = ["author", "asserted_by"]


class WorkAdmin(admin.ModelAdmin):
    inlines = [AuthorshipInline]
    autocomplete_fields = ["published_version"]
    search_fields = ["title", "authors__appellations__last_name"]


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


class OrganizationInline(admin.TabularInline):
    model = Conference.organizers.through
    extra = 0


class OrganizerAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    filter_horizontal = ["conferences_organized"]


class ConferenceAdmin(admin.ModelAdmin):
    inlines = [ConferenceMembershipInline, OrganizationInline]
    search_fields = ["venue"]


admin.site.register(Authorship, AuthorshipAdmin)
admin.site.register(Organizer, OrganizerAdmin)
admin.site.register(ConferenceSeries, ConferenceSeriesAdmin)
admin.site.register(Conference, ConferenceAdmin)
admin.site.register(SeriesMembership)
admin.site.register(Work, WorkAdmin)
admin.site.register(Institution, InstitutionAdmin)
admin.site.register(Gender)
admin.site.register(Author, AuthorAdmin)
admin.site.register(Appellation, AppellationAdmin)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(DepartmentAssertion)
admin.site.register(InstitutionAssertion)
admin.site.register(GenderAssertion)
admin.site.register(Keyword)
admin.site.register(Topic)
admin.site.register(Language)
admin.site.register(Discipline)
