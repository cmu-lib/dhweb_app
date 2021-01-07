"""
Import Works
"""

from abstracts.models import Conference
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Load a directory of ADHO TEI XML files into the database, linking to existing records and creating new ones as needed."

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
        target_conference.import_xml_directory(options["filepath"][0])
