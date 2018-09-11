import datetime

from django.db import models
from django.utils import timezone

# Create your models here.

class Conference(models.Model):
    year = models.IntegerField()
    venue = models.CharField(max_length=100, null=True)

    def __str__(self):
        return f"{self.year} - {self.venue}"

class Work(models.Model):
    submission = models.ForeignKey(Conference, on_delete = models.CASCADE, related_name = 'works')

    def __str__(self):
        return str(self.pk)

    def __eq__(self, other):
        return(self.pk == other.pk)

class Tag(models.Model):
    title = models.CharField(max_length=100, null=True)
    type = models.CharField(max_length=100, null=True)
    start_date = models.CharField(max_length=100, null=True)
    end_date = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.title

class Version(models.Model):
    work = models.ForeignKey(Work, on_delete=models.CASCADE, related_name='versions')
    title = models.CharField(max_length=500, null=True)
    submission_type = models.CharField(max_length=255, null=True)
    state = models.CharField(max_length=2, choices=(
        ("ac", "accpeted"),
        ("su", "submission"),
    ))
    full_text = models.CharField(max_length=50000, null=True)
    tags = models.ManyToManyField(Tag, related_name="versions")

    def __str__(self):
        return self.title

    def age(self):
        return datetime.date.today().year - self.year

    def __eq__(self, other):
        return(self.pk == other.pk)

class Institution(models.Model):
    name = models.CharField(max_length=100, null=True)
    country = models.CharField(max_length=100, null=True)
    city = models.CharField(max_length=100, null=True)

    def __str__(self):
        return f"{self.name} ({self.city}, {self.country})"

class Gender(models.Model):
    gender = models.CharField(max_length = 100)

    def __str__(self):
        return self.gender

class Author(models.Model):
    author_id = models.IntegerField(primary_key=True)

    def __str__(self):
        return str(self.author_id)

class AppellationAssertion(models.Model):
    first_name = models.CharField(max_length = 100, null=True)
    last_name = models.CharField(max_length = 100, null=True)
    author = models.ForeignKey(Author, on_delete = models.CASCADE, related_name='appellations')
    asserted_by = models.ForeignKey(
        Conference, on_delete=models.CASCADE, related_name='appellations')

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Authorship(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='authorships')
    version = models.ForeignKey(Version, on_delete=models.CASCADE, related_name='authorships')
    authorship_order = models.IntegerField(default=1)

class DepartmentAssertion(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name="department_memberships")
    asserted_by = models.ForeignKey(Conference, on_delete = models.CASCADE, related_name="department_assertions")
    department=models.CharField(max_length = 100)

    def __str__(self):
        return self.department

class InstitutionAssertion(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='institution_memberships')
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='member_assertions')
    asserted_by=models.ForeignKey(Conference, on_delete = models.CASCADE, related_name = 'institution_assertions')

class GenderAssertion(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='gender_memberships')
    gender = models.ForeignKey(Gender, on_delete=models.CASCADE, related_name='gender_authors')
    asserted_by=models.ForeignKey(Conference, on_delete = models.CASCADE, related_name = 'gender_assertions')
