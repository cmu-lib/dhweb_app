from django.core.management.base import BaseCommand
from django.conf import settings
from abstracts import models
import csv
import tempfile
from zipfile import ZipFile
from operator import attrgetter


class Command(BaseCommand):
    help = "Export and zip CSVs of most models"

    def get_obj_field(self, obj, f):
        # if the field is a foreign key, retrieve id only
        if getattr(obj, f["name"]) is not None:
            if f["relation"]:
                return getattr(obj, f["name"]).id
            else:
                return getattr(obj, f["name"])
        else:
            return None

    def write_model_csv(self, qs, filename, exclude_fields=[]):
        model = qs.model
        all_model_fields = [
            {"name": f.name, "relation": f.is_relation}
            for f in model._meta.fields
            if not f.one_to_many
        ]
        # Don't include reverse fields
        censored_fields = [
            f for f in all_model_fields if f["name"] not in exclude_fields
        ]
        with open(filename, "w") as csv_file:
            writer = csv.writer(
                csv_file, dialect=csv.unix_dialect, quoting=csv.QUOTE_ALL
            )
            writer.writerow([f["name"] for f in censored_fields])
            for obj in qs.order_by("id"):
                row = [self.get_obj_field(obj, f) for f in censored_fields]
                writer.writerow(row)
        return filename

    def handle(self, *args, **options):
        with tempfile.TemporaryDirectory() as tdir:
            zip_path = f"{settings.DATA_OUTPUT_PATH}/{settings.DATA_ZIP_NAME}"
            with ZipFile(zip_path, "w") as dat_zip:
                for export_conf in settings.DATA_TABLE_CONFIG:
                    final_csvname = (
                        export_conf["model"]
                        .replace(".through", "")
                        .replace(".", "_")
                        .lower()
                    )
                    print(attrgetter(export_conf["model"])(models))
                    dat_zip.write(
                        self.write_model_csv(
                            qs=attrgetter(export_conf["model"])(models).objects.all(),
                            filename=f"{tdir}/{tempfile.TemporaryFile()}",
                            exclude_fields=export_conf["exclude_fields"],
                        ),
                        arcname=f"dh_conferences_data/{final_csvname}.csv",
                    )
                dat_zip.close()
