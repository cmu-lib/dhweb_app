from django.core.management.base import BaseCommand
from abstracts import models
import json


class Command(BaseCommand):
    help = "Export dictionary of entity IDs for testing"

    def handle(self, *args, **options):
        all_ids = {
            "works": list(models.Work.objects.all().values_list("id", flat=True)),
            "conferences": list(
                models.Conference.objects.all().values_list("id", flat=True)
            ),
            "authors": list(models.Author.objects.all().values_list("id", flat=True)),
            "keywords": list(models.Keyword.objects.all().values_list("id", flat=True)),
            "topics": list(models.Topic.objects.all().values_list("id", flat=True)),
            "affiliations": list(
                models.Affiliation.objects.all().values_list("id", flat=True)
            ),
            "institutions": list(
                models.Institution.objects.all().values_list("id", flat=True)
            ),
            "appellations": list(
                models.Appellation.objects.all().values_list("id", flat=True)
            ),
            "countries": list(
                models.Country.objects.all().values_list("id", flat=True)
            ),
        }

        json.dump(all_ids, open("/vol/data/all_ids.json", "w"))

