import datetime
from django.db import models
from django.db.models import Max, Count
from django.utils import timezone
from django.urls import reverse
from django.contrib.sites.models import Site
from django.contrib.redirects.models import Redirect
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVector, SearchVectorField
from django.contrib.auth.models import User
from filer.fields.file import FilerFileField
from os.path import basename
from glob import glob
from parsel import Selector
import re


class ChangeTrackedModel(models.Model):
    last_updated = models.DateTimeField(auto_now=True, db_index=True)
    user_last_updated = models.ForeignKey(
        User,
        null=True,
        on_delete=models.SET_NULL,
        related_name="%(class)ss_last_updated",
    )

    class Meta:
        abstract = True


class TextIndexedModel(models.Model):
    search_text = SearchVectorField(null=True, editable=False)

    class Meta:
        abstract = True
        indexes = [GinIndex(fields=["search_text"])]


class ConferenceSeries(models.Model):
    model_description = "A formalized series of multiple events, such as an annual conference or recurring symposium"
    title = models.CharField(max_length=200, unique=True, help_text="Full name")
    abbreviation = models.CharField(
        max_length=100, unique=True, help_text="Display abbreviation"
    )
    notes = models.TextField(
        blank=True,
        null=False,
        default="",
        help_text="Discursive notes, generally concerning the history of this series",
    )

    @property
    def all_organizers(self):
        return Organizer.objects.filter(conferences_organized__series=self).distinct()

    def __str__(self):
        if self.abbreviation != "":
            return self.abbreviation
        else:
            return self.title

    def get_absolute_url(self):
        return reverse("conference_series_detail", kwargs={"pk": self.pk})

    class Meta:
        ordering = ["abbreviation"]


