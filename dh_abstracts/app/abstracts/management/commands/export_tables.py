from django.core.management.base import BaseCommand
from django.conf import settings
from django.db.models import Q
from abstracts import models
import csv
import tempfile
from zipfile import ZipFile


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
                dat_zip.write(
                    self.write_model_csv(
                        qs=models.Work.objects.all(),
                        filename=f"{tdir}/{tempfile.TemporaryFile()}",
                        exclude_fields=[
                            "search_text",
                            "last_updated",
                            "user_last_updated",
                        ],
                    ),
                    arcname="dh_conferences_data/works.csv",
                )
                dat_zip.write(
                    self.write_model_csv(
                        qs=models.Author.objects.all(),
                        filename=f"{tdir}/{tempfile.TemporaryFile()}",
                    ),
                    arcname="dh_conferences_data/authors.csv",
                )
                dat_zip.write(
                    self.write_model_csv(
                        qs=models.Conference.objects.all(),
                        filename=f"{tdir}/{tempfile.TemporaryFile()}",
                        exclude_fields=["last_updated", "user_last_updated"],
                    ),
                    arcname="dh_conferences_data/conferences.csv",
                )
                dat_zip.write(
                    self.write_model_csv(
                        qs=models.ConferenceSeries.objects.all(),
                        filename=f"{tdir}/{tempfile.TemporaryFile()}",
                    ),
                    arcname="dh_conferences_data/conference_series.csv",
                )
                dat_zip.write(
                    self.write_model_csv(
                        qs=models.SeriesMembership.objects.all(),
                        filename=f"{tdir}/{tempfile.TemporaryFile()}",
                    ),
                    arcname="dh_conferences_data/series_memberships.csv",
                )
                dat_zip.write(
                    self.write_model_csv(
                        qs=models.Organizer.objects.all(),
                        filename=f"{tdir}/{tempfile.TemporaryFile()}",
                    ),
                    arcname="dh_conferences_data/organizers.csv",
                )
                dat_zip.write(
                    self.write_model_csv(
                        qs=models.Authorship.objects.all(),
                        filename=f"{tdir}/{tempfile.TemporaryFile()}",
                        exclude_fields=["last_updated", "user_last_updated"],
                    ),
                    arcname="dh_conferences_data/authorships.csv",
                )
                dat_zip.write(
                    self.write_model_csv(
                        qs=models.Appellation.objects.all(),
                        filename=f"{tdir}/{tempfile.TemporaryFile()}",
                    ),
                    arcname="dh_conferences_data/appellations.csv",
                )
                dat_zip.write(
                    self.write_model_csv(
                        qs=models.Institution.objects.all(),
                        filename=f"{tdir}/{tempfile.TemporaryFile()}",
                    ),
                    arcname="dh_conferences_data/institutions.csv",
                )
                dat_zip.write(
                    self.write_model_csv(
                        qs=models.Affiliation.objects.all(),
                        filename=f"{tdir}/{tempfile.TemporaryFile()}",
                    ),
                    arcname="dh_conferences_data/affiliations.csv",
                )
                dat_zip.write(
                    self.write_model_csv(
                        qs=models.Country.objects.filter(
                            Q(conferences__isnull=False)
                            | Q(institutions__affiliations__asserted_by__isnull=False)
                        ).distinct(),
                        filename=f"{tdir}/{tempfile.TemporaryFile()}",
                        exclude_fields=["names"],
                    ),
                    arcname="dh_conferences_data/countries.csv",
                )
                dat_zip.write(
                    self.write_model_csv(
                        qs=models.Keyword.objects.all(),
                        filename=f"{tdir}/{tempfile.TemporaryFile()}",
                    ),
                    arcname="dh_conferences_data/keywords.csv",
                )
                dat_zip.write(
                    self.write_model_csv(
                        qs=models.Topic.objects.all(),
                        filename=f"{tdir}/{tempfile.TemporaryFile()}",
                    ),
                    arcname="dh_conferences_data/topics.csv",
                )
                dat_zip.write(
                    self.write_model_csv(
                        qs=models.WorkType.objects.all(),
                        filename=f"{tdir}/{tempfile.TemporaryFile()}",
                    ),
                    arcname="dh_conferences_data/work_types.csv",
                )
                dat_zip.write(
                    self.write_model_csv(
                        qs=models.Discipline.objects.all(),
                        filename=f"{tdir}/{tempfile.TemporaryFile()}",
                    ),
                    arcname="dh_conferences_data/disciplines.csv",
                )
                dat_zip.write(
                    self.write_model_csv(
                        qs=models.Language.objects.all(),
                        filename=f"{tdir}/{tempfile.TemporaryFile()}",
                    ),
                    arcname="dh_conferences_data/languages.csv",
                )
                dat_zip.close()
