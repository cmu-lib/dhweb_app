"""
Dump a CSV of all the Works
"""

from django.core.management.base import BaseCommand
from abstracts import models
import csv
from progress.bar import Bar
from datetime import date


class Command(BaseCommand):
    help = "Dump a CSV of all Works"

    def handle(self, *args, **options):
        with open(
            f"abstracts/static/downloads/{date.today().strftime('%Y-%m-%d')}_affiliations.csv",
            "w",
        ) as csvfile:
            writer = csv.writer(
                csvfile, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
            )
            writer.writerow(
                ["affiliation_id", "department", "institution", "city", "country"]
            )
            affiliations = models.Affiliation.objects.order_by(
                "institution__name", "department"
            ).prefetch_related("institution", "institution__country")
            bar = Bar("Exporting", max=affiliations.count())
            for a in affiliations:
                bar.next()
                row = [
                    a.pk,
                    a.department,
                    a.institution,
                    a.institution.city,
                    a.institution.country,
                ]
                writer.writerow(row)
            bar.finish()
