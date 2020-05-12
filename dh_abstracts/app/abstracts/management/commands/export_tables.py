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
        if f[2]:
            all_ids = getattr(obj, f[0]).all().values_list("id", flat=True)
            return ";".join([str(i) for i in all_ids])
        if getattr(obj, f[0]) is not None:
            if f[1]:
                return getattr(obj, f[0]).id
            else:
                return getattr(obj, f[0])
        else:
            return None

    def write_model_csv(self, qs, filename, exclude_fields=[]):
        model = qs.model
        all_model_fields = [(f.name, f.is_relation, False) for f in model._meta.fields]
        m2m_fields = [(f.name, f.is_relation, True) for f in model._meta.many_to_many]
        censored_fields = [
            f for f in all_model_fields + m2m_fields if f[0] not in exclude_fields
        ]
        with open(filename, "w") as csv_file:
            writer = csv.writer(
                csv_file, dialect=csv.unix_dialect, quoting=csv.QUOTE_ALL
            )
            writer.writerow([f[0] for f in censored_fields])
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
