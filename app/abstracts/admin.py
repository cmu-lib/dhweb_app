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

admin.site.register(Organizer)
admin.site.register(ConferenceSeries)
admin.site.register(Conference)
admin.site.register(SeriesMembership)
admin.site.register(Work)
admin.site.register(Institution)
admin.site.register(Gender)
admin.site.register(Appellation)
admin.site.register(Author)
admin.site.register(Authorship)
admin.site.register(Department)
admin.site.register(DepartmentAssertion)
admin.site.register(InstitutionAssertion)
admin.site.register(GenderAssertion)
admin.site.register(Keyword)
admin.site.register(Language)
admin.site.register(Topic)
admin.site.register(Discipline)
