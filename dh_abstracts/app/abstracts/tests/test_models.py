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
from lxml.etree import XMLSyntaxError


class ConferenceXMLImportTest(TestCase):
    fixtures = ["test.json"]

    def test_load_file(self):
        conference = Conference.objects.first()

        conference.import_xml_file("/vol/static_files/files/abstract_tei.xml")
        self.assertTrue(
            Work.objects.filter(title__icontains="Archivos digitales").exists()
        )
        created_work = Work.objects.filter(
            title__icontains="Archivos digitales"
        ).first()
        self.assertEqual(created_work.conference, conference)
        self.assertIn(Language.objects.get(code="es"), created_work.languages.all())
        self.assertTrue(Appellation.objects.filter(first_name="Maria Jose").exists())
        self.assertEqual(created_work.authorships.count(), 2)
        self.assertTrue(
            Institution.objects.filter(name="Universidad de los Andes").exists()
        )
        self.assertTrue(
            Institution.objects.filter(name="Fundación Histórica Neogranadina").exists()
        )
        self.assertTrue(Institution.objects.filter(name="Harvard University").exists())
        self.assertTrue(
            Affiliation.objects.filter(department="Departamento de Historia").exists()
        )
        self.assertTrue(
            Affiliation.objects.filter(
                department="Berkman Klein Center for Internet and Society"
            ).exists()
        )

    def test_bad_file(self):
        conference = Conference.objects.first()

        self.assertRaises(
            XMLSyntaxError,
            conference.import_xml_file,
            filepath="/vol/static_files/files/bad_tei.xml",
        )


class ConferenceXMLDirectoryImportTest(TestCase):
    fixtures = ["test.json"]

    def test_load_directory(self):
        conference = Conference.objects.first()

        conference.import_xml_directory("/vol/static_files/files")
        self.assertTrue(
            Work.objects.filter(title__icontains="Archivos digitales").exists()
        )
        self.assertTrue(
            Work.objects.filter(
                title__icontains="The Index of Digital Humanities Conferences"
            ).exists()
        )
