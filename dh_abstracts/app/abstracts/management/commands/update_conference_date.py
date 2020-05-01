from django.core.management.base import BaseCommand
from abstracts import models
import csv
import datetime
from django.db import transaction


class Command(BaseCommand):
    help = "One-time command to update conference date"

    def add_arguments(self, parser):
        parser.add_argument("filepath", nargs="+")

    @transaction.atomic
    def handle(self, *args, **options):
        with open(options["filepath"][0], newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:

                format_str = "%m/%d/%Y"

                try:
                    start_date = datetime.datetime.strptime(
                        row["Start Date"], format_str
                    )
                except:
                    start_date = None
                try:
                    end_date = datetime.datetime.strptime(row["End Date"], format_str)
                except:
                    end_date = None

                models.Conference.objects.filter(id=row["live_pk"]).update(
                    start_date=start_date, end_date=end_date
                )
