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

from abstracts.forms import WorkFilter


def is_list_unique(x):
    return len(x) == len(set(x))


class AppellationAutocompleteTest(TestCase):
    fixtures = ["test.json"]

    def test_render(self):
        auth_appellation_ac_response = self.client.get(
            reverse("appellation-autocomplete")
        )
        self.assertEqual(auth_appellation_ac_response.status_code, 200)

    def test_unique(self):
        auth_appellation_ac_response = self.client.get(
            reverse("appellation-autocomplete")
        )
        result_vals = [
            res["id"]
            for res in json.loads(auth_appellation_ac_response.content)["results"]
        ]
        self.assertTrue(is_list_unique(result_vals))

    def test_q(self):

        auth_appellation_ac_response = self.client.get(
            reverse("appellation-autocomplete"), data={"q": "franklin"}
        )
        self.assertRegex(str(auth_appellation_ac_response.content), "Franklin")
        result_vals = [
            res["id"]
            for res in json.loads(auth_appellation_ac_response.content)["results"]
        ]
        self.assertTrue(is_list_unique(result_vals))


class WorkAutocompleteTest(TestCase):
    fixtures = ["test.json"]

    def test_render(self):
        auth_work_ac_response = self.client.get(reverse("work-autocomplete"))
        self.assertEqual(auth_work_ac_response.status_code, 200)

    def test_unique(self):
        auth_work_ac_response = self.client.get(reverse("work-autocomplete"))
        result_vals = [
            res["id"] for res in json.loads(auth_work_ac_response.content)["results"]
        ]
        self.assertTrue(is_list_unique(result_vals))

    def test_q(self):
        auth_work_ac_response = self.client.get(
            reverse("work-autocomplete"), data={"q": "foo"}
        )
        self.assertRegex(str(auth_work_ac_response.content), "Foo")
        result_vals = [
            res["id"] for res in json.loads(auth_work_ac_response.content)["results"]
        ]
        self.assertTrue(is_list_unique(result_vals))

    def test_conf_q(self):
        auth_work_ac_response = self.client.get(
            reverse("work-autocomplete"),
            data={"forward": '{"conference": 1, "parents_only": true}'},
        )
        self.assertRegex(str(auth_work_ac_response.content), "big panel session")
        result_vals = [
            res["id"] for res in json.loads(auth_work_ac_response.content)["results"]
        ]
        self.assertTrue(is_list_unique(result_vals))

    def test_no_non_parent(self):
        auth_work_ac_response = self.client.get(
            reverse("work-autocomplete"),
            data={"forward": '{"conference": 1, "parents_only": true}'},
        )
        titles = [
            res["text"] for res in json.loads(auth_work_ac_response.content)["results"]
        ]
        self.assertNotIn("A Foo Too Far", titles)


class KeywordAutocompleteTest(TestCase):
    fixtures = ["test.json"]

    def test_render(self):
        auth_keyword_ac_response = self.client.get(reverse("keyword-autocomplete"))
        self.assertEqual(auth_keyword_ac_response.status_code, 200)

    def test_unique(self):
        auth_keyword_ac_response = self.client.get(reverse("keyword-autocomplete"))
        result_vals = [
            res["id"] for res in json.loads(auth_keyword_ac_response.content)["results"]
        ]
        self.assertTrue(is_list_unique(result_vals))

    def test_q(self):
        auth_keyword_ac_response = self.client.get(
            reverse("keyword-autocomplete"), data={"q": "lat"}
        )
        self.assertRegex(str(auth_keyword_ac_response.content), "Latin")
        result_vals = [
            res["id"] for res in json.loads(auth_keyword_ac_response.content)["results"]
        ]
        self.assertTrue(is_list_unique(result_vals))


class LanguageAutocompleteTest(TestCase):
    fixtures = ["test.json"]

    def test_unique(self):
        auth_language_ac_response = self.client.get(reverse("language-autocomplete"))
        result_vals = [
            res["id"]
            for res in json.loads(auth_language_ac_response.content)["results"]
        ]
        self.assertTrue(is_list_unique(result_vals))

    def test_q(self):
        auth_language_ac_response = self.client.get(
            reverse("language-autocomplete"), data={"q": "dut"}
        )
        self.assertRegex(str(auth_language_ac_response.content), "Dutch")
        result_vals = [
            res["id"]
            for res in json.loads(auth_language_ac_response.content)["results"]
        ]
        self.assertTrue(is_list_unique(result_vals))


class TopicAutocompleteTest(TestCase):
    fixtures = ["test.json"]

    def test_render(self):
        auth_topic_ac_response = self.client.get(reverse("topic-autocomplete"))
        self.assertEqual(auth_topic_ac_response.status_code, 200)

    def test_unique(self):
        auth_topic_ac_response = self.client.get(reverse("topic-autocomplete"))
        result_vals = [
            res["id"] for res in json.loads(auth_topic_ac_response.content)["results"]
        ]
        self.assertTrue(is_list_unique(result_vals))

    def test_q(self):
        auth_topic_ac_response = self.client.get(
            reverse("topic-autocomplete"), data={"q": "comic"}
        )
        self.assertRegex(str(auth_topic_ac_response.content), "Webcomics")
        result_vals = [
            res["id"] for res in json.loads(auth_topic_ac_response.content)["results"]
        ]
        self.assertTrue(is_list_unique(result_vals))


