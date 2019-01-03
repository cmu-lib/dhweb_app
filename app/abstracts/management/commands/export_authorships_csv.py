"""
Dump a CSV of all the Works
"""

from django.core.management.base import BaseCommand
from abstracts.admin import AuthorshipResource


class Command(BaseCommand):
    help = "Dump a CSV of all Works"

    def handle(self, *args, **options):
        ds = AuthorshipResource().export()
        print(ds.csv, file=open("abstracts/static/downloads/authorships.csv", "w"))
