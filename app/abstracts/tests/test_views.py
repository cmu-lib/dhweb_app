from django.test import TestCase
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


class EmptyViewTest(TestCase):
    """
    Test pages when the database is empty
    """

    def test_blank_db(self):
        """
        If no series exist, display appropriate message
        """

        home_response = self.client.get(reverse("home_view"))
        self.assertEqual(home_response.status_code, 200)

        work_response = self.client.get(reverse("work_list"))
        self.assertEqual(work_response.status_code, 200)

        author_response = self.client.get(reverse("author_list"))
        self.assertEqual(author_response.status_code, 200)

        conference_response = self.client.get(reverse("conference_list"))
        self.assertEqual(conference_response.status_code, 200)

