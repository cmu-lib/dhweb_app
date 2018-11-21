from django.contrib import admin

from .models import Organizer, ConferenceSeries, Conference, SeriesMembership, Work, Tag, Version, Institution, Gender, Author, Appellation, AppellationAssertion, Authorship, Department, DepartmentAssertion, InstitutionAssertion, GenderAssertion

class VersionAdmin(admin.ModelAdmin):
  autocomplete_fields = ["tags", "work"]
  search_fields = ["title"]

class WorkAdmin(admin.ModelAdmin):
  search_fields = ["versions__title"]

class TagAdmin(admin.ModelAdmin):
  search_fields = ["title"]

class AppellationAssertionInline(admin.TabularInline):
  model = AppellationAssertion
  extra = 0
  autocomplete_fields = ["appellation", "asserted_by", "author"]

class AppellationAdmin(admin.ModelAdmin):
  inlines = [AppellationAssertionInline]
  search_fields = ["first_name", "last_name"]

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
  inlines = [AppellationAssertionInline,
             DepartmentAssertionInline, InstitutionAssertionInline]
  search_fields = ["appellations__first_name", "appellations__last_name"]

admin.site.register(Organizer)
admin.site.register(ConferenceSeries)
admin.site.register(Conference)
admin.site.register(SeriesMembership)
admin.site.register(Work, WorkAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Version, VersionAdmin)
admin.site.register(Institution, InstitutionAdmin)
admin.site.register(Gender)
admin.site.register(Author, AuthorAdmin)
admin.site.register(Appellation, AppellationAdmin)
admin.site.register(AppellationAssertion)
admin.site.register(Authorship)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(DepartmentAssertion)
admin.site.register(InstitutionAssertion)
admin.site.register(GenderAssertion)
