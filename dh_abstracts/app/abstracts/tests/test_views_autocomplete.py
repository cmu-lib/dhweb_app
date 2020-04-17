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


class AppellationAutocompleteTest(TestCase):
    fixtures = ["test.json"]

    def test_no_public(self):
        appellation_ac_response = self.client.get(reverse("appellation-autocomplete"))
        self.assertEqual(appellation_ac_response.status_code, 403)

    def test_render(self):
        self.client.login(username="root", password="dh-abstracts")
        auth_appellation_ac_response = self.client.get(
            reverse("appellation-autocomplete")
        )
        self.assertEqual(auth_appellation_ac_response.status_code, 200)

    def test_unqiue(self):
        self.client.login(username="root", password="dh-abstracts")
        auth_appellation_ac_response = self.client.get(
            reverse("appellation-autocomplete")
        )
        result_vals = [
            res["id"]
            for res in json.loads(auth_appellation_ac_response.content)["results"]
        ]
        self.assertTrue(is_list_unique(result_vals))

    def test_q(self):
        self.client.login(username="root", password="dh-abstracts")
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

    def test_no_public(self):
        work_ac_response = self.client.get(reverse("work-autocomplete"))
        self.assertEqual(work_ac_response.status_code, 403)

    def test_render(self):
        self.client.login(username="root", password="dh-abstracts")
        auth_work_ac_response = self.client.get(reverse("work-autocomplete"))
        self.assertEqual(auth_work_ac_response.status_code, 200)

    def test_unqiue(self):
        self.client.login(username="root", password="dh-abstracts")
        auth_work_ac_response = self.client.get(reverse("work-autocomplete"))
        result_vals = [
            res["id"] for res in json.loads(auth_work_ac_response.content)["results"]
        ]
        self.assertTrue(is_list_unique(result_vals))

    def test_q(self):
        self.client.login(username="root", password="dh-abstracts")
        auth_work_ac_response = self.client.get(
            reverse("work-autocomplete"), data={"q": "foo"}
        )
        self.assertRegex(str(auth_work_ac_response.content), "Foo")
        result_vals = [
            res["id"] for res in json.loads(auth_work_ac_response.content)["results"]
        ]
        self.assertTrue(is_list_unique(result_vals))


class KeywordAutocompleteTest(TestCase):
    fixtures = ["test.json"]

    def test_no_public(self):
        keyword_ac_response = self.client.get(reverse("keyword-autocomplete"))
        self.assertEqual(keyword_ac_response.status_code, 403)

    def test_render(self):
        self.client.login(username="root", password="dh-abstracts")
        auth_keyword_ac_response = self.client.get(reverse("keyword-autocomplete"))
        self.assertEqual(auth_keyword_ac_response.status_code, 200)

    def test_unqiue(self):
        self.client.login(username="root", password="dh-abstracts")
        auth_keyword_ac_response = self.client.get(reverse("keyword-autocomplete"))
        result_vals = [
            res["id"] for res in json.loads(auth_keyword_ac_response.content)["results"]
        ]
        self.assertTrue(is_list_unique(result_vals))

    def test_q(self):
        self.client.login(username="root", password="dh-abstracts")
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

    def test_no_public(self):
        language_ac_response = self.client.get(reverse("language-autocomplete"))
        self.assertEqual(language_ac_response.status_code, 403)

    def test_render(self):
        self.client.login(username="root", password="dh-abstracts")
        auth_language_ac_response = self.client.get(reverse("language-autocomplete"))
        self.assertEqual(auth_language_ac_response.status_code, 200)

    def test_unqiue(self):
        self.client.login(username="root", password="dh-abstracts")
        auth_language_ac_response = self.client.get(reverse("language-autocomplete"))
        result_vals = [
            res["id"]
            for res in json.loads(auth_language_ac_response.content)["results"]
        ]
        self.assertTrue(is_list_unique(result_vals))

    def test_unqiue(self):
        self.client.login(username="root", password="dh-abstracts")
        auth_language_ac_response = self.client.get(
            reverse("language-autocomplete"), data={"q": "dut"}
        )
        self.assertRegex(str(auth_language_ac_response.content), "Dutch")
        result_vals = [
            res["id"]
            for res in json.loads(auth_language_ac_response.content)["results"]
        ]
        self.assertTrue(is_list_unique(result_vals))


class DisciplineAutocompleteTest(TestCase):
    fixtures = ["test.json"]

    def test_no_public(self):
        discipline_ac_response = self.client.get(reverse("discipline-autocomplete"))
        self.assertEqual(discipline_ac_response.status_code, 403)

    def test_render(self):
        self.client.login(username="root", password="dh-abstracts")
        auth_discipline_ac_response = self.client.get(
            reverse("discipline-autocomplete")
        )
        self.assertEqual(auth_discipline_ac_response.status_code, 200)

    def test_unqiue(self):
        self.client.login(username="root", password="dh-abstracts")
        auth_discipline_ac_response = self.client.get(
            reverse("discipline-autocomplete")
        )
        result_vals = [
            res["id"]
            for res in json.loads(auth_discipline_ac_response.content)["results"]
        ]
        self.assertTrue(is_list_unique(result_vals))

    def test_q(self):
        self.client.login(username="root", password="dh-abstracts")
        auth_discipline_ac_response = self.client.get(
            reverse("discipline-autocomplete"), data={"q": "art"}
        )
        self.assertRegex(str(auth_discipline_ac_response.content), "Art")
        result_vals = [
            res["id"]
            for res in json.loads(auth_discipline_ac_response.content)["results"]
        ]
        self.assertTrue(is_list_unique(result_vals))