class AuthorAutocompleteTest(TestCase):
    fixtures = ["test.json"]

    def test_render(self):
        auth_author_ac_response = self.client.get(reverse("author-autocomplete"))
        self.assertEqual(auth_author_ac_response.status_code, 200)

    def test_unique(self):
        auth_author_ac_response = self.client.get(reverse("author-autocomplete"))
        result_vals = [
            res["id"] for res in json.loads(auth_author_ac_response.content)["results"]
        ]
        self.assertTrue(is_list_unique(result_vals))

    def test_q(self):
        auth_author_ac_response = self.client.get(
            reverse("author-autocomplete"), data={"q": "frank"}
        )
        self.assertRegex(str(auth_author_ac_response.content), "Rosalind")
        result_vals = [
            res["id"] for res in json.loads(auth_author_ac_response.content)["results"]
        ]
        self.assertTrue(is_list_unique(result_vals))


class AffiliationAutocompleteTest(TestCase):
    fixtures = ["test.json"]

    def test_render(self):
        auth_affiliation_ac_response = self.client.get(
            reverse("affiliation-autocomplete")
        )
        self.assertEqual(auth_affiliation_ac_response.status_code, 200)

    def test_unique(self):
        auth_affiliation_ac_response = self.client.get(
            reverse("affiliation-autocomplete")
        )
        result_vals = [
            res["id"]
            for res in json.loads(auth_affiliation_ac_response.content)["results"]
        ]
        self.assertTrue(is_list_unique(result_vals))

    def test_q(self):
        auth_affiliation_ac_response = self.client.get(
            reverse("affiliation-autocomplete"), data={"q": "libr"}
        )
        self.assertRegex(str(auth_affiliation_ac_response.content), "Stanford")
        result_vals = [
            res["id"]
            for res in json.loads(auth_affiliation_ac_response.content)["results"]
        ]
        self.assertTrue(is_list_unique(result_vals))


class InstitutionAutocompleteTest(TestCase):
    fixtures = ["test.json"]

    def test_render(self):
        auth_institution_ac_response = self.client.get(
            reverse("institution-autocomplete")
        )
        self.assertEqual(auth_institution_ac_response.status_code, 200)

    def test_unique(self):
        auth_institution_ac_response = self.client.get(
            reverse("institution-autocomplete")
        )
        result_vals = [
            res["id"]
            for res in json.loads(auth_institution_ac_response.content)["results"]
        ]
        self.assertTrue(is_list_unique(result_vals))

    def test_q(self):
        auth_institution_ac_response = self.client.get(
            reverse("institution-autocomplete"), data={"q": "wood"}
        )
        self.assertRegex(str(auth_institution_ac_response.json()), "Wood")
        result_vals = [
            res["id"]
            for res in json.loads(auth_institution_ac_response.content)["results"]
        ]
        self.assertTrue(is_list_unique(result_vals))


class CountryAutocompleteTest(TestCase):
    fixtures = ["test.json"]

    def test_render(self):
        auth_country_ac_response = self.client.get(reverse("country-autocomplete"))
        self.assertEqual(auth_country_ac_response.status_code, 200)

    def test_unique(self):
        auth_country_ac_response = self.client.get(reverse("country-autocomplete"))
        result_vals = [
            res["id"] for res in json.loads(auth_country_ac_response.content)["results"]
        ]
        self.assertTrue(is_list_unique(result_vals))

    def test_q(self):
        auth_country_ac_response = self.client.get(
            reverse("country-autocomplete"), data={"q": "uni"}
        )
        self.assertRegex(str(auth_country_ac_response.json()), "United")
        result_vals = [
            res["id"] for res in json.loads(auth_country_ac_response.content)["results"]
        ]
        self.assertTrue(is_list_unique(result_vals))


class ConferenceAutocompleteTest(TestCase):
    fixtures = ["test.json"]

    def test_render(self):
        auth_conference_ac_response = self.client.get(
            reverse("conference-autocomplete")
        )
        self.assertEqual(auth_conference_ac_response.status_code, 200)

    def test_unique(self):
        auth_conference_ac_response = self.client.get(
            reverse("conference-autocomplete")
        )
        result_vals = [
            res["id"]
            for res in json.loads(auth_conference_ac_response.content)["results"]
        ]
        self.assertTrue(is_list_unique(result_vals))

    def test_q(self):
        auth_conference_ac_response = self.client.get(
            reverse("conference-autocomplete"), data={"q": "Toronto"}
        )
        self.assertRegex(str(auth_conference_ac_response.json()), "Toronto")
        result_vals = [
            res["id"]
            for res in json.loads(auth_conference_ac_response.content)["results"]
        ]
        self.assertTrue(is_list_unique(result_vals))
