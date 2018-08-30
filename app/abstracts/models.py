import datetime

from django.db import models
from django.utils import timezone

# Create your models here.

class Work(models.Model):
    work_id = models.IntegerField(primary_key=True)

    def __str__(self):
        return self.work_id

class Version(models.Model):
    work_id = models.ForeignKey(Work, on_delete=models.CASCADE)
    title = models.CharField(max_length = 500)
    type = models.CharField(max_length = 255)
    year = models.IntegerField()
    state = models.CharField(max_length = 255)
    full_text = models.CharField(max_length = 50000)

    def __str__(self):
        return self.title
    
    def age(self):
        return datetime.date.today().year - self.year
