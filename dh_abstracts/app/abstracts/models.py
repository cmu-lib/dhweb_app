import datetime

from django.db import models
from django.db.models import Max, Count
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.urls import reverse
from django.contrib.sites.models import Site
from django.contrib.redirects.models import Redirect
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVector, SearchVectorField
from django.contrib.auth.models import User

# Create your models here.


class TextIndexedModel(models.Model):
    search_text = SearchVectorField(null=True, editable=False)

    class Meta:
        abstract = True
        indexes = [GinIndex(fields=["search_text"])]


class ConferenceSeries(models.Model):
    title = models.CharField(max_length=200, unique=True)
    abbreviation = models.CharField(max_length=30, unique=True)
    notes = models.TextField(blank=True, null=False, default="")

    @property
    def all_organizers(self):
        return Organizer.objects.filter(conferences_organized__series=self).distinct()

    def __str__(self):
        if self.abbreviation != "":
            return self.abbreviation
        else:
            return self.title

    def get_absolute_url(self):
        return reverse("series_edit", kwargs={"pk": self.pk})


class Conference(models.Model):
    year = models.IntegerField()
    venue = models.CharField(max_length=200)
    venue_abbreviation = models.CharField(max_length=50, blank=True)
    series = models.ManyToManyField(
        ConferenceSeries,
        through="SeriesMembership",
        through_fields=("conference", "series"),
        related_name="conferences",
        blank=True,
    )
    notes = models.TextField(blank=True, null=False, default="")
    url = models.URLField(blank=True)

    class Meta:
        ordering = ["-year"]
        unique_together = ["year", "venue"]

    @property
    def public_works(self):
        return self.works.all()

    def public_authors(self):
        return (
            Author.objects.filter(authorships__work__in=self.public_works)
            .distinct()
            .count()
        )

    def __str__(self):
        if self.venue_abbreviation:
            display = self.venue_abbreviation
        else:
            display = self.venue
        # series.first() is still kludgy - need a nice method to concatenate series names
        if self.series.exists():
            return f"{self.series.first()} {self.year} - {display}"
        else:
            return f"{self.year} - {display}"

    def get_absolute_url(self):
        return reverse("conference_edit", kwargs={"pk": self.pk})


class Organizer(models.Model):
    name = models.CharField(max_length=200, unique=True)
    abbreviation = models.CharField(max_length=7, unique=True)
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


class SeriesMembership(models.Model):
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
    author_supplied = models.BooleanField(default=True)


class Language(Tag):
    pass


class Discipline(Tag):
    pass


class Topic(Tag):
    pass


class WorkType(models.Model):
    title = models.CharField(max_length=100, unique=True)

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
    title = models.CharField(max_length=100, unique=True)
    full_text = models.TextField(max_length=100_000)
    display_abbreviation = models.CharField(max_length=50, unique=True)
    url = models.URLField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.title


class Work(TextIndexedModel):
    FT_TYPE = (("", "-----------"), ("xml", "XML"), ("txt", "plain text"))

    conference = models.ForeignKey(
        Conference, on_delete=models.CASCADE, related_name="works"
    )
    title = models.CharField(max_length=500)
    work_type = models.ForeignKey(
        WorkType, blank=True, null=True, on_delete=models.SET_NULL, related_name="works"
    )
    full_text = models.TextField(max_length=50000, blank=True, null=False, default="")
    full_text_type = models.CharField(
        max_length=3, choices=FT_TYPE, blank=True, null=False, default=""
    )
    keywords = models.ManyToManyField(Keyword, related_name="works", blank=True)
    languages = models.ManyToManyField(Language, related_name="works", blank=True)
    disciplines = models.ManyToManyField(Discipline, related_name="works", blank=True)
    topics = models.ManyToManyField(Topic, related_name="works", blank=True)
    full_text_license = models.ForeignKey(
        License, blank=True, null=True, on_delete=models.SET_NULL
    )
    url = models.URLField(blank=True, null=False, max_length=500)
    last_updated = models.DateTimeField(auto_now=True, db_index=True)
    user_last_updated = models.ForeignKey(
        User, null=True, on_delete=models.SET_NULL, related_name="records_last_updated"
    )

    def get_absolute_url(self):
        return reverse("work_detail", kwargs={"pk": self.pk})

    @property
    def display_title(self):
        if len(self.title) > 75:
            return self.title[:75] + "..."
        else:
            return self.title

    def __str__(self):
        return self.display_title

    class Meta(TextIndexedModel.Meta):
        ordering = ["title"]


class Attribute(models.Model):
    class Meta:
        abstract = True

    @property
    def is_unused(self):
        return self.asserted_by.count() == 0


class Appellation(Attribute):
    first_name = models.CharField(
        max_length=100, blank=True, null=False, default="", db_index=True
    )
    last_name = models.CharField(
        max_length=100, blank=True, null=False, default="", db_index=True
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
    tgn_id = models.URLField(max_length=100, unique=True)
    pref_name = models.CharField(max_length=300, db_index=True)

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


class Institution(models.Model):
    name = models.CharField(max_length=500)
    city = models.CharField(max_length=100, blank=True, null=False, default="")
    country = models.ForeignKey(
        Country,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="institutions",
    )

    class Meta:
        unique_together = (("name", "country"),)
        ordering = ["name"]

    def __str__(self):
        if not self.city and not self.country:
            return f"{self.name}"
        elif not self.city:
            return f"{self.name} ({self.country})"
        elif not self.country:
            return f"{self.name} ({self.city})"
        else:
            return f"{self.name} ({self.city}, {self.country})"

    def merge(self, target):
        affected_affiliations = Affiliation.objects.filter(institution=self)

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
    department = models.CharField(max_length=500, blank=True, null=False, default="")
    institution = models.ForeignKey(
        Institution, on_delete=models.CASCADE, related_name="affiliations"
    )

    class Meta:
        unique_together = (("department", "institution"),)
        ordering = ["institution", "department"]

    def __str__(self):
        if self.department == "":
            return f"(no department) {self.institution}"
        else:
            return f"{self.department} - {self.institution}"

    def n_authors(self):
        return Author.objects.filter(authorships__affiliations=self).distinct().count()

    def n_works(self):
        return Work.objects.filter(authorships__affiliations=self).distinct().count()

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


class Author(models.Model):
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
        the latest year of th eoncference in which they were asserted
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

        # Delete self
        deletion_results = self.delete()[1]
        results["deletions"] = deletion_results
        return results


class Authorship(models.Model):
    author = models.ForeignKey(
        Author, on_delete=models.CASCADE, related_name="authorships"
    )
    work = models.ForeignKey(Work, on_delete=models.CASCADE, related_name="authorships")
    authorship_order = models.PositiveSmallIntegerField(default=1)
    appellation = models.ForeignKey(
        Appellation, on_delete=models.CASCADE, related_name="asserted_by"
    )
    affiliations = models.ManyToManyField(
        Affiliation, related_name="asserted_by", blank=True
    )
    last_updated = models.DateTimeField(auto_now=True, db_index=True)
    user_last_updated = models.ForeignKey(
        User,
        null=True,
        on_delete=models.SET_NULL,
        related_name="authorships_last_updated",
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


class FileImportMessgaes(models.Model):
    attempt = models.ForeignKey(FileImportTries, on_delete=models.CASCADE)
    message = models.CharField(max_length=1000)
    addition_type = models.CharField(
        choices=(("mat", "matched existing"), ("new", "newly created"), ("non", "NA")),
        max_length=3,
        default="non",
    )
    warning = models.BooleanField(default=False)

    def __str__(self):
        return self.message