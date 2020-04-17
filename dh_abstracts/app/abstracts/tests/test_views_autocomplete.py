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

    def test_q(self):
        self.client.login(username="root", password="dh-abstracts")
        auth_appellation_ac_response = self.client.get(
            reverse("unrestricted-appellation-autocomplete"), data={"q": "franklin"}
        )
        self.assertRegex(str(auth_appellation_ac_response.content), "Franklin")
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

    def test_q(self):
        self.client.login(username="root", password="dh-abstracts")
        auth_work_ac_response = self.client.get(
            reverse("unrestricted-work-autocomplete"), data={"q": "foo"}
        )
        self.assertRegex(str(auth_work_ac_response.content), "Foo")
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

    def test_q(self):
        self.client.login(username="root", password="dh-abstracts")
        auth_keyword_ac_response = self.client.get(
            reverse("unrestricted-keyword-autocomplete"), data={"q": "lat"}
        )
        self.assertRegex(str(auth_keyword_ac_response.content), "Latin")
        result_vals = [
            res["id"] for res in json.loads(auth_keyword_ac_response.content)["results"]
        ]
        self.assertTrue(is_list_unique(result_vals))


class UnrestrictedLanguageAutocompleteTest(TestCase):
    fixtures = ["test.json"]

    def test_no_public(self):
        language_ac_response = self.client.get(
            reverse("unrestricted-language-autocomplete")
        )
        self.assertEqual(language_ac_response.status_code, 403)

    def test_render(self):
        self.client.login(username="root", password="dh-abstracts")
        auth_language_ac_response = self.client.get(
            reverse("unrestricted-language-autocomplete")
        )
        self.assertEqual(auth_language_ac_response.status_code, 200)

    def test_unqiue(self):
        self.client.login(username="root", password="dh-abstracts")
        auth_language_ac_response = self.client.get(
            reverse("unrestricted-language-autocomplete")
        )
        result_vals = [
            res["id"]
            for res in json.loads(auth_language_ac_response.content)["results"]
        ]
        self.assertTrue(is_list_unique(result_vals))

    def test_unqiue(self):
        self.client.login(username="root", password="dh-abstracts")
        auth_language_ac_response = self.client.get(
            reverse("unrestricted-language-autocomplete"), data={"q": "dut"}
        )
        self.assertRegex(str(auth_language_ac_response.content), "Dutch")
        result_vals = [
            res["id"]
            for res in json.loads(auth_language_ac_response.content)["results"]
        ]
        self.assertTrue(is_list_unique(result_vals))


class UnrestrictedDisciplineAutocompleteTest(TestCase):
    fixtures = ["test.json"]

    def test_no_public(self):
        discipline_ac_response = self.client.get(
            reverse("unrestricted-discipline-autocomplete")
        )
        self.assertEqual(discipline_ac_response.status_code, 403)

    def test_render(self):
        self.client.login(username="root", password="dh-abstracts")
        auth_discipline_ac_response = self.client.get(
            reverse("unrestricted-discipline-autocomplete")
        )
        self.assertEqual(auth_discipline_ac_response.status_code, 200)

    def test_unqiue(self):
        self.client.login(username="root", password="dh-abstracts")
        auth_discipline_ac_response = self.client.get(
            reverse("unrestricted-discipline-autocomplete")
        )
        result_vals = [
            res["id"]
            for res in json.loads(auth_discipline_ac_response.content)["results"]
        ]
        self.assertTrue(is_list_unique(result_vals))

    def test_q(self):
        self.client.login(username="root", password="dh-abstracts")
        auth_discipline_ac_response = self.client.get(
            reverse("unrestricted-discipline-autocomplete"), data={"q": "art"}
        )
        self.assertRegex(str(auth_discipline_ac_response.content), "Art")
        result_vals = [
            res["id"]
            for res in json.loads(auth_discipline_ac_response.content)["results"]
        ]
        self.assertTrue(is_list_unique(result_vals))


class UnrestrictedTopicAutocompleteTest(TestCase):
    fixtures = ["test.json"]

    def test_no_public(self):
        topic_ac_response = self.client.get(reverse("unrestricted-topic-autocomplete"))
        self.assertEqual(topic_ac_response.status_code, 403)

    def test_render(self):
        self.client.login(username="root", password="dh-abstracts")
        auth_topic_ac_response = self.client.get(
            reverse("unrestricted-topic-autocomplete")
        )
        self.assertEqual(auth_topic_ac_response.status_code, 200)

    def test_unqiue(self):
        self.client.login(username="root", password="dh-abstracts")
        auth_topic_ac_response = self.client.get(
            reverse("unrestricted-topic-autocomplete")
        )
        result_vals = [
            res["id"] for res in json.loads(auth_topic_ac_response.content)["results"]
        ]
        self.assertTrue(is_list_unique(result_vals))

    def test_q(self):
        self.client.login(username="root", password="dh-abstracts")
        auth_topic_ac_response = self.client.get(
            reverse("unrestricted-topic-autocomplete"), data={"q": "comic"}
        )
        self.assertRegex(str(auth_topic_ac_response.content), "Webcomics")
        result_vals = [
            res["id"] for res in json.loads(auth_topic_ac_response.content)["results"]
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

    def test_q(self):
        self.client.login(username="root", password="dh-abstracts")
        auth_author_ac_response = self.client.get(
            reverse("unrestricted-author-autocomplete"), data={"q": "frank"}
        )
        self.assertRegex(str(auth_author_ac_response.content), "Rosalind")
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

    def test_q(self):
        self.client.login(username="root", password="dh-abstracts")
        auth_affiliation_ac_response = self.client.get(
            reverse("unrestricted-affiliation-autocomplete"), data={"q": "libr"}
        )
        self.assertRegex(str(auth_affiliation_ac_response.content), "Stanford")
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

    def test_q(self):
        self.client.login(username="root", password="dh-abstracts")
        auth_institution_ac_response = self.client.get(
            reverse("unrestricted-institution-autocomplete"), data={"q": "wood"}
        )
        self.assertRegex(str(auth_institution_ac_response.json()), "Wood")
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

    def test_q(self):
        self.client.login(username="root", password="dh-abstracts")
        auth_country_ac_response = self.client.get(
            reverse("unrestricted-country-autocomplete"), data={"q": "uni"}
        )
        self.assertRegex(str(auth_country_ac_response.json()), "United")
        result_vals = [
            res["id"] for res in json.loads(auth_country_ac_response.content)["results"]
        ]
        self.assertTrue(is_list_unique(result_vals))
