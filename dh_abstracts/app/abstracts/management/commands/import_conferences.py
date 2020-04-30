from glob import glob
from django.core.management.base import BaseCommand
from abstracts import models
import re
import csv
import datetime
from django.db import transaction


def get_country(s):
    try:
        return models.Country.objects.get(names__name=s)
    except:
        return None


def get_organizer(s):
    try:
        return models.Organizer.objects.get(abbreviation=s)
    except:
        try:
            return models.Organizer.objects.get(name=s)
        except:
            return models.Organizer.objects.create(name=s, abbreviation=s)


class Command(BaseCommand):
    help = "One-time load of DH conferences spreadsheet into the database"

    def add_arguments(self, parser):
        parser.add_argument("filepath", nargs="+")

    @transaction.atomic
    def handle(self, *args, **options):

        with open(options["filepath"][0], newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # Find/create hosting institutions
                print(row)
                this_country = get_country(row["Country"])
                hosting_institutions = []
                if row["Hosting Institution(s) Location"] != "":
                    for inst in row["Hosting Institution(s) Location"].split(";"):
                        this_institution = models.Institution.objects.get_or_create(
                            name=inst
                        )[0]
                        # Add city and country info if it's not there already
                        if this_institution.city == "":
                            this_institution.city = row["City"]
                            this_institution.country = this_country
                            this_institution.save()
                        hosting_institutions.append(this_institution)

                # Find/create organizations
                conf_organizers = []
                if row["Professional/Regional Organization (if applicable)"] != "":
                    for org in row[
                        "Professional/Regional Organization (if applicable)"
                    ].split(";"):
                        this_org = get_organizer(org)
                        conf_organizers.append(this_org)

                format_str = "%d/%m/%Y"

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

                # Create the base conference
                conference = models.Conference.objects.create(
                    year=int(row["Year"]),
                    theme_title=row["Theme Title"],
                    short_title=row["Hosting Institution(s) Location"],
                    start_date=start_date,
                    end_date=end_date,
                    city=row["City"],
                    state_province_region=row["State/Province/Region"],
                    country=this_country,
                    url=row["URL"],
                    references=row["Reference"],
                    notes=row["Notes"],
                    contributors=row["Contributors of Details"].rstrip(","),
                    attendance=row["Attendance"],
                    primary_contact=row["Primary Contact"],
                )

                conference.organizers.set(conf_organizers)
                conference.hosting_institutions.set(hosting_institutions)

                # Create and set series
                if row["Recurring Title"] != "":
                    for series_string in row["Recurring Title"].split(";"):
                        split_series = series_string.split(" - ")
                        series = models.ConferenceSeries.objects.get_or_create(
                            abbreviation=split_series[0]
                        )[0]
                        if series.title == "":
                            series.title = split_series[0]
                            series.save()
                        membership = models.SeriesMembership.objects.create(
                            conference=conference,
                            series=series,
                            number=int(split_series[1]),
                        )

                print(conference)
                print(conf_organizers)
                print(hosting_institutions)