class Conference(models.Model):
    ENTRY_STATUS = (
        ("n", "Not started"),
        ("i", "Incomplete"),
        ("r", "Needs review"),
        ("c", "Complete"),
    )

    model_description = "A scholarly event with organized presentations, such as a conference, symposium, or workshop."
    year = models.PositiveIntegerField(help_text="Year the conference was held")
    short_title = models.CharField(
        max_length=200,
        blank=True,
        help_text="A location-based short title for the conference",
    )
    series = models.ManyToManyField(
        ConferenceSeries,
        through="SeriesMembership",
        through_fields=("conference", "series"),
        related_name="conferences",
        blank=True,
        help_text="Conference series which this event belongs to",
    )
    notes = models.TextField(
        max_length=200000,
        blank=True,
        null=False,
        default="",
        help_text="Further descriptive information",
    )
    url = models.URLField(
        max_length=500,
        blank=True,
        verbose_name="URL",
        help_text="Public URL for the conference and/or conference program",
    )
    theme_title = models.CharField(
        max_length=1000,
        blank=True,
        null=False,
        default="",
        help_text="Optional thematic title (e.g. 'Big Tent Digital Humanities')",
    )
    start_date = models.DateField(null=True, blank=True, help_text="YYYY-MM-DD")
    end_date = models.DateField(null=True, blank=True, help_text="YYYY-MM-DD")
    city = models.CharField(
        max_length=1000,
        blank=True,
        null=False,
        default="",
        help_text="City where the conference took place",
    )
    hosting_institutions = models.ManyToManyField(
        "Institution",
        related_name="conferences",
        blank=True,
        help_text="Institutions that organized the conference",
    )
    state_province_region = models.CharField(
        max_length=1000,
        blank=True,
        null=False,
        default="",
        verbose_name="State / Province / Region",
        help_text="State, province, or region where the conference was held",
    )
    country = models.ForeignKey(
        "Country",
        related_name="conferences",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    references = models.TextField(
        max_length=20000,
        blank=True,
        default="",
        help_text="Citations to conference proceedings",
    )
    contributors = models.TextField(
        max_length=20000,
        blank=True,
        default="",
        help_text="Individuals or organizations who contributed data about this conference",
    )
    attendance = models.TextField(
        max_length=20000,
        blank=True,
        default="",
        help_text="Summary information about conference attendance, with source links",
    )
    entry_status = models.CharField(
        max_length=1,
        default="n",
        choices=ENTRY_STATUS,
        blank=False,
        null=False,
        help_text="Have all the abstracts for this conference been entered?",
        db_index=True,
    )
    editing_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="User who has currently checked out this conference for data entry",
    )
    program_available = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Program available?",
        help_text="Is a program for this conference available in some format for editors to input?",
    )
    abstracts_available = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Abstracts available?",
        help_text="Are the abstracts for this conference available in some format for editors to input?",
    )
    search_text = models.CharField(
        blank=True,
        max_length=20000,
        help_text="Any searchable text that should lead to this conference",
    )

    class Meta:
        ordering = ["-year"]

    @property
    def public_works(self):
        return self.works.all()

    def public_authors(self):
        return (
            Author.objects.filter(authorships__work__in=self.public_works)
            .distinct()
            .count()
        )

    def save(self, *args, **kwargs):
        # Save the object to the DB first so that we can filter on many-to-many relations
        super().save(*args, **kwargs)
        hosting_objects = Institution.objects.filter(conferences=self).distinct()
        series_objects = ConferenceSeries.objects.filter(
            conference_memberships__conference=self
        ).distinct()
        organizer_objects = Organizer.objects.filter(
            conferences_organized=self
        ).distinct()
        # Generate the search text string and save again before returning
        new_search_text = " ".join(
            [str(self.year), self.short_title, self.city]
            + [str(hi) for hi in hosting_objects]
            + [" ".join([sr.title, sr.abbreviation]) for sr in series_objects]
            + [" ".join([sr.name, sr.abbreviation]) for sr in organizer_objects]
        )
        self.search_text = new_search_text
        res = super().save(*args, **kwargs)
        return res

    def __str__(self):
        if self.short_title != "":
            return f"{self.year} - {self.short_title}"
        elif self.theme_title != "":
            return f"{self.year} - {self.theme_title}"
        elif self.city != "":
            try:
                return f"{self.year} - {self.city} - {self.series.first().title}"
            except:
                try:
                    return f"{self.year} - {self.city} - {self.hosting_institutions.first().name}"
                except:
                    return f"{self.year} - {self.city}"
        else:
            try:
                return f"{self.year} - {self.hosting_institutions.first().name}"
            except:
                return f"{self.year} - {self.series.first().title}"

    def get_absolute_url(self):
        return reverse("conference_edit", kwargs={"pk": self.pk})

    def import_xml_directory(self, dirpath):
        all_files = glob(f"{dirpath}/**/*.xml", recursive=True)
        successful_files = []
        failed_files = []
        for filepath in all_files:
            try:
                self.import_xml_file(filepath)
                successful_files.append(filepath)
            except Exception as e:
                failed_files.append({"filepath": filepath, "error": e})
                continue

        return {"successful_files": successful_files, "failed_files": failed_files}

    def import_xml_file(self, filepath):
        fn = FileImport.objects.get_or_create(path=filepath)
        attempt = FileImportTries(file_name=fn[0], conference=self)
        attempt.save()
        with open(filepath, "r") as xmlpath:
            xml = Selector(text=xmlpath.read())

            # For now, skip over teicorpora
            if xml.xpath("//teicorpus").get() is not None:
                err = f"{filepath} contained a <teicorpus> and is not valid."
                attempt.add_message(err, warning=True)
                raise err

            work_type = xml.xpath("//keywords[@n='subcategory']/term/text()").get()
            if work_type is None:
                work_type = xml.xpath("//keywords[@n='category']/term/text()").get()
            work_type = work_type.lower()
            # titles + subtitles will result in multiple possible title nodes. We just concatenate them here.
            work_title = " ".join(
                xml.xpath("//titlestmt//title/text()").getall()
            ).strip()
            work_full_text = xml.xpath("//text").get()
            keywords = xml.xpath("//keywords[@n='keywords']/term/text()").getall()
            topics = xml.xpath(
                "//keywords[@n='topics']/term/text() | //keywords[@n='topic']/term/text()"
            ).getall()
            language_code = xml.xpath("//text").attrib["lang"]
            language = Language.objects.get(code=language_code)

            new_work = Work.objects.get_or_create(
                conference=self,
                title=work_title,
                work_type=WorkType.objects.get_or_create(title=work_type)[0],
                full_text=work_full_text,
                full_text_type="xml",
            )[0]

            new_work.languages.add(language)

            for kw in keywords:
                for kkw in re.split("[;,]", kw):
                    target_kw = Keyword.objects.get_or_create(title=kkw.strip().lower())
                    attempt.add_get_or_create_response(target_kw)
                    new_work.keywords.add(target_kw[0])

            for tp in topics:
                for ttp in re.split("[;,]", tp):
                    target_tp = Topic.objects.get_or_create(title=ttp.lower())
                    attempt.add_get_or_create_response(target_tp)
                    new_work.topics.add(target_tp[0])

            """
            Authors
            """

            n_authors = len(xml.xpath("//filedesc//author"))
            for idx in range(n_authors):
                first_name = xml.xpath(f"//author[{idx+1}]//forename/text()").get()
                last_name = xml.xpath(f"//author[{idx+1}]//surname/text()").get()

                if first_name is None:
                    first_name = ""
                if last_name is None:
                    last_name = ""

                target_app = Appellation.objects.get_or_create(
                    first_name=first_name, last_name=last_name
                )
                attempt.add_get_or_create_response(target_app)
                target_app = target_app[0]

                possible_authors = Author.objects.filter(
                    appellations=target_app
                ).distinct()

                if possible_authors.count() == 0:
                    target_author = Author()
                    target_author.save()
                    attempt.add_create_response(target_author)
                else:
                    target_author = possible_authors.first()
                    attempt.add_create_response(target_author)

                all_affiliations = affiliation = xml.xpath(
                    f"//author[{idx+1}]/affiliation"
                )
                final_affiliation_list = []
                for aff_idx in range(len(all_affiliations)):

                    # Get affiliation name if present
                    affiliation_name = xml.xpath(
                        f"//author[{idx+1}]/affiliation[{aff_idx + 1}]/orgname/name[@type='sub']/text()"
                    ).get()

                    if affiliation_name is None:
                        affiliation_name = ""

                    # Match institution if possible
                    institution_name = xml.xpath(
                        f"//author[{idx+1}]/affiliation[{aff_idx + 1}]/orgname/name[@type='main']/text()"
                    ).get()

                    if institution_name is None:
                        institution_name = ""
                    top_institution = Institution.objects.filter(
                        name__icontains=institution_name
                    ).first()
                    if top_institution is None:
                        # Try to find country, then create the institution
                        city_name = xml.xpath(
                            f"//author[{idx+1}]/affiliation[{aff_idx + 1}]/district/text()"
                        ).get()
                        if city_name is None:
                            city_name = ""

                        country_name = xml.xpath(
                            f"//author[{idx+1}]/affiliation[{aff_idx + 1}]/orgname/name[@type='main']/text()"
                        ).get()
                        if country_name is None:
                            country_name = ""

                        top_country = (
                            Country.objects.filter(names__name=country_name)
                            .annotate(
                                n_institutions=Count("institutions", distinct=True)
                            )
                            .order_by("-n_institutions")
                            .first()
                        )
                        top_institution = Institution.objects.get_or_create(
                            name=institution_name,
                            city=city_name,
                            country=top_country,
                        )
                        attempt.add_get_or_create_response(top_institution)
                        top_institution = top_institution[0]

                    # Create an affiliation

                    top_affiliation = Affiliation.objects.get_or_create(
                        department=affiliation_name,
                        institution=top_institution,
                    )
                    attempt.add_get_or_create_response(top_affiliation)
                    final_affiliation_list.append(top_affiliation[0])

                new_authorship = Authorship.objects.get_or_create(
                    work=new_work,
                    author=target_author,
                    appellation=target_app,
                    authorship_order=idx + 1,
                )
                attempt.add_get_or_create_response(new_authorship)
                new_authorship = new_authorship[0]
                for target_affiliation in final_affiliation_list:
                    new_authorship.affiliations.add(target_affiliation)

        return filepath


