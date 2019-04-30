from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
import json

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

from abstracts.forms import WorkFilter


def is_list_unique(x):
    return len(x) == len(set(x))


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

    def test_render(self):
        author_list_response = self.client.get(reverse("author_list"))
        self.assertEqual(author_list_response.status_code, 200)

    def test_query_filtered_count(self):
        author_list_response = self.client.get(reverse("author_list"))
        self.assertEqual(
            author_list_response.context["filtered_authors_count"],
            len(author_list_response.context["author_list"]),
        )

    def test_query_total_count(self):
        author_list_response = self.client.get(reverse("author_list"))
        self.assertIsInstance(
            author_list_response.context["available_authors_count"], int
        )

    def test_unique(self):
        author_list_response = self.client.get(reverse("author_list"))
        self.assertTrue(is_list_unique(author_list_response.context["author_list"]))

    def test_all_accepted(self):
        author_list_response = self.client.get(reverse("author_list"))
        for author in author_list_response.context["author_list"]:
            self.assertGreaterEqual(author.works.filter(state="ac").count(), 1)


class AuthorDetailViewTest(TestCase):
    """
    Test Author detail page
    """

    fixtures = ["test.json"]

    def test_render(self):
        author_detail_response = self.client.get(
            reverse("author_detail", kwargs={"pk": 1})
        )
        self.assertEqual(author_detail_response.status_code, 200)

    def test_works_unqiue_in_series(self):
        author_detail_response = self.client.get(
            reverse("author_detail", kwargs={"pk": 1})
        )
        for series in author_detail_response.context["split_works"]:
            self.assertTrue(is_list_unique(series["works"]))

    def test_appellations_unique(self):
        author_detail_response = self.client.get(
            reverse("author_detail", kwargs={"pk": 1})
        )
        self.assertTrue(
            is_list_unique(
                [
                    d["appellation"]
                    for d in author_detail_response.context["appellation_assertions"]
                ]
            )
        )

    def test_affiliations_unique_institutions(self):
        author_detail_response = self.client.get(
            reverse("author_detail", kwargs={"pk": 1})
        )
        self.assertTrue(
            is_list_unique(
                [
                    d["institution"]
                    for d in author_detail_response.context["affiliation_assertions"]
                ]
            )
        )

    def test_affiliations_each_has_value(self):
        author_detail_response = self.client.get(
            reverse("author_detail", kwargs={"pk": 1})
        )
        for assertion in author_detail_response.context["affiliation_assertions"]:
            self.assertGreaterEqual(len(assertion["works"]), 1)
            self.assertTrue(is_list_unique(assertion["works"]))

    def test_unaccepted_author(self):
        """
        Authors with only submitted papers should not have pages
        """
        unaccepted_author_detail_response = self.client.get(
            reverse("author_detail", kwargs={"pk": 3})
        )
        self.assertEqual(
            len(unaccepted_author_detail_response.context["split_works"]), 0
        )


class WorkListViewTest(TestCase):
    """
    Test Work list page
    """

    fixtures = ["test.json"]

    def test_render(self):
        author_list_response = self.client.get(reverse("author_list"))
        self.assertEqual(author_list_response.status_code, 200)

    def test_query_filtered_count(self):
        work_list_response = self.client.get(reverse("work_list"))
        self.assertEqual(
            work_list_response.context["filtered_works_count"],
            len(work_list_response.context["work_list"]),
        )

    def test_query_total_count(self):
        work_list_response = self.client.get(reverse("work_list"))
        self.assertIsInstance(work_list_response.context["available_works_count"], int)

    def test_form(self):
        work_list_response = self.client.get(reverse("work_list"))
        self.assertIsInstance(
            work_list_response.context["work_filter_form"], WorkFilter
        )

    def test_unique_set(self):
        work_list_response = self.client.get(reverse("work_list"))
        self.assertEqual(
            len(set(work_list_response.context["work_list"])),
            work_list_response.context["filtered_works_count"],
        )

    def test_only_accepted(self):
        work_list_response = self.client.get(reverse("work_list"))
        for work in work_list_response.context["work_list"]:
            self.assertEqual(work.state, "ac")


