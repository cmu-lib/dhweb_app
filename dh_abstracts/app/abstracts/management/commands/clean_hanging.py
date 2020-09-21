from django.core.management.base import BaseCommand
from abstracts import models
from django.db import transaction
from django.db.models import Q


class Command(BaseCommand):
    help = "Erase hanging records"

    def handle(self, *args, **options):
        models.Author.objects.exclude(authorships__isnull=False).all().delete()
        models.Affiliation.objects.exclude(asserted_by__isnull=False).all().delete()
        models.Institution.objects.exclude(
            Q(affiliations__asserted_by__isnull=False) | Q(conferences__isnull=False)
        ).all().delete()
        models.Keyword.objects.exclude(works__isnull=False).all().delete()
        models.Appellation.objects.exclude(asserted_by__isnull=False).all().delete()

