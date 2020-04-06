from django.core import management
from django.core.management.base import BaseCommand
from datetime import date
import os
from glob import glob


class Command(BaseCommand):
    help = "Dump CSVs of all data as well as a JSON-seriazlied fixture of all models to /static, then runs collectstatic"

    def handle(self, *args, **options):
        dl_dir = "abstracts/static/downloads"
        # Wipe existing data
        old_files = glob(f"{dl_dir}/*")
        for fl in old_files:
            os.unlink(fl)
        management.call_command("export_works_csv")
        management.call_command("export_authorships_csv")
        management.call_command("export_affiliations_csv")
        management.call_command(
            "dumpdata",
            "abstracts",
            indent=2,
            output=f"{dl_dir}/{date.today().strftime('%Y-%m-%d')}_full.json",
        )
        management.call_command("collectstatic", interactive=False)
