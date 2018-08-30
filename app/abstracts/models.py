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
    title = models.CharField(max_length=100)
    type = models.CharField(max_length=100)
    StartDate = models.IntegerField()
    EndDate = models.IntegerField()

    def __str__(self):
        return self.title

class Version(models.Model):
    work_id = models.ForeignKey(Work, on_delete=models.CASCADE)
    title = models.CharField(max_length = 500)
    type = models.CharField(max_length = 255)
    year = models.IntegerField()
    state = models.CharField(max_length = 255)
    full_text = models.CharField(max_length = 50000)
    tags = models.ManyToManyField(Tag)

    def __str__(self):
        return self.title
    
    def age(self):
        return datetime.date.today().year - self.year

class Department(models.Model):
    department = models.CharField(max_length = 100)

    def __str__(self):
        return self.department

class Institution(models.Model):
    institution = models.CharField(max_length = 100)
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100)

class FirstName(models.Model):
    first_name = models.CharField(max_length = 100)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return self.first_name

class LastName(models.Model):
    last_name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):  
        return self.last_name

class Gender(models.Model):
    gender = models.CharField(max_length = 100)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return self.gender

class Author(models.Model):
    author_id = models.IntegerField(primary_key=True)
    first_names = models.ForeignKey(FirstName, on_delete=models.CASCADE)
    last_names = models.ForeignKey(LastName, on_delete=models.CASCADE)
    genders = models.ForeignKey(Gender, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.author_id)

class Authorship(models.Model):
    author_id = models.ForeignKey(Author, on_delete=models.CASCADE)
    version_id = models.ForeignKey(Version, on_delete=models.CASCADE)
    authorship_order = models.IntegerField()

class DepartmentMembership(models.Model):
    author_id = models.ForeignKey(Author, on_delete=models.CASCADE)
    department_id = models.ForeignKey(Department, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()

class InstitutionMembership(models.Model):
    author_id = models.ForeignKey(Author, on_delete=models.CASCADE)
    institution_id = models.ForeignKey(Department, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
