import datetime

from django.db import models
from django.utils import timezone

# Create your models here.

class Work(models.Model):
    work_id = models.IntegerField(primary_key=True)

    def __str__(self):
        return str(self.work_id)

class Tag(models.Model):
    tag_id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=100, null=True)
    type = models.CharField(max_length=100, null=True)
    StartDate = models.CharField(max_length=100, null=True)
    EndDate = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.title

class Version(models.Model):
    work_id = models.ForeignKey(Work, on_delete=models.CASCADE, related_name='versions')
    title = models.CharField(max_length=500, null=True)
    type = models.CharField(max_length=255, null=True)
    year = models.IntegerField(null=True)
    state = models.CharField(max_length=255, null=True)
    full_text = models.CharField(max_length=50000, null=True)
    tags = models.ManyToManyField(Tag, related_name="versions")

    def __str__(self):
        return self.title
    
    def age(self):
        return datetime.date.today().year - self.year

class Department(models.Model):
    department = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.department

class Institution(models.Model):
    name = models.CharField(max_length=100, null=True)
    country = models.CharField(max_length=100, null=True)
    city = models.CharField(max_length=100, null=True)

class Gender(models.Model):
    gender = models.CharField(max_length = 100)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)

    def __str__(self):
        return self.gender

class Author(models.Model):
    author_id = models.IntegerField(primary_key=True)
    genders = models.ManyToManyField(Gender, related_name='authors')

    def __str__(self):
        return str(self.author_id)

class FirstName(models.Model):
    first_name = models.CharField(max_length = 100)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    author_id = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='first_names')

    def __str__(self):
        return self.first_name

class LastName(models.Model):
    last_name = models.CharField(max_length=100)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    author_id = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='last_names')

    def __str__(self):  
        return self.last_name

class Authorship(models.Model):
    author_id = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='authorships')
    version_id = models.ForeignKey(Version, on_delete=models.CASCADE, related_name='authorships')
    authorship_order = models.IntegerField(default=1)

class DepartmentMembership(models.Model):
    author_id = models.ForeignKey(Author, on_delete=models.CASCADE)
    department_id = models.ForeignKey(Department, on_delete=models.CASCADE)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)

class InstitutionMembership(models.Model):
    author_id = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='institution_memberships')
    institution_id = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='author_memberships')
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
