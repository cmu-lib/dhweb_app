"""
Import Works
"""

from abstracts.models import (
    Conference,
    Organizer,
    ConferenceSeries,
    SeriesMembership,
    Work,
    Author,
    Keyword,
    Topic,
    Language,
    Discipline,
    Authorship,
    Appellation,
    Affiliation,
    Institution,
    Country,
    WorkType,
    FileImport,
    FileImportTries,
    FileImportMessgaes,
)

from parsel import Selector
from glob import glob
from django.core.management.base import BaseCommand
import re
from django.db.models.query import QuerySet
from pprint import PrettyPrinter


def object_status(command, object, attempt):
    actual = object[0]

    if object[1]:
        FileImportMessgaes.objects.create(
            attempt=attempt,
            message=f"Created new {type(actual).__name__} {actual}",
            addition_type="new",
        )
    else:
        FileImportMessgaes.objects.create(
            attempt=attempt,
            message=f"Matched with {type(actual).__name__} {actual}",
            addition_type="mat",
        )


class Command(BaseCommand):
    help = "Load a Digital Humanities TEI XML file into the database, linking to exisitng records and creating new ones as needed."

    def add_arguments(self, parser):
        parser.add_argument("filepath", nargs="+")
        parser.add_argument(
            "--conference",
            dest="default_conference",
            help="Primary key of the conference that all works will be added to.",
            type=int,
        )

    def handle(self, *args, **options):

        """
        Find conference. If you put in a bad ID, then this stops right away.
        """
        target_conference = Conference.objects.get(pk=options["default_conference"])

        print(options)
        all_files = glob(f"{options['filepath'][0]}/**/*.xml", recursive=True)
        print(all_files)
        for f in all_files:
            # Get or create filename and start new attempt record
            fn = FileImport.objects.get_or_create(path=f)
            attempt = FileImportTries(file_name=fn[0], conference=target_conference)
            attempt.save()

            self.stdout.write(self.style.SUCCESS(f))
            with open(f, "r") as xmlpath:
                xml = Selector(text=xmlpath.read())

                # For now, skip over teicorpora
                if xml.xpath("//teicorpus").get() is not None:
                    FileImportMessgaes.objects.create(
                        attempt=attempt,
                        message="File contains a teicorpus. Skipping.",
                        warning=True,
                    )
                    continue

                work_type = xml.xpath("//keywords[@n='subcategory']/term/text()").get()
                if work_type is None:
                    work_type = xml.xpath("//keywords[@n='category']/term/text()").get()
                work_type = work_type.lower()
                # titles + subtitles will result in multiple possible title nodes. We just concatenate them here.
                work_title = " ".join(
                    xml.xpath("//titlestmt//title/text()").getall()
                ).strip()
                work_state = "ac"
                work_full_text = xml.xpath("//text").get()
                keywords = xml.xpath("//keywords[@n='keywords']/term/text()").getall()
                topics = xml.xpath(
                    "//keywords[@n='topics']/term/text() | //keywords[@n='topic']/term/text()"
                ).getall()

                new_work = Work.objects.get_or_create(
                    conference=target_conference,
                    title=work_title,
                    state=work_state,
                    work_type=WorkType.objects.get_or_create(title=work_type)[0],
                    full_text=work_full_text,
                    full_text_type="xml",
                )

                object_status(self, new_work, attempt)
                new_work = new_work[0]

                for kw in keywords:
                    for kkw in re.split("[;,]", kw):
                        target_kw = Keyword.objects.get_or_create(
                            title=kkw.strip().lower()
                        )
                        object_status(self, target_kw, attempt)
                        new_work.keywords.add(target_kw[0])

                for tp in topics:
                    for ttp in re.split("[;,]", tp):
                        target_tp = Topic.objects.get_or_create(title=ttp.lower())
                        object_status(self, target_tp, attempt)
                        new_work.topics.add(target_tp[0])

                """
                Authors
                """

                n_authors = len(xml.xpath("//filedesc//author"))
                for idx in range(n_authors):
                    first_name = xml.xpath(f"//author[{idx+1}]//forename/text()").get()
                    last_name = xml.xpath(f"//author[{idx+1}]//surname/text()").get()
                    affiliation = xml.xpath(
                        f"//author[{idx+1}]/affiliation/text()"
                    ).get()

                    if first_name is None:
                        first_name = ""
                    if last_name is None:
                        last_name = ""

                    target_app = Appellation.objects.get_or_create(
                        first_name=first_name, last_name=last_name
                    )
                    object_status(self, target_app, attempt)
                    target_app = target_app[0]

                    possible_authors = Author.objects.filter(
                        appellations=target_app
                    ).distinct()

                    if possible_authors.count() == 0:
                        target_author = Author()
                        target_author.save()
                        object_status(self, (target_author, True), attempt)
                    else:
                        target_author = possible_authors.first()
                        object_status(self, (target_author, False), attempt)

                    if affiliation is not None:

                        """
                        Try to split out country and institution
                        """

                        split_affiliation = affiliation.split(",")
                        # Try to find a matching institution first; if not that, then fall back to the country

                        institution = None
                        country = None
                        for particle in split_affiliation:
                            ustrip = particle
                            particle = particle.strip()

                            if (
                                institution is None
                                and Institution.objects.filter(name=particle).exists()
                            ):
                                institution = Institution.objects.filter(
                                    name=particle
                                ).first()
                                split_affiliation.remove(ustrip)
                                object_status(self, (institution, False), attempt)

                            if (
                                country is None
                                and Country.objects.filter(name=particle).exists()
                            ):
                                country = Country.objects.get(name=particle)
                                object_status(self, (country, False), attempt)
                                split_affiliation.remove(ustrip)

                        # After clearing out matching institution and/or country texts, reassemble the affiliation statement.
                        affiliation = ", ".join(split_affiliation)

                        if institution is None:
                            # If no institution was matched, create one
                            if country is not None:
                                # If a country was matched, attach it to the new institution
                                target_institution = Institution.objects.get_or_create(
                                    name=affiliation, country=country
                                )
                            else:
                                #  otherwise leave the country blank
                                target_institution = Institution.objects.get_or_create(
                                    name=affiliation, country=None
                                )
                            object_status(self, target_institution, attempt)
                            target_institution = target_institution[0]
                        else:
                            # If we matched an institutuion, go ahead and use it
                            target_institution = institution

                        # finally, create or retreive the affiliation statement by attaching the non-institutuion, non-country text as the department, and point to the matched-or-created institution
                        target_affiliation = Affiliation.objects.get_or_create(
                            department=affiliation, institution=target_institution
                        )
                        object_status(self, target_affiliation, attempt)
                        target_affiliation = target_affiliation[0]

                    new_authorship = Authorship.objects.get_or_create(
                        work=new_work,
                        author=target_author,
                        appellation=target_app,
                        authorship_order=idx,
                    )
                    object_status(self, new_authorship, attempt)
                    new_authorship = new_authorship[0]

                    if affiliation is not None:
                        new_authorship.affiliations.add(target_affiliation)
