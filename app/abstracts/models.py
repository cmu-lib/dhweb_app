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
        Conference, related_name="organizers"
    )

    def __str__(self):
        return str(self.name)


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


class Work(models.Model):
    conference = models.ForeignKey(
        Conference, on_delete=models.CASCADE, related_name="works"
    )

    def __str__(self):
        return f"{self.pk} - {self.pref_title}"

    @property
    def pref_title(self):
        return self.versions.last().title

    def authors(self):
        return Author.objects.filter(versions__work=self).distinct()

    @property
    def submissions(self):
        return self.versions.distinct()


class Keyword(models.Model):
    title = models.CharField(max_length=100, unique=True)
    author_supplied = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    def works(self):
        return Work.objects.filter(versions__keywords=self).distinct()


class Language(models.Model):
    title = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.title

    def works(self):
        return Work.objects.filter(versions__languages=self).distinct()


class Discipline(models.Model):
    title = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.title

    def works(self):
        return Work.objects.filter(versions__disciplines=self).distinct()


class Topic(models.Model):
    title = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.title

    def works(self):
        return Work.objects.filter(versions__topics=self).distinct()


class Version(models.Model):
    work = models.ForeignKey(Work, on_delete=models.CASCADE, related_name="versions")
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
        return f"{self.name} - {self.institution.name}"


class Appellation(models.Model):
    first_name = models.CharField(max_length=100, blank=True, null=False, default="")
    last_name = models.CharField(max_length=100, blank=True, null=False, default="")
    author = models.ForeignKey(
        "Author", on_delete=models.CASCADE, related_name="appellations"
    )
    asserted_by = models.ManyToManyField(Version, related_name="appellation_assertions")

    class Meta:
        unique_together = ("author", "first_name", "last_name")

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def source_works(self):
        return Work.objects.filter(versions__appellation_assertions=self).distinct()

    def add_source_work(self, work):
        """
        At a low level, attributes are asserted by Versions. However, in most cases when adding new assertions, we'll want to simply supply a single Work and then have the assertions made by all of the Work's constituent Versions.
        """
        assoc_versions = work.versions.all()
        self.asserted_by.set(assoc_versions)

    def years_asserted(self):
        years = (
            Conference.objects.filter(works__versions__appellation_assertions=self)
            .distinct()
            .values_list("year", flat=True)
        )
        return years

    def latest_year(self):
        return max(self.years_asserted())

    def eariest_year(self):
        return min(self.years_asserted())


class Author(models.Model):
    versions = models.ManyToManyField(
        Version,
        through="Authorship",
        through_fields=("author", "version"),
        related_name="authors",
    )
    genders = models.ManyToManyField(
        Gender,
        through="GenderAssertion",
        through_fields=("author", "gender"),
        related_name="members",
    )
    institutions = models.ManyToManyField(
        Institution,
        through="InstitutionAssertion",
        through_fields=("author", "institution"),
        related_name="members",
    )
    departments = models.ManyToManyField(
        Department,
        through="DepartmentAssertion",
        through_fields=("author", "department"),
        related_name="members",
    )

    def __str__(self):
        return f"{self.pk} - {self.pref_name}"

    @property
    def pref_name(self):
        return f"{self.pref_first_name} {self.pref_last_name}"

    @property
    def pref_first_name(self):
        return self.most_recent_appellation().first_name

    @property
    def pref_last_name(self):
        return self.most_recent_appellation().last_name

    def most_recent_appellation(self):
        """
        Calculate the most recent appellation by querying the latest year each
        appellation was asserted, then taking the most recent of those
        appellations.
        """
        all_appellations = self.appellations.all()

        if len(all_appellations) == 1:
            return all_appellations[0]

        appellation_latest_years = [a.latest_year() for a in all_appellations]
        return all_appellations[
            appellation_latest_years.index(max(appellation_latest_years))
        ]

    def works(self):
        return Work.objects.filter(versions__authors=self).distinct()

    class Meta:
        ordering: ["pref_last_name"]


class Authorship(models.Model):
    author = models.ForeignKey(
        Author, on_delete=models.CASCADE, related_name="authorships"
    )
    version = models.ForeignKey(
        Version, on_delete=models.CASCADE, related_name="authorships"
    )
    authorship_order = models.PositiveSmallIntegerField(default=1)

    def __str__(self):
        return f"{self.version} - {self.author} ({self.authorship_order})"

    class Meta:
        unique_together = (("author", "version", "authorship_order"),)


class DepartmentAssertion(models.Model):
    author = models.ForeignKey(
        Author, on_delete=models.CASCADE, related_name="department_memberships"
    )
    asserted_by = models.ManyToManyField(Version, related_name="department_assertions")
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, related_name="assertions"
    )

    class Meta:
        unique_together = ("author", "department")

    def __str__(self):
        return f"{self.department} - {self.author}"

    def source_works(self):
        return Work.objects.filter(versions__department_assertions=self).distinct()

    def add_source_work(self, work):
        """
        At a low level, attributes are asserted by Versions. However, in most cases when adding new assertions, we'll want to simply supply a single Work and then have the assertions made by all of the Work's constituent Versions.
        """
        assoc_versions = work.versions.all()
        self.asserted_by.set(assoc_versions)


class InstitutionAssertion(models.Model):
    author = models.ForeignKey(
        Author, on_delete=models.CASCADE, related_name="institution_memberships"
    )
    institution = models.ForeignKey(
        Institution, on_delete=models.CASCADE, related_name="assertions"
    )
    asserted_by = models.ManyToManyField(Version, related_name="institution_assertions")

    class Meta:
        unique_together = ("author", "institution")

    def __str__(self):
        return f"{self.institution} - {self.author}"

    def source_works(self):
        return Work.objects.filter(versions__institution_assertions=self).distinct()

    def add_source_work(self, work):
        """
        At a low level, attributes are asserted by Versions. However, in most cases when adding new assertions, we'll want to simply supply a single Work and then have the assertions made by all of the Work's constituent Versions.
        """
        assoc_versions = work.versions.all()
        self.asserted_by.set(assoc_versions)


class GenderAssertion(models.Model):
    author = models.ForeignKey(
        Author, on_delete=models.CASCADE, related_name="gender_memberships"
    )
    gender = models.ForeignKey(
        Gender, on_delete=models.CASCADE, related_name="gender_authors"
    )
    asserted_by = models.ManyToManyField(Version, related_name="gender_assertions")

    class Meta:
        unique_together = ("author", "gender")

    def __str__(self):
        return f"{self.gender} - {self.author}"

    def source_works(self):
        return Work.objects.filter(versions__gender_assertions=self).distinct()

    def add_source_work(self, work):
        """
        At a low level, attributes are asserted by Versions. However, in most cases when adding new assertions, we'll want to simply supply a single Work and then have the assertions made by all of the Work's constituent Versions.
        """
        assoc_versions = work.versions.all()
        self.asserted_by.set(assoc_versions)
