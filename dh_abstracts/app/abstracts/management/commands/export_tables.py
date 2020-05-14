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

    def write_csvs(self, dt_config):
        with tempfile.TemporaryDirectory() as tdir:
            zip_path = f"{settings.DATA_OUTPUT_PATH}/{dt_config['DATA_ZIP_NAME']}"
            with ZipFile(zip_path, "w") as dat_zip:
                for export_conf in dt_config["CONFIGURATION"]:
                    final_csvname = export_conf["csv_name"]
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

    def write_public_csvs(self):
        print("Writing public CSVs")
        self.write_csvs(settings.PUBLIC_DATA_TABLE_CONFIG)

    def write_private_csvs(self):
        print("Writing private CSVs")
        self.write_csvs(settings.PRIVATE_DATA_TABLE_CONFIG)

    def write_denormalized_csvs(self):
        print("Writing Denormalized CSV")
        with tempfile.TemporaryDirectory() as tdir:
            all_works = (
                models.Work.objects.order_by("id")
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
            zip_path = (
                f"{settings.DATA_OUTPUT_PATH}/{settings.DENORMALIZED_WORKS_NAME}.zip"
            )
            csv_path = f"{tdir}/{settings.DENORMALIZED_WORKS_NAME}.csv"

            header_names = [
                "work_id",
                "conference_short_title",
                "conference_theme_title",
                "conference_year",
                "conference_organizers",
                "conference_series",
                "conference_hosting_institutions",
                "conference_city",
                "conference_state",
                "conference_country",
                "conference_url",
                "work_title",
                "work_url",
                "work_authors",
                "work_type",
                "parent_work_id",
                "keywords",
                "languages",
                "disciplines",
                "topics",
            ]

            with ZipFile(zip_path, "w") as dat_zip:
                with open(csv_path, "w") as csv_file:
                    writer = csv.writer(
                        csv_file, dialect=csv.unix_dialect, quoting=csv.QUOTE_ALL
                    )
                    writer.writerow(header_names)
                    for w in all_works:
                        try:
                            parent_session_id = w.parent_session.id
                        except:
                            parent_session_id = None
                        row_data = [
                            w.pk,
                            w.conference.short_title,
                            w.conference.theme_title,
                            w.conference.year,
                            ";".join([str(o) for o in w.conference.organizers.all()]),
                            ";".join([str(s) for s in w.conference.series.all()]),
                            ";".join(
                                [
                                    str(s)
                                    for s in w.conference.hosting_institutions.all()
                                ]
                            ),
                            w.conference.city,
                            w.conference.state_province_region,
                            w.conference.country,
                            w.conference.url,
                            w.title,
                            w.url,
                            ";".join([str(a.appellation) for a in w.authorships.all()]),
                            w.work_type,
                            parent_session_id,
                            ";".join([str(k) for k in w.keywords.all()]),
                            ";".join([str(k) for k in w.languages.all()]),
                            ";".join([str(k) for k in w.disciplines.all()]),
                            ";".join([str(k) for k in w.topics.all()]),
                        ]
                        writer.writerow(row_data)
                dat_zip.write(
                    csv_path, arcname=f"{settings.DENORMALIZED_WORKS_NAME}.csv"
                )
            dat_zip.close()

    def handle(self, *args, **options):
        # self.write_private_csvs()
        # self.write_public_csvs()
        self.write_denormalized_csvs()