class WorkDetailViewTest(TestCase):
    """
    Test Work detail view
    """

    fixtures = ["test.json"]

    def test_render(self):
        work_detail_response = self.client.get(reverse("work_detail", kwargs={"pk": 1}))
        self.assertEqual(work_detail_response.status_code, 200)

    def test_is_work(self):
        work_detail_response = self.client.get(reverse("work_detail", kwargs={"pk": 1}))
        self.assertIsInstance(work_detail_response.context["work"], Work)

    def test_authorships_unique(self):
        work_detail_response = self.client.get(reverse("work_detail", kwargs={"pk": 1}))
        self.assertTrue(is_list_unique(work_detail_response.context["authorships"]))


class ConferenceListViewTest(TestCase):
    """
    Test Conference list view
    """

    fixtures = ["test.json"]

    def test_render(self):
        conference_list_response = self.client.get(reverse("conference_list"))
        self.assertEqual(conference_list_response.status_code, 200)

    def test_hide_unaccepted_conferences(self):
        conference_list_response = self.client.get(reverse("conference_list"))
        self.assertNotIn(
            ConferenceSeries.objects.get(pk=2),
            conference_list_response.context["conference_list"],
        )


class InstitutionAutocompleteTest(TestCase):
    fixtures = ["test.json"]

    def test_render(self):
        institution_ac_response = self.client.get(reverse("institution-autocomplete"))
        self.assertEqual(institution_ac_response.status_code, 200)


class TopicAutocompleteTest(TestCase):
    fixtures = ["test.json"]

    def test_render(self):
        topic_ac_response = self.client.get(reverse("topic-autocomplete"))
        self.assertEqual(topic_ac_response.status_code, 200)


class KeywordAutocompleteTest(TestCase):
    fixtures = ["test.json"]

    def test_render(self):
        keyword_ac_response = self.client.get(reverse("keyword-autocomplete"))
        self.assertEqual(keyword_ac_response.status_code, 200)


class CountryAutocompleteTest(TestCase):
    fixtures = ["test.json"]

    def test_render(self):
        country_ac_response = self.client.get(reverse("country-autocomplete"))
        self.assertEqual(country_ac_response.status_code, 200)


class AuthorAutocompleteTest(TestCase):
    fixtures = ["test.json"]

    def test_render(self):
        author_ac_response = self.client.get(reverse("author-autocomplete"))
        self.assertEqual(author_ac_response.status_code, 200)


class UnrestrictedAppellationAutocompleteTest(TestCase):
    fixtures = ["test.json"]

    def test_no_public(self):
        appellation_ac_response = self.client.get(
            reverse("unrestricted-appellation-autocomplete")
        )
        self.assertEqual(appellation_ac_response.status_code, 403)

    def test_render(self):
        self.client.login(username="root", password="dh-abstracts")
        auth_appellation_ac_response = self.client.get(
            reverse("unrestricted-appellation-autocomplete")
        )
        self.assertEqual(auth_appellation_ac_response.status_code, 200)

    def test_unqiue(self):
        self.client.login(username="root", password="dh-abstracts")
        auth_appellation_ac_response = self.client.get(
            reverse("unrestricted-appellation-autocomplete")
        )
        result_vals = [
            res["id"]
            for res in json.loads(auth_appellation_ac_response.content)["results"]
        ]
        self.assertTrue(is_list_unique(result_vals))


class UnrestrictedWorkAutocompleteTest(TestCase):
    fixtures = ["test.json"]

    def test_no_public(self):
        work_ac_response = self.client.get(reverse("unrestricted-work-autocomplete"))
        self.assertEqual(work_ac_response.status_code, 403)

    def test_render(self):
        self.client.login(username="root", password="dh-abstracts")
        auth_work_ac_response = self.client.get(
            reverse("unrestricted-work-autocomplete")
        )
        self.assertEqual(auth_work_ac_response.status_code, 200)

    def test_unqiue(self):
        self.client.login(username="root", password="dh-abstracts")
        auth_work_ac_response = self.client.get(
            reverse("unrestricted-work-autocomplete")
        )
        result_vals = [
            res["id"] for res in json.loads(auth_work_ac_response.content)["results"]
        ]
        self.assertTrue(is_list_unique(result_vals))


