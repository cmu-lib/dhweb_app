"""
Full text indices for various models need to be calculated by concatenating
multiple fields into one SearchVector field. This only needs to be done
periodically, so it is included here as a management command.
"""

from django.core.management.base import BaseCommand
from django.contrib.postgres.search import SearchVector
from abstracts.models import Work, Appellation, Institution


class Command(BaseCommand):
    help = "Repopulates the SearchVector fields for models that need full-text search."

    def handle(self, *args, **kwargs):

        print("Updating index for Works...", end="", flush=True)
        Work.objects.update(search_text=SearchVector("title", "full_text"))
        print("done.")

