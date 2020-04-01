"""
Dump a CSV of all the Works
"""

from django.core.management.base import BaseCommand
from abstracts import models
import csv
from progress.bar import Bar


class Command(BaseCommand):
    help = "Dump a CSV of all Works"

    def handle(self, *args, **options):
        with open("abstracts/static/downloads/authorships.csv", "w") as csvfile:
            writer = csv.writer(
                csvfile, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
            )
            writer.writerow(
                [
                    "authorship_id",
                    "work_id",
                    "author_id",
                    "first_name",
                    "last_name",
                    "authorship_order",
                    "affiliation_ids",
                ]
            )

            authorships = models.Authorship.objects.order_by(
                "work__pk", "authorship_order"
            ).prefetch_related("author", "affiliations")

            bar = Bar("Exporting authorships", max=authorships.count())
            for a in authorships:
                bar.next()
                row = [
                    a.pk,
                    a.work.pk,
                    a.author.pk,
                    a.appellation.first_name,
                    a.appellation.last_name,
                    a.authorship_order,
                    ";".join([str(aff.pk) for aff in a.affiliations.all()]),
                ]
                writer.writerow(row)
            bar.finish()