class UnrestrictedKeywordAutocompleteTest(TestCase):
    fixtures = ["test.json"]

    def test_no_public(self):
        keyword_ac_response = self.client.get(
            reverse("unrestricted-keyword-autocomplete")
        )
        self.assertEqual(keyword_ac_response.status_code, 403)

    def test_render(self):
        self.client.login(username="root", password="dh-abstracts")
        auth_keyword_ac_response = self.client.get(
            reverse("unrestricted-keyword-autocomplete")
        )
        self.assertEqual(auth_keyword_ac_response.status_code, 200)

    def test_unqiue(self):
        self.client.login(username="root", password="dh-abstracts")
        auth_keyword_ac_response = self.client.get(
            reverse("unrestricted-keyword-autocomplete")
        )
        result_vals = [
            res["id"] for res in json.loads(auth_keyword_ac_response.content)["results"]
        ]
        self.assertTrue(is_list_unique(result_vals))


class UnrestrictedAuthorAutocompleteTest(TestCase):
    fixtures = ["test.json"]

    def test_no_public(self):
        author_ac_response = self.client.get(
            reverse("unrestricted-author-autocomplete")
        )
        self.assertEqual(author_ac_response.status_code, 403)

    def test_render(self):
        self.client.login(username="root", password="dh-abstracts")
        auth_author_ac_response = self.client.get(
            reverse("unrestricted-author-autocomplete")
        )
        self.assertEqual(auth_author_ac_response.status_code, 200)

    def test_unqiue(self):
        self.client.login(username="root", password="dh-abstracts")
        auth_author_ac_response = self.client.get(
            reverse("unrestricted-author-autocomplete")
        )
        result_vals = [
            res["id"] for res in json.loads(auth_author_ac_response.content)["results"]
        ]
        self.assertTrue(is_list_unique(result_vals))


class UnrestrictedAffiliationAutocompleteTest(TestCase):
    fixtures = ["test.json"]

    def test_no_public(self):
        affiliation_ac_response = self.client.get(
            reverse("unrestricted-affiliation-autocomplete")
        )
        self.assertEqual(affiliation_ac_response.status_code, 403)

    def test_render(self):
        self.client.login(username="root", password="dh-abstracts")
        auth_affiliation_ac_response = self.client.get(
            reverse("unrestricted-affiliation-autocomplete")
        )
        self.assertEqual(auth_affiliation_ac_response.status_code, 200)

    def test_unqiue(self):
        self.client.login(username="root", password="dh-abstracts")
        auth_affiliation_ac_response = self.client.get(
            reverse("unrestricted-affiliation-autocomplete")
        )
        result_vals = [
            res["id"]
            for res in json.loads(auth_affiliation_ac_response.content)["results"]
        ]
        self.assertTrue(is_list_unique(result_vals))


class UnrestrictedInstitutionAutocompleteTest(TestCase):
    fixtures = ["test.json"]

    def test_no_public(self):
        institution_ac_response = self.client.get(
            reverse("unrestricted-institution-autocomplete")
        )
        self.assertEqual(institution_ac_response.status_code, 403)

    def test_render(self):
        self.client.login(username="root", password="dh-abstracts")
        auth_institution_ac_response = self.client.get(
            reverse("unrestricted-institution-autocomplete")
        )
        self.assertEqual(auth_institution_ac_response.status_code, 200)

    def test_unqiue(self):
        self.client.login(username="root", password="dh-abstracts")
        auth_institution_ac_response = self.client.get(
            reverse("unrestricted-institution-autocomplete")
        )
        result_vals = [
            res["id"]
            for res in json.loads(auth_institution_ac_response.content)["results"]
        ]
        self.assertTrue(is_list_unique(result_vals))


class UnrestrictedCountryAutocompleteTest(TestCase):
    fixtures = ["test.json"]

    def test_no_public(self):
        country_ac_response = self.client.get(
            reverse("unrestricted-country-autocomplete")
        )
        self.assertEqual(country_ac_response.status_code, 403)

    def test_render(self):
        self.client.login(username="root", password="dh-abstracts")
        auth_country_ac_response = self.client.get(
            reverse("unrestricted-country-autocomplete")
        )
        self.assertEqual(auth_country_ac_response.status_code, 200)

    def test_unqiue(self):
        self.client.login(username="root", password="dh-abstracts")
        auth_country_ac_response = self.client.get(
            reverse("unrestricted-country-autocomplete")
        )
        result_vals = [
            res["id"] for res in json.loads(auth_country_ac_response.content)["results"]
        ]
        self.assertTrue(is_list_unique(result_vals))