class ConferenceDocument(models.Model):
    document = FilerFileField(
        null=True,
        blank=True,
        related_name="document_conference",
        on_delete=models.CASCADE,
    )
    conference = models.ForeignKey(
        Conference, on_delete=models.CASCADE, related_name="documents"
    )

    @property
    def basename(self):
        try:
            return basename(self.document.file.name)
        except:
            return f"File not found"

    @property
    def url(self):
        return self.document.url

    @property
    def size(self):
        try:
            return self.document.file.size
        except:
            return f"File not found"


class Organizer(ChangeTrackedModel):
    model_description = "An organizer of academic events, such as a scholarly association or academic center."
    name = models.CharField(max_length=200, unique=True)
    abbreviation = models.CharField(max_length=100, unique=True)
    conferences_organized = models.ManyToManyField(
        Conference, related_name="organizers", blank=True
    )
    notes = models.TextField(blank=True)
    url = models.URLField(blank=True, max_length=100)

    def __str__(self):
        if self.abbreviation:
            return self.abbreviation
        else:
            return self.name

    class Meta:
        ordering = ["abbreviation"]


class SeriesMembership(models.Model):
    model_description = "Many-to-many relationships between conferences and the (potentially) multiple series they belong to."
    series = models.ForeignKey(
        ConferenceSeries,
        on_delete=models.CASCADE,
        related_name="conference_memberships",
    )
    conference = models.ForeignKey(
        Conference, on_delete=models.CASCADE, related_name="series_memberships"
    )
    number = models.IntegerField(
        blank=True, null=True, help_text="Order of this conference within this series."
    )

    class Meta:
        ordering = ["-conference__year"]
        unique_together = (("series", "conference"),)

    def __str__(self):
        return f"{self.series.title} - {self.conference}"


