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
            f"abstracts/static/downloads/{date.today().strftime('%Y-%m-%d')}_works.csv",
            "w",
        ) as csvfile:
            writer = csv.writer(
                csvfile, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
            )
            writer.writerow()
            works = (
                models.Work.objects.order_by("pk")
                .select_related("conference__country")
                .prefetch_related(
                    "conference",
                    "conference__series",
                    "conference__organizers",
                    "conference__hosting_institutions",
                    "conference__hosting_institutions__country",
                    "keywords",
                    "languages",
                    "disciplines",
                    "topics",
                    "work_type",
                    "full_text_license",
                )
            )
            bar = Bar("Exporting works", max=works.count())
            for w in works:
                bar.next()
                row = [
                    w.pk,
                    w.conference.short_title,
                    w.conference.theme_title,
                    w.conference.year,
                    ";".join([str(o) for o in w.conference.organizers.all()]),
                    ";".join([str(s) for s in w.conference.series.all()]),
                    ";".join([str(s) for s in w.conference.hosting_institutions.all()]),
                    w.conference.city,
                    w.conference.state_province_region,
                    w.conference.country,
                    w.conference.url,
                    w.conference.notes,
                    w.title,
                    w.url,
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
