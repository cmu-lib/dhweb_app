from django.test import TestCase
from django.db.utils import DataError, IntegrityError

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

