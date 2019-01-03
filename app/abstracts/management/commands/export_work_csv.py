"""
Dump a CSV of all the Works
"""

from django.core.management.base import BaseCommand
from abstracts.admin import WorkResource


class Command(BaseCommand):
    help = "Dump a CSV of all Works"

    def handle(self, *args, **options):
        ds = WorkResource().export()
        print(ds.csv, file=open("works.csv", "w"))

