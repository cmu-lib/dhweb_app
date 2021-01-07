from django.test import TestCase

from abstracts.models import (
    Organizer,
    ConferenceSeries,
    Conference,
    SeriesMembership,
    Work,
    Institution,
    Appellation,
    Author,
    Authorship,
    Keyword,
    Language,
    Topic,
    Affiliation,
    Country,
    CountryLabel,
    WorkType,
    FileImport,
    FileImportMessgaes,
    FileImportTries,
    License,
)


class ConferenceXMLImportTest(TestCase):
    fixtures = ["test.json"]

    def test_load_file(self):
        conference = Conference.objects.first()

        conference.import_xml_file("/vol/static_files/files/abstract_tei.xml")
        self.assertTrue(
            Work.objects.filter(title__icontains="Archivos digitales").exists()
        )
