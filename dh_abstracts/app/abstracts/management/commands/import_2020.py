from django.core.management.base import BaseCommand
from abstracts import models
import re
import csv
from django.db import transaction


class Command(BaseCommand):
    help = "One-time load of DH 2020"

    def add_arguments(self, parser):
        pass

    @transaction.atomic
    def handle(self, *args, **options):
        with open("/vol/data/metadata_V4.csv", "r") as csvfile:
            reader = csv.DictReader(csvfile)
            adho2020 = models.Conference.objects.get(id=495)
            models.Work.objects.filter(conference=adho2020).delete()
            for work in reader:
                # print(work)
                # Grab authors
                authors_dict = []
                for author in work["authors"].split(";"):
                    name = re.match(r"^[^(]+", author).group(0)
                    last_name = name.split(",")[0].strip()
                    first_name = name.split(",")[1].strip()
                    raw_institutions = re.search(r"\(([0-9](?:,[0-9])*)\)", author)
                    if raw_institutions is not None:
                        institution_nos = [
                            int(i) for i in raw_institutions.group(1).split(",")
                        ]
                    else:
                        institution_nos = [0]
                    appellation_object = models.Appellation.objects.get_or_create(
                        first_name=first_name, last_name=last_name
                    )[0]
                    author_object = models.Author.objects.filter(
                        authorships__appellation__first_name=first_name.strip(),
                        authorships__appellation__last_name=last_name.strip(),
                    ).first()
                    authors_dict.append(
                        {
                            "appellation_object": appellation_object,
                            "author_object": author_object,
                            "institution_nos": institution_nos,
                        }
                    )

                institution_dict = []
                if re.search(r"\d: ", work["organisations"]) is not None:
                    for institution in re.findall(
                        r"\d:[^0-9;]+", work["organisations"]
                    ):
                        number = re.search(r"(\d)", institution)
                        institution_no = int(number.group(1))
                        namestring = re.search(r"\d: (.+)", institution).group(1)
                        institution_dict.append(
                            {
                                "institution_no": institution_no,
                                "institution_name": namestring,
                            }
                        )
                else:
                    institution_no = 0
                    namestring = work["organisations"]
                    institution_dict.append(
                        {
                            "institution_no": institution_no,
                            "institution_name": namestring,
                        }
                    )

                keywords = []
                for kw in re.split(r"[,;]", work["keywords"]):
                    keyword = models.Keyword.objects.get_or_create(title=kw.strip())[0]
                    keywords.append(keyword)

                disciplines = []
                for disc in re.split(r",", work["tg5_Disciplines_Fields_of_Study"]):
                    discipline = models.Discipline.objects.get_or_create(
                        title=disc.strip()
                    )[0]
                    disciplines.append(discipline)

                abstract = models.Work.objects.create(
                    conference=adho2020,
                    title=work["title_plain"],
                    full_text=work["Abstract"],
                    full_text_type="txt",
                    work_type=models.WorkType.objects.get_or_create(
                        title=work["acceptance"]
                    )[0],
                )

                abstract.keywords.set(keywords)
                abstract.disciplines.set(disciplines)

                for author in authors_dict:
                    if author["author_object"] is None:
                        real_author = models.Author.objects.create()
                    else:
                        real_author = author["author_object"]

                    authorship = models.Authorship.objects.get_or_create(
                        work=abstract,
                        appellation=author["appellation_object"],
                        author=real_author,
                    )[0]

                    for institution_no in author["institution_nos"]:
                        institution_name = [
                            i["institution_name"]
                            for i in institution_dict
                            if i["institution_no"] == institution_no
                        ][0]
                        candidate_institutions = models.Institution.objects.filter(
                            name=institution_name
                        )
                        if bool(candidate_institutions):
                            institution = candidate_institutions[0]
                        else:
                            institution = models.Institution.objects.create(
                                name=institution_name
                            )
                        affiliation = models.Affiliation.objects.get_or_create(
                            department="", institution=institution
                        )[0]
                        authorship.affiliations.add(affiliation)

        for a in models.Author.objects.all():
            a.save()
