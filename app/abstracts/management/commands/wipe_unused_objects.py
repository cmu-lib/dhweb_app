from django.core import management
from django.core.management.base import BaseCommand
from abstracts import models


class Command(BaseCommand):
    help = "Wipe all unfreferenced Appellations, Authors, Affiliations, Institutions, Countries, Keywords, and Topics"

    def handle(self, *args, **options):
        models.Author.objects.filter(authorships__isnull=True).delete()
        models.Affiliation.objects.filter(asserted_by__isnull=True).delete()
        models.Institution.objects.filter(affiliations__isnull=True).delete()
        models.Keyword.objects.filter(works__isnull=True).delete()
        models.Topic.objects.filter(works__isnull=True).delete()
        models.Appellation.objects.filter(asserted_by__isnull=True).delete()
