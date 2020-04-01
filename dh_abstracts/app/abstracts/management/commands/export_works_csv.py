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
        with open("abstracts/static/downloads/works.csv", "w") as csvfile:
            writer = csv.writer(
                csvfile, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
            )
            writer.writerow(
                [
                    "work_id",
                    "conference_venue",
                    "conference_year",
                    "conference_organizers",
                    "conference_series",
                    "work_title",
                    "work_authors",
                    "work_type",
                    "work_full_text",
                    "work_full_text_type",
                    "work_full_text_license",
                    "keywords",
                    "languages",
                    "disciplines",
                    "topics",
                ]
            )
            works = models.Work.objects.order_by("pk").prefetch_related(
                "conference",
                "conference__series",
                "conference__organizers",
                "keywords",
                "languages",
                "disciplines",
                "topics",
                "work_type",
                "full_text_license",
            )
            bar = Bar("Exporting works", max=works.count())
            for w in works:
                bar.next()
                row = [
                    w.pk,
                    w.conference.venue,
                    w.conference.year,
                    ";".join([str(o) for o in w.conference.organizers.all()]),
                    ";".join([str(s) for s in w.conference.series.all()]),
                    w.title,
                    ";".join([str(a.appellation) for a in w.authorships.all()]),
                    w.work_type,
                    w.full_text,
                    w.full_text_type,
                    w.full_text_license,
                    ";".join([str(k) for k in w.keywords.all()]),
                    ";".join([str(k) for k in w.languages.all()]),
                    ";".join([str(k) for k in w.disciplines.all()]),
                    ";".join([str(k) for k in w.topics.all()]),
                ]
                writer.writerow(row)
            bar.finish()
