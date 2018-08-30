from django.contrib import admin

from .models import Work, Tag, Version, Department, Institution, FirstName, LastName, Gender, Author, Authorship, DepartmentMembership, InstitutionMembership

admin.site.register(Work)
admin.site.register(Tag)
admin.site.register(Version)
admin.site.register(Department)
admin.site.register(Institution)
admin.site.register(FirstName)
admin.site.register(LastName)
admin.site.register(Gender)
admin.site.register(Author)
admin.site.register(Authorship)
admin.site.register(DepartmentMembership)
admin.site.register(InstitutionMembership)
