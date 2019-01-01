import datetime

from django.db import models
from django.db.models import Max
from django.utils import timezone

# Create your models here.


class ConferenceSeries(models.Model):
    title = models.CharField(max_length=100)
    abbreviation = models.CharField(max_length=7, blank=True, unique=True)
    notes = models.TextField(blank=True, null=False, default="")

    @property
    def all_organizers(self):
        return Organizer.objects.filter(conferences_organized__series=self).distinct()

    def __str__(self):
        if self.abbreviation:
            return self.abbreviation
        else:
            return self.title


class Conference(models.Model):
    year = models.IntegerField()
    venue = models.CharField(max_length=100)
    venue_abbreviation = models.CharField(max_length=25, blank=True)
    series = models.ManyToManyField(
        ConferenceSeries,
        through="SeriesMembership",
        through_fields=("conference", "series"),
        related_name="conferences",
    )
    notes = models.TextField(blank=True, null=False, default="")
    url = models.URLField(blank=True)

    class Meta:
        ordering: ["-year"]

    @property
    def public_works(self):
        return self.works.filter(state="ac")

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
        return f"{self.series.first()} {self.year} - {display}"


class Organizer(models.Model):
    name = models.CharField(max_length=100)
    abbreviation = models.CharField(max_length=7, blank=True, unique=True)
    conferences_organized = models.ManyToManyField(
        Conference, related_name="organizers", blank=True
    )
    notes = models.TextField(blank=True)

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
    number = models.PositiveSmallIntegerField(blank=True)

    class Meta:
        unique_together = ("series", "number")
        ordering = ["-conference__year"]

    def __str__(self):
        return f"{self.series.title} - {self.number} - {self.conference}"


class Tag(models.Model):
    title = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.title

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

    class Meta:
        ordering = ["title"]


class Work(models.Model):
    conference = models.ForeignKey(
        Conference, on_delete=models.PROTECT, related_name="works"
    )
    title = models.CharField(max_length=500)
    work_type = models.ForeignKey(
        WorkType, blank=True, null=True, on_delete=models.SET_NULL, related_name="works"
    )
    state = models.CharField(
        max_length=2, choices=(("ac", "accpeted"), ("su", "submission"))
    )
    full_text = models.TextField(max_length=50000, blank=True, null=False, default="")
    full_text_type = models.CharField(
        max_length=3, choices=(("xml", "XML"), ("txt", "plain text")), default="txt"
    )
    keywords = models.ManyToManyField(Keyword, related_name="works", blank=True)
    languages = models.ManyToManyField(Language, related_name="works", blank=True)
    disciplines = models.ManyToManyField(Discipline, related_name="works", blank=True)
    topics = models.ManyToManyField(Topic, related_name="works", blank=True)
    published_version = models.ForeignKey(
        "self",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="unpublished_versions",
        limit_choices_to={"state": "ac"},
    )

    @property
    def display_title(self):
        if len(self.title) > 75:
            return self.title[:75] + "..."
        else:
            return self.title

    def __str__(self):
        return f"({self.state}) {self.display_title}"


class Attribute(models.Model):
    class Meta:
        abstract = True

    @property
    def is_unused(self):
        return self.asserted_by.count() == 0


class Appellation(Attribute):
    first_name = models.CharField(max_length=100, blank=True, null=False, default="")
    last_name = models.CharField(max_length=100, blank=True, null=False, default="")

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Gender(Attribute):
    gender = models.CharField(max_length=100)

    def __str__(self):
        return self.gender


class Country(models.Model):
    name = models.CharField(max_length=500, unique=True)

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

    def __str__(self):
        if not self.city and not self.country:
            return f"{self.name}"
        elif not self.city:
            return f"{self.name} ({self.country})"
        elif not self.country:
            return f"{self.name} ({self.city})"
        else:
            return f"{self.name} ({self.city}, {self.country})"


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

    class Meta:
        ordering = ["appellations__last_name"]

    def __str__(self):
        return f"{self.pk} - {self.pref_name}"

    @property
    def all_authorships(self):
        return self.authorships.all()

    @property
    def public_authorships(self):
        return self.authorships.filter(work__state="ac").distinct()

    @property
    def public_works(self):
        return Work.objects.filter(authorships__in=self.public_authorships).distinct()

    @property
    def pref_name(self):
        return f"{self.pref_first_name} {self.pref_last_name}"

    @property
    def pref_first_name(self):
        return self.most_recent_appellation.first_name

    @property
    def pref_last_name(self):
        return self.most_recent_appellation.last_name

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
    def most_recent_gender(self):
        return self.most_recent_attribute(Gender)

    @property
    def most_recent_affiliation(self):
        return self.most_recent_attribute(Affiliation)

    @property
    def most_recent_appellations(self):
        return self.most_recent_attributes(Appellation)

    @property
    def most_recent_genders(self):
        return self.most_recent_attributes(Gender)

    @property
    def most_recent_affiliations(self):
        return self.most_recent_attributes(Affiliation)


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
    genders = models.ManyToManyField(Gender, related_name="asserted_by", blank=True)

    def __str__(self):
        return f"{self.author} - {self.work}"

    @property
    def has_outdated_(self):
        pref_attrs = self.author.most_recent_appellations.values_list("pk", flat=True)
        given_attrs = self.appellation.values_list("pk", flat=True)
        return not given_attrs in pref_attrs

    @property
    def has_outdated_affiliations(self):
        pref_attrs = set(
            self.author.most_recent_affiliations.values_list("pk", flat=True)
        )
        given_attrs = set(self.affiliations.values_list("pk", flat=True))
        return not given_attrs.issubset(pref_attrs)

    class Meta:
        unique_together = (("work", "authorship_order"), ("author", "work"))
        ordering = ["authorship_order"]