class Tag(models.Model):
    title = models.CharField(max_length=100, unique=True, db_index=True)

    def __str__(self):
        return self.title

    def merge(self, target):
        results = {}
        affected_works = self.works.all()
        for w in affected_works:
            target.works.add(w)
        results["update_results"] = affected_works.count()

        # Add the target tag to all the works with the origin tag
        # remove the origin tag
        delete_results = self.delete()
        return results

    class Meta:
        abstract = True
        ordering = ["title"]


class Keyword(Tag):
    model_description = "Author-supplied keywords describing the content of a work"


class Language(Tag):
    model_description = "Languages in which works are written"
    code = models.CharField(blank=True, null=True, max_length=3, unique=True)


class Topic(Tag):
    model_description = "Conference-specific controlled vocabulary of topics"
    pass


class WorkType(models.Model):
    model_description = (
        "Controlled vocabulary of work types, such as 'paper' or 'keynote'"
    )
    title = models.CharField(max_length=100, unique=True)
    is_parent = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Works of this type are considered multi-paper panels/sessions and may contain 'child' abstracts",
    )

    def __str__(self):
        return self.title

    def merge(self, target):
        results = {}
        affected_works = self.works.all()
        results["update_results"] = affected_works.update(work_type=target)
        self.delete()

        return results

    class Meta:
        ordering = ["title"]


class License(models.Model):
    model_description = "Licenses that may be applicable to full texts"
    title = models.CharField(
        max_length=100, unique=True, help_text="Full title of the license"
    )
    full_text = models.TextField(
        max_length=100_000, help_text="Full text of the license"
    )
    display_abbreviation = models.CharField(
        max_length=100,
        unique=True,
        help_text="A short, identifiable abbreviation of the license",
    )
    url = models.URLField(
        max_length=200,
        blank=True,
        null=True,
        help_text="URL with a full description of the licnese",
    )
    default = models.BooleanField(
        default=False,
        help_text="Make this license the default license applied to any work whose conference has been set to show all full texts.",
    )

    def __str__(self):
        return self.title


class Work(TextIndexedModel, ChangeTrackedModel):
    model_description = (
        "A record for a single work such as a paper, keynote, or session."
    )
    FT_TYPE = (("", "-----------"), ("xml", "XML"), ("txt", "plain text"))

    conference = models.ForeignKey(
        Conference,
        on_delete=models.CASCADE,
        related_name="works",
        help_text="The conference where this abstract was submitted/published.",
    )
    title = models.CharField(max_length=500, db_index=True, help_text="Abstract title")
    work_type = models.ForeignKey(
        WorkType,
        blank=False,
        null=True,
        on_delete=models.SET_NULL,
        related_name="works",
        help_text='Abstracts may belong to one type that has been defined by editors based on a survey of all the abstracts in this collection, e.g. "poster", "workshop", "long paper".',
    )
    full_text = models.TextField(
        blank=True,
        null=False,
        default="",
        help_text="Full text content of the abstract, including references, but excluding authorship information.",
    )
    full_text_type = models.CharField(
        max_length=3,
        choices=FT_TYPE,
        blank=True,
        null=False,
        default="",
        help_text="Format of the full text (currently either plain text, or XML)",
    )
    keywords = models.ManyToManyField(
        Keyword,
        related_name="works",
        blank=True,
        help_text="Optional keywords that are supplied by authors during submission. (Matches ANY of the keywords)",
    )
    languages = models.ManyToManyField(
        Language,
        related_name="works",
        blank=True,
        help_text="The language(s) of the text of an abstract (not to be confused with e.g. 'English' as a keyword, where the topic of the abstract concerns English.)  (Matches ANY of the languages)",
    )
    topics = models.ManyToManyField(
        Topic,
        related_name="works",
        blank=True,
        help_text="Optional topics from a conference-specific controlled vocabulary. (Matches ANY of the topics)",
    )
    full_text_license = models.ForeignKey(
        License,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        help_text="License of this full text, when known",
    )
    url = models.URLField(
        blank=True,
        null=False,
        max_length=500,
        help_text="URL where the full text of this specific abstract can be freely accessed",
    )
    parent_session = models.ForeignKey(
        "Work",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="session_papers",
        help_text="If this work was part of a multi-paper organized session, this is the entry for the parent session",
    )

    def get_absolute_url(self):
        return reverse("work_detail", kwargs={"work_id": self.id})

    @property
    def display_title(self):
        if len(self.title) > 75:
            return self.title[:75] + "..."
        else:
            return self.title

    def __str__(self):
        return self.display_title

    def save(self, *args, **kwargs):
        res = super().save(*args, **kwargs)
        # Update the search index
        Work.objects.filter(id=self.id).update(
            search_text=SearchVector("title", weight="A")
            + SearchVector("full_text", weight="B")
        )
        return res

    class Meta(TextIndexedModel.Meta):
        ordering = ["title"]


