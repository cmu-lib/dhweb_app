from django.test import TestCase
from django.db.utils import DataError, IntegrityError
from django.urls import reverse

from abstracts.models import (
    Organizer,
    ConferenceSeries,
    Conference,
    SeriesMembership,
    Work,
    Institution,
    Gender,
    Appellation,
    Author,
    Authorship,
    Keyword,
    Language,
    Topic,
    Discipline,
    Affiliation,
    Country,
    CountryLabel,
    WorkType,
    FileImport,
    FileImportMessgaes,
    FileImportTries,
    License,
)


class OrganizerModelTest(TestCase):
    """
    Test the Organizer model definition
    """

    @classmethod
    def setUpTestData(self):
        Organizer.objects.create(name="Tesco", abbreviation="TeCo")

    def test_org_str_abbreviation(self):
        org_with_abbreviation = Organizer.objects.get(name="Tesco")
        self.assertEquals("TeCo", str(org_with_abbreviation))

    def test_abbreviation_limit(self):
        with self.assertRaises(DataError):
            Organizer.objects.create(
                name="Foo", abbreviation="Too long to be an abbreviation"
            )

    def test_unique_name(self):
        with self.assertRaises(IntegrityError):
            Organizer.objects.create(name="Tesco", abbreviation="Buzz")

    def test_unique_abbreviation(self):
        with self.assertRaises(IntegrityError):
            Organizer.objects.create(name="Bar", abbreviation="TeCo")


class ConferenceSeriesModelTest(TestCase):
    """
    Test the ConferenceSeries model definition
    """

    @classmethod
    def setUpTestData(self):
        ConferenceSeries.objects.create(
            title="Tesco Conference Series", abbreviation="TECOS"
        )

    def test_series_str(self):
        tecos = ConferenceSeries.objects.get(abbreviation="TECOS")
        self.assertEquals("TECOS", str(tecos))

    def test_abbreviation_limit(self):
        with self.assertRaises(DataError):
            ConferenceSeries.objects.create(
                title="Foo", abbreviation="Too long to be an abbreviation"
            )

    def test_unique_title(self):
        with self.assertRaises(IntegrityError):
            ConferenceSeries.objects.create(
                title="Tesco Conference Series", abbreviation="Buzz"
            )

    def test_unique_abbreviation(self):
        with self.assertRaises(IntegrityError):
            ConferenceSeries.objects.create(title="Bar", abbreviation="TECOS")


class SeriesMembershipModelTest(TestCase):
    """
    Test the Conference model definition
    """

    @classmethod
    def setUpTestData(self):
        cs = ConferenceSeries.objects.create(
            title="Tesco Conference Series", abbreviation="TECOS"
        )
        org = Organizer.objects.create(name="Tesco", abbreviation="TeCo")
        Conference.objects.create(
            year=2000, venue="New York", venue_abbreviation="NYC", series=cs
        )


class ConferenceModelTest(TestCase):
    """
    Test the Conference model definition
    """

    @classmethod
    def setUpTestData(self):
        cs = ConferenceSeries.objects.create(
            title="Tesco Conference Series", abbreviation="TECOS"
        )
        org = Organizer.objects.create(name="Tesco", abbreviation="TeCo")
        abbr_con = Conference.objects.create(
            year=2000, venue="New York", venue_abbreviation="NYC"
        )
        no_abbr_con = Conference.objects.create(year=2001, venue="Oregon")
        SeriesMembership.objects.create(series=cs, conference=abbr_con, number=1)
        SeriesMembership.objects.create(series=cs, conference=no_abbr_con, number=2)

    def test_conference_str_abbr(self):
        abbr_con = Conference.objects.get(pk=1)
        self.assertEquals(
            f"{abbr_con.series.first()} {abbr_con.year} - {abbr_con.venue_abbreviation}",
            str(abbr_con),
        )

    def test_conference_str_no_abbr(self):
        no_abbr_con = Conference.objects.get(pk=2)
        self.assertEquals(
            f"{no_abbr_con.series.first()} {no_abbr_con.year} - {no_abbr_con.venue}",
            str(no_abbr_con),
        )

    def test_conference_default_ordering(self):
        """
        Conferences are returned in reverse chronological order
        """
        cons = Conference.objects.all()
        self.assertGreater(cons.first().year, cons.last().year)


class AuthorModelTest(TestCase):
    """
    Test the Author model definition
    """

    @classmethod
    def setUpTestData(self):
        Author.objects.create()

    def test_reverse_url(self):
        a1 = Author.objects.get(pk=1)
        self.assertEqual(
            a1.get_absolute_url(), reverse("author_detail", kwargs={"author_id": 1})
        )