class TopicAutocompleteTest(TestCase):
    fixtures = ["test.json"]

    def test_no_public(self):
        topic_ac_response = self.client.get(reverse("topic-autocomplete"))
        self.assertEqual(topic_ac_response.status_code, 403)

    def test_render(self):
        self.client.login(username="root", password="dh-abstracts")
        auth_topic_ac_response = self.client.get(reverse("topic-autocomplete"))
        self.assertEqual(auth_topic_ac_response.status_code, 200)

    def test_unqiue(self):
        self.client.login(username="root", password="dh-abstracts")
        auth_topic_ac_response = self.client.get(reverse("topic-autocomplete"))
        result_vals = [
            res["id"] for res in json.loads(auth_topic_ac_response.content)["results"]
        ]
        self.assertTrue(is_list_unique(result_vals))

    def test_q(self):
        self.client.login(username="root", password="dh-abstracts")
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

    def test_no_public(self):
        author_ac_response = self.client.get(reverse("author-autocomplete"))
        self.assertEqual(author_ac_response.status_code, 403)

    def test_render(self):
        self.client.login(username="root", password="dh-abstracts")
        auth_author_ac_response = self.client.get(reverse("author-autocomplete"))
        self.assertEqual(auth_author_ac_response.status_code, 200)

    def test_unqiue(self):
        self.client.login(username="root", password="dh-abstracts")
        auth_author_ac_response = self.client.get(reverse("author-autocomplete"))
        result_vals = [
            res["id"] for res in json.loads(auth_author_ac_response.content)["results"]
        ]
        self.assertTrue(is_list_unique(result_vals))

    def test_q(self):
        self.client.login(username="root", password="dh-abstracts")
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

    def test_no_public(self):
        affiliation_ac_response = self.client.get(reverse("affiliation-autocomplete"))
        self.assertEqual(affiliation_ac_response.status_code, 403)

    def test_render(self):
        self.client.login(username="root", password="dh-abstracts")
        auth_affiliation_ac_response = self.client.get(
            reverse("affiliation-autocomplete")
        )
        self.assertEqual(auth_affiliation_ac_response.status_code, 200)

    def test_unqiue(self):
        self.client.login(username="root", password="dh-abstracts")
        auth_affiliation_ac_response = self.client.get(
            reverse("affiliation-autocomplete")
        )
        result_vals = [
            res["id"]
            for res in json.loads(auth_affiliation_ac_response.content)["results"]
        ]
        self.assertTrue(is_list_unique(result_vals))

    def test_q(self):
        self.client.login(username="root", password="dh-abstracts")
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

    def test_no_public(self):
        institution_ac_response = self.client.get(reverse("institution-autocomplete"))
        self.assertEqual(institution_ac_response.status_code, 403)

    def test_render(self):
        self.client.login(username="root", password="dh-abstracts")
        auth_institution_ac_response = self.client.get(
            reverse("institution-autocomplete")
        )
        self.assertEqual(auth_institution_ac_response.status_code, 200)

    def test_unqiue(self):
        self.client.login(username="root", password="dh-abstracts")
        auth_institution_ac_response = self.client.get(
            reverse("institution-autocomplete")
        )
        result_vals = [
            res["id"]
            for res in json.loads(auth_institution_ac_response.content)["results"]
        ]
        self.assertTrue(is_list_unique(result_vals))

    def test_q(self):
        self.client.login(username="root", password="dh-abstracts")
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

    def test_no_public(self):
        country_ac_response = self.client.get(reverse("country-autocomplete"))
        self.assertEqual(country_ac_response.status_code, 403)

    def test_render(self):
        self.client.login(username="root", password="dh-abstracts")
        auth_country_ac_response = self.client.get(reverse("country-autocomplete"))
        self.assertEqual(auth_country_ac_response.status_code, 200)

    def test_unqiue(self):
        self.client.login(username="root", password="dh-abstracts")
        auth_country_ac_response = self.client.get(reverse("country-autocomplete"))
        result_vals = [
            res["id"] for res in json.loads(auth_country_ac_response.content)["results"]
        ]
        self.assertTrue(is_list_unique(result_vals))

    def test_q(self):
        self.client.login(username="root", password="dh-abstracts")
        auth_country_ac_response = self.client.get(
            reverse("country-autocomplete"), data={"q": "uni"}
        )
        self.assertRegex(str(auth_country_ac_response.json()), "United")
        result_vals = [
            res["id"] for res in json.loads(auth_country_ac_response.content)["results"]
        ]
        self.assertTrue(is_list_unique(result_vals))