class Attribute(models.Model):
    class Meta:
        abstract = True

    @property
    def is_unused(self):
        return self.asserted_by.count() == 0


class Appellation(Attribute):
    model_description = "A name belonging to an author"
    first_name = models.CharField(
        max_length=100,
        blank=True,
        null=False,
        default="",
        db_index=True,
        help_text="Surname and/or first and middle initials",
    )
    last_name = models.CharField(
        max_length=100,
        blank=True,
        null=False,
        default="",
        db_index=True,
        help_text="Family name",
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def merge(self, target):
        merges = []
        merges.append(
            Authorship.objects.filter(appellation=self).update(appellation=target)
        )
        merges.append(self.delete())
        return merges

    class Meta:
        unique_together = (("first_name", "last_name"),)
        ordering = ["last_name", "first_name"]


class Country(models.Model):
    model_description = "A controlled vocabulary of countries"
    tgn_id = models.URLField(
        max_length=100,
        unique=True,
        help_text="Canonical ID in the Getty Thesaurus of Geographic Names",
    )
    pref_name = models.CharField(
        max_length=300,
        db_index=True,
        help_text="Preferred label for the country sourced from the Getty TGN",
    )

    def __str__(self):
        return self.pref_name

    def merge(self, target):
        affected_institutions = Institution.objects.filter(country=self)

        # If changing one of those affected countries to the new one would create an Institution that already exists, then merge that institution into the existing one

        merges = []
        for inst in affected_institutions:
            if Institution.objects.filter(name=inst.name, country=target).exists():
                merges.append(inst.merge(target))
            # Otherwise just reassign the country
            else:
                inst.country = target
                inst.save()

        merges.append(self.delete())
        return merges

    class Meta:
        ordering = ["pref_name"]


class CountryLabel(models.Model):
    name = models.CharField(max_length=300, db_index=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name="names")

    def __str__(self):
        return self.name


class Institution(ChangeTrackedModel):
    model_description = "Institutions such as universities or research centers, with which authors may be affiliated."
    name = models.CharField(max_length=500, help_text="Institution name")
    city = models.CharField(
        max_length=100,
        blank=True,
        null=False,
        default="",
        help_text="City where the institution is located",
    )
    state_province_region = models.CharField(
        max_length=1000,
        blank=True,
        null=False,
        default="",
        verbose_name="State / Province / Region",
        help_text="State, province, or region where the institution is located",
    )
    country = models.ForeignKey(
        Country,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="institutions",
        help_text="Country where the institution is located",
    )

    class Meta:
        unique_together = (("name", "country"),)
        ordering = ["name"]

    def __str__(self):
        return self.name

    def merge(self, target):
        affected_affiliations = Affiliation.objects.filter(institution=self)
        affected_conferences = Conference.objects.filter(hosting_institutions=self)

        # If changing one of those affect afiliations to the new institution would create an affiliation that already exists, then reassign those authorships to the already-existing affiliation
        results = {"update_results": affected_affiliations.count()}
        for aff in affected_affiliations:
            if Affiliation.objects.filter(
                department=aff.department, institution=target
            ).exists():
                replacement_aff = Affiliation.objects.get(
                    department=aff.department, institution=target
                )

                for affected_auth in Authorship.objects.filter(affiliations=aff).all():
                    affected_auth.affiliations.remove(aff)
                    affected_auth.affiliations.add(replacement_aff)
                # Otherwise, we can just reassign the institution
            else:
                aff.institution = target
                aff.save()
        for conf in affected_conferences:
            conf.hosting_institutions.remove(self)
            conf.hosting_institutions.add(target)
            conf.save()

        # Finally, delete the old institution
        self.delete()
        return results

    @property
    def public_affiliated_authors(self):
        return (
            Author.objects.filter(authorships__affiliations__institution=self)
            .annotate(n_works=Count("works"))
            .distinct()
            .order_by("-n_works")
        )

    @property
    def affiliated_authors(self):
        return (
            Author.objects.filter(authorships__affiliations__institution=self)
            .annotate(n_works=Count("works"))
            .distinct()
            .order_by("-n_works")
        )


class Affiliation(Attribute):
    model_description = (
        "A sub-unit of an Institution, such as a center, department, library, etc."
    )
    department = models.CharField(
        max_length=500,
        blank=True,
        null=False,
        default="",
        help_text="The name of a department, center, or other subdivision of a larger institution",
    )
    institution = models.ForeignKey(
        Institution,
        on_delete=models.CASCADE,
        related_name="affiliations",
        help_text="The parent institution for this affiliation",
    )

    class Meta:
        unique_together = (("department", "institution"),)
        ordering = ["institution", "department"]

    def __str__(self):
        if self.department == "":
            return f"{self.institution}"
        else:
            return f"{self.department} - {self.institution}"

    def n_authors(self):
        return Author.objects.filter(authorships__affiliations=self).distinct().count()

    def merge(self, target):
        # Don't edit authorships where the target affiliaiton is already # present. It'll get deleted eventually.
        affected_authorships = (
            Authorship.objects.filter(affiliations=self)
            .exclude(affiliations=target)
            .all()
        )

        results = {"update_results": affected_authorships.count()}
        for authorship in affected_authorships:
            authorship.affiliations.add(target)
            authorship.save()

        self.delete()
        return results


class Author(ChangeTrackedModel):
    model_description = "A person who has authored at least one abstract in this database. All attributes of the author are established in the context of a given work, so authors have no inherent/immutable attributes beyond this unique identifier."
    works = models.ManyToManyField(
        Work,
        through="Authorship",
        through_fields=("author", "work"),
        related_name="authors",
    )
    appellations = models.ManyToManyField(
        Appellation,
        through="Authorship",
        through_fields=("author", "appellation"),
        related_name="authors",
    )
    appellations_index = models.CharField(
        max_length=4000, blank=True, null=False, db_index=True
    )

    def __str__(self):
        pname = self.most_recent_appellation
        if pname is not None:
            return f"{self.pk} - {pname}"
        else:
            return f"{self.pk} - anonymous author"

    def save(self, *args, **kwargs):
        all_appellations = (
            Appellation.objects.filter(asserted_by__author=self)
            .values_list("first_name", "last_name")
            .distinct()
        )
        self.appellations_index = " ".join([f"{a[0]} {a[1]}" for a in all_appellations])
        super().save(*args, **kwargs)

    class Meta:
        ordering = ["id"]

    @property
    def all_authorships(self):
        return self.authorships.all()

    @property
    def public_authorships(self):
        return self.authorships.all()

    @property
    def public_works(self):
        return Work.objects.filter(authorships__in=self.public_authorships).distinct()

    @property
    def pref_name(self):
        return f"{self.most_recent_appellation}"

    def most_recent_attributes(self, attr):
        """
        Calculate the most recent attribute by annotating attributes based on
        the latest year of the conference in which they were asserted
        """
        every_attr = attr.objects.filter(
            asserted_by__in=self.public_authorships
        ).distinct()

        if len(every_attr) == 0:
            every_attr = attr.objects.filter(
                asserted_by__in=self.all_authorships
            ).distinct()

        if len(every_attr) == 0:
            return attr.objects.none()

        if len(every_attr) == 1:
            return every_attr

        ranked_dates = every_attr.annotate(
            maxyear=Max("asserted_by__work__conference__year")
        ).order_by("-maxyear")

        most_recent_year = max(ranked_dates.values_list("maxyear", flat=True))

        return ranked_dates.filter(maxyear=most_recent_year)

    def most_recent_attribute(self, attr):
        return self.most_recent_attributes(attr).first()

    @property
    def most_recent_appellation(self):
        return self.most_recent_attribute(Appellation)

    @property
    def most_recent_affiliation(self):
        return self.most_recent_attribute(Affiliation)

    @property
    def most_recent_appellations(self):
        return self.most_recent_attributes(Appellation)

    @property
    def most_recent_affiliations(self):
        return self.most_recent_attributes(Affiliation)

    def get_absolute_url(self):
        return reverse("author_detail", kwargs={"author_id": self.pk})

    def merge(self, target):
        """
        Reassign all of an author's authorships to a target author. This effectivley merges one Author instance into another.
        """
        results = {}

        # Don't double-assign the target author to a work if they already
        # have an uathorship for it
        update_results = (
            Authorship.objects.filter(author=self)
            .exclude(work__authorships__author=target)
            .update(author=target)
        )

        results["update_results"] = update_results

        # Register a redirect
        Redirect.objects.create(
            site=Site.objects.get_current(),
            old_path=self.get_absolute_url(),
            new_path=target.get_absolute_url(),
        )

        # Force-save the target so that its appellation index gets updated
        target.save()

        # Delete self
        deletion_results = self.delete()[1]
        results["deletions"] = deletion_results
        return results


class Authorship(ChangeTrackedModel):
    model_description = "Each authorship describes the relationship of an author to a given work, establishing the authors' attributes as they gave them in the official program where the work was presented."
    author = models.ForeignKey(
        Author,
        on_delete=models.CASCADE,
        related_name="authorships",
        help_text="The author",
    )
    work = models.ForeignKey(
        Work,
        on_delete=models.CASCADE,
        related_name="authorships",
        help_text="The work authored.",
    )
    authorship_order = models.PositiveSmallIntegerField(
        default=1, help_text="Authorship order (1-based indexing)"
    )
    appellation = models.ForeignKey(
        Appellation,
        on_delete=models.CASCADE,
        related_name="asserted_by",
        help_text="The appellation given by the author when they submitted this particular work.",
    )
    affiliations = models.ManyToManyField(
        Affiliation,
        related_name="asserted_by",
        blank=True,
        help_text="The affiliation(s) given by the author when they submitted this particular work.",
    )

    def __str__(self):
        return f"{self.author} - {self.work}"

    @property
    def has_outdated_appellation(self):
        pref_attrs = self.author.most_recent_appellations.values_list("pk", flat=True)
        given_attrs = self.appellation.pk
        return not given_attrs in pref_attrs

    @property
    def has_outdated_affiliations(self):
        pref_attrs = set(
            self.author.most_recent_affiliations.values_list("pk", flat=True)
        )
        given_attrs = set(self.affiliations.values_list("pk", flat=True))
        return not given_attrs.issubset(pref_attrs)

    class Meta:
        unique_together = ("author", "work")
        ordering = ["authorship_order"]


class FileImport(models.Model):
    path = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.path


class FileImportTries(models.Model):
    started = models.DateTimeField(auto_now_add=True)
    file_name = models.ForeignKey(FileImport, on_delete=models.CASCADE)
    conference = models.ForeignKey(Conference, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.file_name} - {self.started}"

    def add_message(self, message, addition_type, warning=False):
        FileImportMessgaes.objects.create(
            attempt=self, message=message, addition_type=addition_type, warning=warning
        )

    def add_create_response(self, create_response):
        self.add_message(
            message=f"Created new {type(create_response)} {create_response}",
            addition_type="new",
        )

    def add_get_or_create_response(self, get_or_create_response):
        actual = get_or_create_response[0]

        if get_or_create_response[1]:
            self.add_message(
                message=f"Created new {type(actual)} {actual}",
                addition_type="new",
            )
        else:
            self.add_message(
                message=f"Matched with {type(actual)} {actual}",
                addition_type="mat",
            )


class FileImportMessgaes(models.Model):
    attempt = models.ForeignKey(FileImportTries, on_delete=models.CASCADE)
    message = models.CharField(max_length=10000)
    addition_type = models.CharField(
        choices=(("mat", "matched existing"), ("new", "newly created"), ("non", "NA")),
        max_length=3,
        default="non",
    )
    warning = models.BooleanField(default=False)

    def __str__(self):
        return self.message
