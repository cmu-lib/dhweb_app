from django.core import management
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Dump CSVs of all data as well as a JSON-seriazlied fixture of all models to /static, then runs collectstatic"

    def handle(self, *args, **options):
        management.call_command("export_works_csv")
        management.call_command("export_authorships_csv")
        management.call_command("export_affiliations_csv")
        management.call_command(
            "dumpdata",
            "abstracts",
            indent=2,
            output="abstracts/static/downloads/full.json",
        )
        management.call_command("collectstatic", interactive=False)