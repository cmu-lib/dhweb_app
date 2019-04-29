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


class EmptyListViewTest(TestCase):
    """
    Test pages when the database is empty
    """

    def test_home_blank(self):
        home_response = self.client.get(reverse("home_view"))
        self.assertEqual(home_response.status_code, 200)

    def test_work_blank(self):
        work_response = self.client.get(reverse("work_list"))
        self.assertEqual(work_response.status_code, 200)

    def test_author_blank(self):
        author_response = self.client.get(reverse("author_list"))
        self.assertEqual(author_response.status_code, 200)

    def test_conference_blank(self):
        conference_response = self.client.get(reverse("conference_list"))
        self.assertEqual(conference_response.status_code, 200)


class AuthorListViewTest(TestCase):
    """
    Test Author list page
    """

    fixtures = ["test.json"]

    def test_author_list_render(self):
        author_list_response = self.client.get(reverse("author_list"))
        self.assertEqual(author_list_response.status_code, 200)

    def test_author_list_length(self):
        author_list_response = self.client.get(reverse("author_list"))
        self.assertEqual(
            len(
                set(
                    author_list_response.context["author_list"].values_list(
                        "pk", flat=True
                    )
                )
            ),
            2,
        )

    def test_author_list_query_filtered_count(self):
        author_list_response = self.client.get(reverse("author_list"))
        self.assertEqual(author_list_response.context["filtered_authors_count"], 2)

    def test_author_list_query_total_count(self):
        author_list_response = self.client.get(reverse("author_list"))
        self.assertEqual(author_list_response.context["available_authors_count"], 2)


class AuthorDetailViewTest(TestCase):
    """
    Test Author detail page
    """

    fixtures = ["test.json"]

    def test_author_detail(self):
        author_detail_response = self.client.get(
            reverse("author_detail", kwargs={"pk": 1})
        )
        self.assertEqual(author_detail_response.status_code, 200)

    def test_author_detail_series(self):
        author_detail_response = self.client.get(
            reverse("author_detail", kwargs={"pk": 1})
        )
        self.assertEqual(len(author_detail_response.context["split_works"]), 1)

    def test_author_detail_works(self):
        author_detail_response = self.client.get(
            reverse("author_detail", kwargs={"pk": 1})
        )
        self.assertEqual(len(set(author_detail_response.context["split_works"][0])), 2)

    def test_author_detail_appellations(self):
        author_detail_response = self.client.get(
            reverse("author_detail", kwargs={"pk": 1})
        )
        self.assertEqual(
            len(author_detail_response.context["appellation_assertions"]), 2
        )

    def test_author_detail_affiliations(self):
        author_detail_response = self.client.get(
            reverse("author_detail", kwargs={"pk": 1})
        )
        self.assertEqual(
            len(author_detail_response.context["affiliation_assertions"]), 2
        )
