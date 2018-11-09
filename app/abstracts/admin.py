from django.contrib import admin

from .models import Organizer, ConferenceSeries, Conference, SeriesMembership, Work, Tag, Version, Institution, Gender, Author, Appellation, AppellationAssertion, Authorship, Department, DepartmentAssertion, InstitutionAssertion, GenderAssertion

admin.site.register(Organizer)
admin.site.register(ConferenceSeries)
admin.site.register(Conference)
admin.site.register(SeriesMembership)
admin.site.register(Work)
admin.site.register(Tag)
admin.site.register(Version)
admin.site.register(Institution)
admin.site.register(Gender)
admin.site.register(Author)
admin.site.register(Appellation)
admin.site.register(AppellationAssertion)
admin.site.register(Authorship)
admin.site.register(Department)
admin.site.register(DepartmentAssertion)
admin.site.register(InstitutionAssertion)
admin.site.register(GenderAssertion)
