import datetime

from django.db import models
from django.utils import timezone

# Create your models here.


class ConferenceSeries(models.Model):
    title = models.CharField(max_length=100)
    notes = models.TextField(blank=True, null=False, default="")

    def __str__(self):
        return str(self.title)


class Conference(models.Model):
    year = models.IntegerField()
    venue = models.CharField(max_length=100)
    series = models.ManyToManyField(
        ConferenceSeries,
        through="SeriesMembership",
        through_fields=("conference", "series"),
        related_name="conferences",
    )
    notes = models.TextField(blank=True, null=False, default="")

    def __str__(self):
        # series.first() is still kludgy - need a nice method to concatenate series names
        return f"{self.series.first()} {self.year} - {self.venue}"


class Organizer(models.Model):
    name = models.CharField(max_length=100)
    conferences_organized = models.ManyToManyField(
        Conference, related_name="organizers", blank=True
    )

    def __str__(self):
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

    def __str__(self):
        return f"{self.series.title} - {self.number} - {self.conference}"


class Keyword(models.Model):
    title = models.CharField(max_length=100, unique=True)
    author_supplied = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class Language(models.Model):
    title = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.title


class Discipline(models.Model):
    title = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.title


class Topic(models.Model):
    title = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.title


class Work(models.Model):
    conference = models.ForeignKey(
        Conference, on_delete=models.PROTECT, related_name="works"
    )
    title = models.CharField(max_length=500)
    submission_type = models.CharField(
        max_length=255, blank=True, null=False, default=""
    )
    state = models.CharField(
        max_length=2, choices=(("ac", "accpeted"), ("su", "submission"))
    )
    full_text = models.TextField(max_length=50000, blank=True, null=False, default="")
    full_text_type = models.CharField(
        max_length=3, choices=(("xml", "XML"), ("txt", "plain text")), default="txt"
    )
    keywords = models.ManyToManyField(Keyword, related_name="versions", blank=True)
    languages = models.ManyToManyField(Language, related_name="versions", blank=True)
    disciplines = models.ManyToManyField(
        Discipline, related_name="versions", blank=True
    )
    topics = models.ManyToManyField(Topic, related_name="versions", blank=True)
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


class Gender(models.Model):
    gender = models.CharField(max_length=100)

    def __str__(self):
        return self.gender


class Institution(models.Model):
    name = models.CharField(max_length=500)
    country = models.CharField(max_length=100, blank=True, null=False, default="")
    city = models.CharField(max_length=100, blank=True, null=False, default="")

    def __str__(self):
        if not self.city and not self.country:
            return f"{self.name}"
        elif not self.city:
            return f"{self.name} ({self.country})"
        elif not self.country:
            return f"{self.name} ({self.city})"
        else:
            return f"{self.name} ({self.city}, {self.country})"


class Department(models.Model):
    name = models.CharField(max_length=500)
    institution = models.ForeignKey(
        Institution, on_delete=models.CASCADE, related_name="departments"
    )

    def __str__(self):
        return f"{self.name} - {self.institution}"


class Author(models.Model):
    works = models.ManyToManyField(
        Work,
        through="Authorship",
        through_fields=("author", "work"),
        related_name="authors",
    )

    @property
    def all_authorships(self):
        return self.authorships.all()

    @property
    def public_authorships(self):
        return self.authorships.filter(work__state="ac").distinct()

    @property
    def genders(self):
        return Gender.objects.filter(asserted_by__in=self.public_authorships)

    @property
    def institutions(self):
        return Institution.objects.filter(asserted_by__in=self.public_authorships)

    @property
    def departments(self):
        return Department.objects.filter(asserted_by__in=self.public_authorships)

    @property
    def all_appellations(self):
        return Appellation.objects.filter(asserted_by__in=self.all_authorships)

    def __str__(self):
        return f"{self.pk} - {self.pref_name}"

    @property
    def pref_name(self):
        return f"{self.pref_first_name} {self.pref_last_name}"

    @property
    def pref_first_name(self):
        return self.most_recent_appellation.first_name

    @property
    def pref_last_name(self):
        return self.most_recent_appellation.last_name

    @property
    def most_recent_appellation(self):
        """
        Calculate the most recent appellation by querying the latest year each
        appellation was asserted, then taking the most recent of those
        appellations.
        """
        every_app = self.all_appellations

        if len(every_app) == 1:
            return every_app[0]

        appellation_latest_years = [a.latest_year for a in every_app]
        return every_app[appellation_latest_years.index(max(appellation_latest_years))]


class Appellation(models.Model):
    first_name = models.CharField(max_length=100, blank=True, null=False, default="")
    last_name = models.CharField(max_length=100, blank=True, null=False, default="")

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def source_works(self):
        return Work.objects.filter(authorships__appellations=self).distinct()

    @property
    def source_conferences(self):
        return Conference.objects.filter(works__in=self.source_works).distinct()

    @property
    def years_asserted(self):
        years = self.source_conferences.values_list("year", flat=True)
        return years

    @property
    def latest_year(self):
        return max(self.years_asserted)

    @property
    def eariest_year(self):
        return min(self.years_asserted)

    @property
    def is_unused(self):
        return self.asserted_by.count() == 0


class Authorship(models.Model):
    author = models.ForeignKey(
        Author, on_delete=models.CASCADE, related_name="authorships"
    )
    work = models.ForeignKey(Work, on_delete=models.CASCADE, related_name="authorships")
    authorship_order = models.PositiveSmallIntegerField(default=1)
    departments = models.ManyToManyField(
        Department, related_name="asserted_by", blank=True
    )
    appellations = models.ManyToManyField(Appellation, related_name="asserted_by")
    institutions = models.ManyToManyField(
        Institution, related_name="asserted_by", blank=True
    )
    genders = models.ManyToManyField(Gender, related_name="asserted_by", blank=True)

    def __str__(self):
        return f"{self.author} - {self.work}"

    class Meta:
        unique_together = (("work", "authorship_order"), ("author", "work"))

