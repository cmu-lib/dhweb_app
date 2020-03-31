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


def publicly_available(testcase, viewname, **kwargs):
    res = testcase.client.get(reverse(viewname, **kwargs))
    testcase.assertEqual(res.status_code, 200)


def privately_available(testcase, viewname, **kwargs):
    target_url = reverse(viewname, **kwargs)
    redirected_url = f"{reverse('login')}?next={target_url}"
    res = testcase.client.get(target_url, follow=True)
    testcase.assertRedirects(res, redirected_url)
    testcase.client.login(username="root", password="dh-abstracts")
    auth_res = testcase.client.get(target_url)
    testcase.assertEqual(auth_res.status_code, 200)


def as_auth(func):
    def auth_client(self):
        self.client.login(username="root", password="dh-abstracts")
        return func(self)

    return auth_client


class EmptyListViewTest(TestCase):
    """
    Test pages when the database is empty
    """

    def test_home_blank(self):
        publicly_available(self, "home_view")

    def test_work_blank(self):
        publicly_available(self, "work_list")

    def test_author_blank(self):
        publicly_available(self, "author_list")

    def test_conference_blank(self):
        publicly_available(self, "conference_list")


class DownloadPageTest(TestCase):
    fixtures = ["test.json"]

    def test_render(self):
        privately_available(self, "download_data")


class AuthorListViewTest(TestCase):
    """
    Test Author list page
    """

    fixtures = ["test.json"]

    def test_render(self):
        publicly_available(self, "author_list")

    def test_query_filtered_count(self):
        res = self.client.get(reverse("author_list"))
        self.assertEqual(
            res.context["filtered_authors_count"], len(res.context["author_list"])
        )

    def test_query_total_count(self):
        res = self.client.get(reverse("author_list"))
        self.assertIsInstance(res.context["available_authors_count"], int)

    def test_unique(self):
        res = self.client.get(reverse("author_list"))
        self.assertTrue(is_list_unique(res.context["author_list"]))


class AuthorFullListViewTest(TestCase):
    """
    Test full Author list page
    """

    fixtures = ["test.json"]

    def test_render(self):
        privately_available(self, "full_author_list")

    @as_auth
    def test_query_filtered_count(self):
        res = self.client.get(reverse("full_author_list"))
        self.assertEqual(
            res.context["filtered_authors_count"], len(res.context["author_list"])
        )

    @as_auth
    def test_query_total_count(self):
        res = self.client.get(reverse("full_author_list"))
        self.assertIsInstance(res.context["available_authors_count"], int)

    @as_auth
    def test_unique(self):
        res = self.client.get(reverse("full_author_list"))
        self.assertTrue(is_list_unique(res.context["author_list"]))

    @as_auth
    def test_filter_affiliation(self):
        res = self.client.get(reverse("full_author_list"), data={"affiliation": 1})
        for author in res.context["author_list"]:
            self.assertTrue(
                Affiliation.objects.filter(pk=1, asserted_by__author=author.pk).exists()
            )


class WorkFullListViewTest(TestCase):
    """
    Test full Work list page
    """

    fixtures = ["test.json"]

    def test_render(self):
        privately_available(self, "full_work_list")

    @as_auth
    def test_query_filtered_count(self):
        res = self.client.get(reverse("full_work_list"))
        self.assertEqual(
            res.context["filtered_works_count"], len(res.context["work_list"])
        )

    @as_auth
    def test_query_total_count(self):
        res = self.client.get(reverse("full_work_list"))
        self.assertIsInstance(res.context["available_works_count"], int)

    @as_auth
    def test_unique(self):
        res = self.client.get(reverse("full_work_list"))
        self.assertTrue(is_list_unique(res.context["work_list"]))


class InstitutionFullListViewTest(TestCase):
    """
    Test full Institution list page
    """

    fixtures = ["test.json"]

    def test_render(self):
        privately_available(self, "full_institution_list")

    @as_auth
    def test_query_filtered_count(self):
        res = self.client.get(reverse("full_institution_list"))
        self.assertEqual(
            res.context["filtered_institutions_count"],
            len(res.context["institution_list"]),
        )

    @as_auth
    def test_query_total_count(self):
        res = self.client.get(reverse("full_institution_list"))
        self.assertIsInstance(res.context["available_institutions_count"], int)

    @as_auth
    def test_unique(self):
        res = self.client.get(reverse("full_institution_list"))
        self.assertTrue(is_list_unique(res.context["institution_list"]))

    @as_auth
    def test_sort(self):
        res = self.client.get(reverse("full_institution_list"), data={"ordering": "a"})
        self.assertLess(
            res.context["institution_list"][0].name,
            res.context["institution_list"][1].name,
        )
        res = self.client.get(
            reverse("full_institution_list"), data={"ordering": "n_dsc"}
        )
        self.assertGreaterEqual(
            Authorship.objects.filter(
                affiliations__institution=res.context["institution_list"][0]
            ).count(),
            Authorship.objects.filter(
                affiliations__institution=res.context["institution_list"][1]
            ).count(),
        )
        res = self.client.get(
            reverse("full_institution_list"), data={"ordering": "n_asc"}
        )
        self.assertLessEqual(
            Authorship.objects.filter(
                affiliations__institution=res.context["institution_list"][0]
            ).count(),
            Authorship.objects.filter(
                affiliations__institution=res.context["institution_list"][1]
            ).count(),
        )


class AuthorInstitutionFullListViewTest(TestCase):
    """
    Test Author-Institution list page
    """

    fixtures = ["test.json"]

    def test_render(self):
        privately_available(self, "author_institution_list")

    @as_auth
    def test_query_filtered_count(self):
        res = self.client.get(reverse("author_institution_list"))
        self.assertEqual(
            res.context["filtered_institutions_count"],
            len(res.context["institution_list"]),
        )

    @as_auth
    def test_query_total_count(self):
        res = self.client.get(reverse("author_institution_list"))
        self.assertIsInstance(res.context["available_institutions_count"], int)

    @as_auth
    def test_unique(self):
        res = self.client.get(reverse("author_institution_list"))
        self.assertTrue(is_list_unique(res.context["institution_list"]))

    @as_auth
    def test_sort(self):
        res = self.client.get(
            reverse("author_institution_list"), data={"ordering": "a"}
        )
        self.assertLess(
            res.context["institution_list"][0].name,
            res.context["institution_list"][1].name,
        )
        res = self.client.get(
            reverse("author_institution_list"), data={"ordering": "n_dsc"}
        )
        self.assertGreaterEqual(
            Authorship.objects.filter(
                affiliations__institution=res.context["institution_list"][0]
            ).count(),
            Authorship.objects.filter(
                affiliations__institution=res.context["institution_list"][1]
            ).count(),
        )
        res = self.client.get(
            reverse("author_institution_list"), data={"ordering": "n_asc"}
        )
        self.assertLessEqual(
            Authorship.objects.filter(
                affiliations__institution=res.context["institution_list"][0]
            ).count(),
            Authorship.objects.filter(
                affiliations__institution=res.context["institution_list"][1]
            ).count(),
        )


class AuthorDetailViewTest(TestCase):
    """
    Test Author detail page
    """

    fixtures = ["test.json"]

    def test_render(self):
        publicly_available(self, "author_detail", kwargs={"author_id": 1})

    def test_404(self):
        res = self.client.get(reverse("author_detail", kwargs={"author_id": 100}))
        self.assertEqual(res.status_code, 404)

    def test_works_unqiue_in_series(self):
        res = self.client.get(reverse("author_detail", kwargs={"author_id": 1}))
        for series in res.context["split_works"]:
            self.assertTrue(is_list_unique(series["works"]))

    def test_appellations_unique(self):
        res = self.client.get(reverse("author_detail", kwargs={"author_id": 1}))
        self.assertTrue(
            is_list_unique(
                [d["appellation"] for d in res.context["appellation_assertions"]]
            )
        )

    def test_affiliations_unique_institutions(self):
        res = self.client.get(reverse("author_detail", kwargs={"author_id": 1}))
        self.assertTrue(
            is_list_unique(
                [d["institution"] for d in res.context["affiliation_assertions"]]
            )
        )

    def test_affiliations_each_has_value(self):
        res = self.client.get(reverse("author_detail", kwargs={"author_id": 1}))
        for assertion in res.context["affiliation_assertions"]:
            self.assertGreaterEqual(len(assertion["works"]), 1)
            self.assertTrue(is_list_unique(assertion["works"]))

    def test_unaccepted_author(self):
        """
        Authors with only submitted papers should redirect with errors
        """
        res = self.client.get(
            reverse("author_detail", kwargs={"author_id": 3}), follow=True
        )
        self.assertRedirects(res, reverse("author_list"))
        self.assertGreaterEqual(len(res.context["messages"]), 1)


class WorkListViewTest(TestCase):
    """
    Test Work list page
    """

    fixtures = ["test.json"]

    def test_render(self):
        publicly_available(self, "work_list")

    def test_query_filtered_count(self):
        res = self.client.get(reverse("work_list"))
        self.assertEqual(
            res.context["filtered_works_count"], len(res.context["work_list"])
        )

    def test_query_total_count(self):
        res = self.client.get(reverse("work_list"))
        self.assertIsInstance(res.context["available_works_count"], int)

    def test_form(self):
        res = self.client.get(reverse("work_list"))
        self.assertIsInstance(res.context["work_filter_form"], WorkFilter)

    def test_unique_set(self):
        res = self.client.get(reverse("work_list"))
        self.assertEqual(
            len(set(res.context["work_list"])), res.context["filtered_works_count"]
        )


class WorkDetailViewTest(TestCase):
    """
    Test Work detail view
    """

    fixtures = ["test.json"]

    def test_render(self):
        publicly_available(self, "work_detail", kwargs={"work_id": 1})

    def test_404(self):
        res = self.client.get(reverse("work_detail", kwargs={"work_id": 100}))
        self.assertEqual(res.status_code, 404)

    def test_is_work(self):
        res = self.client.get(reverse("work_detail", kwargs={"work_id": 1}))
        self.assertIsInstance(res.context["work"], Work)

    def test_authorships_unique(self):
        res = self.client.get(reverse("work_detail", kwargs={"work_id": 1}))
        self.assertTrue(is_list_unique(res.context["authorships"]))


class ConferenceListViewTest(TestCase):
    """
    Test Conference list view
    """

    fixtures = ["test.json"]

    def test_render(self):
        publicly_available(self, "conference_list")

    def test_has_unaffiliated_conferences(self):
        res = self.client.get(reverse("conference_list"))
        self.assertIn(
            Conference.objects.filter(series__isnull=True).first(),
            res.context["standalone_conferences"],
        )


class FullConferenceListViewTest(TestCase):
    """
    Test Full Conference list view
    """

    fixtures = ["test.json"]

    def test_render(self):
        privately_available(self, "full_conference_list")


class AuthorMergeViewTest(TestCase):
    fixtures = ["test.json"]

    def test_render(self):
        privately_available(self, "author_merge", kwargs={"author_id": 1})

    @as_auth
    def test_404(self):
        res = self.client.get(
            reverse("author_merge", kwargs={"author_id": 100}), follow=True
        )
        self.assertEqual(res.status_code, 404)

    @as_auth
    def test_post(self):
        res = self.client.post(
            reverse("author_merge", kwargs={"author_id": 1}),
            data={"into": 2},
            follow=True,
        )
        expected_redirect = reverse("author_detail", kwargs={"author_id": 2})
        self.assertRedirects(res, expected_redirect)
        self.assertFalse(Author.objects.filter(pk=1).exists())
        self.assertContains(res, "updated")
        self.assertContains(res, "deleted")

    @as_auth
    def test_invalid_author(self):
        res = self.client.post(
            reverse("author_merge", kwargs={"author_id": 1}),
            data={"into": 1},
            follow=True,
        )
        expected_redirect = reverse("author_merge", kwargs={"author_id": 1})
        self.assertRedirects(res, expected_redirect)
        self.assertContains(res, "You cannot merge an author into themselves")


class InstitutionMergeViewTest(TestCase):
    fixtures = ["test.json"]

    def test_render(self):
        privately_available(self, "institution_merge", kwargs={"institution_id": 1})

    @as_auth
    def test_404(self):
        res = self.client.get(
            reverse("institution_merge", kwargs={"institution_id": 100}), follow=True
        )
        self.assertEqual(res.status_code, 404)

    @as_auth
    def test_post(self):
        res = self.client.post(
            reverse("institution_merge", kwargs={"institution_id": 1}),
            data={"into": 2},
            follow=True,
        )
        expected_redirect = reverse("institution_edit", kwargs={"pk": 2})
        self.assertRedirects(res, expected_redirect)
        self.assertFalse(Institution.objects.filter(pk=1).exists())
        self.assertContains(res, "updated")

    @as_auth
    def test_invalid_institution(self):
        res = self.client.post(
            reverse("institution_merge", kwargs={"institution_id": 1}),
            data={"into": 1},
            follow=True,
        )
        expected_redirect = reverse("institution_merge", kwargs={"institution_id": 1})
        self.assertRedirects(res, expected_redirect)
        self.assertContains(res, "You cannot merge an institution into itself")


class AffiliationMergeViewTest(TestCase):
    fixtures = ["test.json"]

    def test_render(self):
        privately_available(self, "affiliation_merge", kwargs={"affiliation_id": 1})

    @as_auth
    def test_404(self):
        res = self.client.get(
            reverse("affiliation_merge", kwargs={"affiliation_id": 100}), follow=True
        )
        self.assertEqual(res.status_code, 404)

    @as_auth
    def test_post(self):
        res = self.client.post(
            reverse("affiliation_merge", kwargs={"affiliation_id": 1}),
            data={"into": 2},
            follow=True,
        )
        expected_redirect = reverse("affiliation_edit", kwargs={"pk": 2})
        self.assertRedirects(res, expected_redirect)
        self.assertFalse(Affiliation.objects.filter(pk=1).exists())
        self.assertContains(res, "updated")

    @as_auth
    def test_invalid_affiliation(self):
        res = self.client.post(
            reverse("affiliation_merge", kwargs={"affiliation_id": 1}),
            data={"into": 1},
            follow=True,
        )
        expected_redirect = reverse("affiliation_merge", kwargs={"affiliation_id": 1})
        self.assertRedirects(res, expected_redirect)
        self.assertContains(res, "You cannot merge an affiliation into itself")


class AffiliationMultiMergeViewTest(TestCase):
    fixtures = ["test.json"]

    def test_render(self):
        privately_available(self, "affiliation_multi_merge")

    @as_auth
    def test_post(self):
        res = self.client.post(
            reverse("affiliation_multi_merge"),
            data={"sources": [1, 3, 4], "into": 2},
            follow=True,
        )
        expected_redirect = reverse("affiliation_edit", kwargs={"pk": 2})
        self.assertRedirects(res, expected_redirect)
        self.assertFalse(Affiliation.objects.filter(pk=1).exists())
        self.assertTrue(Affiliation.objects.filter(pk=2).exists())
        self.assertFalse(Affiliation.objects.filter(pk=3).exists())
        self.assertFalse(Affiliation.objects.filter(pk=4).exists())
        self.assertContains(res, "updated")


class InstitutionMultiMergeViewTest(TestCase):
    fixtures = ["test.json"]

    def test_render(self):
        privately_available(self, "institution_multi_merge")

    @as_auth
    def test_post(self):
        res = self.client.post(
            reverse("institution_multi_merge"),
            data={"sources": [1, 3], "into": 2},
            follow=True,
        )
        expected_redirect = reverse("institution_edit", kwargs={"pk": 2})
        self.assertRedirects(res, expected_redirect)
        self.assertFalse(Institution.objects.filter(pk=1).exists())
        self.assertTrue(Institution.objects.filter(pk=2).exists())
        self.assertFalse(Institution.objects.filter(pk=3).exists())
        self.assertContains(res, "updated")


class WipeUnusedViewTest(TestCase):
    fixtures = ["test.json"]

    def test_render(self):
        privately_available(self, "wipe_unused")

    @as_auth
    def test_has_dict(self):
        res = self.client.get(reverse("wipe_unused"))
        self.assertIsInstance(res.context["deletions"], dict)
        self.assertIsInstance(res.context["hanging_items"], bool)
        self.assertTrue(res.context["hanging_items"])

    @as_auth
    def test_post(self):
        res = self.client.post(reverse("wipe_unused"))
        res = self.client.post(reverse("wipe_unused"))
        self.assertFalse(res.context["hanging_items"])


class CreateConferenceViewTest(TestCase):
    fixtures = ["test.json"]

    def test_render(self):
        privately_available(self, "conference_create")

    @as_auth
    def test_post(self):
        res = self.client.post(
            reverse("conference_create"),
            data={
                "year": 1987,
                "venue": "foo",
                "venue_abbreviation": "bar",
                "notes": "buzz",
            },
            follow=True,
        )
        self.assertContains(res, "created")
        self.assertTrue(Conference.objects.filter(year=1987, venue="foo").exists())


class EditConferenceViewTest(TestCase):
    fixtures = ["test.json"]

    def test_render(self):
        privately_available(self, "conference_edit", kwargs={"pk": 1})

    @as_auth
    def test_post(self):
        res = self.client.post(
            reverse("conference_edit", kwargs={"pk": 1}),
            data={
                "year": "1987",
                "venue": "foo",
                "venue_abbreviation": "bar",
                "notes": "buzz",
                "organizers": ["1"],
                "form-0-number": [""],
                "form-0-series": ["1"],
                "form-INITIAL_FORMS": ["1"],
                "form-MAX_NUM_FORMS": ["1000"],
                "form-MIN_NUM_FORMS": ["0"],
                "form-TOTAL_FORMS": ["1"],
            },
            follow=True,
        )
        self.assertContains(res, "updated")


class DeleteConferenceViewTest(TestCase):
    fixtures = ["test.json"]

    def test_render(self):
        privately_available(self, "conference_delete", kwargs={"pk": 1})

    @as_auth
    def test_post(self):
        res = self.client.post(
            reverse("conference_delete", kwargs={"pk": 1}), follow=True
        )
        self.assertContains(res, "deleted")
        self.assertFalse(Conference.objects.filter(pk=1).exists())


class CreateSeriesViewTest(TestCase):
    fixtures = ["test.json"]

    def test_render(self):
        privately_available(self, "series_create")

    @as_auth
    def test_post(self):
        res = self.client.post(
            reverse("series_create"),
            data={"title": "foo", "abbreviation": "bar", "notes": "buzz"},
            follow=True,
        )
        self.assertContains(res, "created")


class EditSeriesViewTest(TestCase):
    fixtures = ["test.json"]

    def test_render(self):
        privately_available(self, "series_edit", kwargs={"pk": 1})

    @as_auth
    def test_post(self):
        res = self.client.post(
            reverse("series_edit", kwargs={"pk": 1}),
            data={"title": "fi", "abbreviation": "fi", "notes": "buzz"},
            follow=True,
        )
        self.assertContains(res, "updated")


class DeleteSeriesViewTest(TestCase):
    fixtures = ["test.json"]

    def test_render(self):
        privately_available(self, "series_delete", kwargs={"pk": 1})

    @as_auth
    def test_post(self):
        res = self.client.post(reverse("series_delete", kwargs={"pk": 1}), follow=True)
        self.assertContains(res, "deleted")
        self.assertFalse(ConferenceSeries.objects.filter(pk=1).exists())


class OrganizerListViewTest(TestCase):
    fixtures = ["test.json"]

    def test_render(self):
        privately_available(self, "full_organizer_list")

    @as_auth
    def test_unique(self):
        res = self.client.get(reverse("full_organizer_list"))
        self.assertTrue(is_list_unique(res.context["organizer_list"]))


class CreateOrganizerViewTest(TestCase):
    fixtures = ["test.json"]

    def test_render(self):
        privately_available(self, "organizer_create")

    @as_auth
    def test_post(self):
        res = self.client.post(
            reverse("organizer_create"),
            data={"title": "foo", "abbreviation": "bar", "notes": "buzz"},
            follow=True,
        )
        self.assertContains(res, "created")


class EditOrganizerViewTest(TestCase):
    fixtures = ["test.json"]

    def test_render(self):
        privately_available(self, "organizer_edit", kwargs={"pk": 1})

    @as_auth
    def test_post(self):
        res = self.client.post(
            reverse("organizer_edit", kwargs={"pk": 1}),
            data={"title": "foo", "abbreviation": "bar", "notes": "buzz"},
            follow=True,
        )
        self.assertEquals(res.status_code, 200)


class DeleteWorkViewTest(TestCase):
    fixtures = ["test.json"]

    def test_render(self):
        privately_available(self, "work_delete", kwargs={"pk": 1})

    @as_auth
    def test_post(self):
        res = self.client.post(reverse("work_delete", kwargs={"pk": 1}), follow=True)
        self.assertFalse(Work.objects.filter(pk=1).exists())


class AuthorJSONViewTest(TestCase):
    fixtures = ["test.json"]

    def test_render(self):
        privately_available(self, "author-info-json", kwargs={"author_id": 1})

    @as_auth
    def test_format(self):
        res = self.client.get(reverse("author-info-json", kwargs={"author_id": 1}))
        self.assertTrue("first_name" in json.dumps(str(res.content)))
        self.assertTrue("last_name" in json.dumps(str(res.content)))
        self.assertTrue("affiliation" in json.dumps(str(res.content)))


class AffiliationJSONViewTest(TestCase):
    fixtures = ["test.json"]

    def test_render(self):
        privately_available(self, "affiliation-info-json", kwargs={"affiliation_id": 1})

    @as_auth
    def test_format(self):
        res = self.client.get(
            reverse("affiliation-info-json", kwargs={"affiliation_id": 1})
        )
        self.assertTrue("department" in json.dumps(str(res.content)))
        self.assertTrue("institution" in json.dumps(str(res.content)))


class KeywordFullListViewTest(TestCase):
    """
    Test full Keyword list page
    """

    fixtures = ["test.json"]

    def test_render(self):
        privately_available(self, "full_keyword_list")

    @as_auth
    def test_query_filtered_count(self):
        res = self.client.get(reverse("full_keyword_list"))
        self.assertEqual(
            res.context["filtered_tags_count"], len(res.context["tag_list"])
        )

    @as_auth
    def test_query_total_count(self):
        res = self.client.get(reverse("full_keyword_list"))
        self.assertIsInstance(res.context["available_tags_count"], int)

    @as_auth
    def test_unique(self):
        res = self.client.get(reverse("full_keyword_list"))
        self.assertTrue(is_list_unique(res.context["tag_list"]))

    @as_auth
    def test_sort(self):
        res = self.client.get(reverse("full_keyword_list"), data={"ordering": "a"})
        self.assertTrue(res.context["tag_list"].ordered)
        res = self.client.get(reverse("full_keyword_list"), data={"ordering": "n_dsc"})
        self.assertTrue(res.context["tag_list"].ordered)
        res = self.client.get(reverse("full_keyword_list"), data={"ordering": "n_asc"})
        self.assertTrue(res.context["tag_list"].ordered)


class CreateKeywordViewTest(TestCase):
    fixtures = ["test.json"]

    def test_render(self):
        privately_available(self, "keyword_create")

    @as_auth
    def test_post(self):
        res = self.client.post(
            reverse("keyword_create"), data={"title": "foo"}, follow=True
        )
        self.assertContains(res, "created")
        self.assertTrue(Keyword.objects.filter(title="foo").exists())


class EditKeywordViewTest(TestCase):
    fixtures = ["test.json"]

    def test_render(self):
        privately_available(self, "keyword_edit", kwargs={"pk": 1})

    @as_auth
    def test_post(self):
        res = self.client.post(
            reverse("keyword_edit", kwargs={"pk": 1}),
            data={"title": "buzz"},
            follow=True,
        )
        self.assertContains(res, "updated")
        self.assertTrue(Keyword.objects.filter(title="buzz").exists())


class DeleteKeywordViewTest(TestCase):
    fixtures = ["test.json"]

    def test_render(self):
        privately_available(self, "keyword_delete", kwargs={"pk": 1})

    @as_auth
    def test_post(self):
        res = self.client.post(reverse("keyword_delete", kwargs={"pk": 1}), follow=True)
        self.assertFalse(Keyword.objects.filter(pk=1).exists())


class KeywordMergeViewTest(TestCase):
    fixtures = ["test.json"]

    def test_render(self):
        privately_available(self, "keyword_merge", kwargs={"keyword_id": 1})

    @as_auth
    def test_404(self):
        res = self.client.get(
            reverse("keyword_merge", kwargs={"keyword_id": 100}), follow=True
        )
        self.assertEqual(res.status_code, 404)

    @as_auth
    def test_post(self):
        res = self.client.post(
            reverse("keyword_merge", kwargs={"keyword_id": 1}),
            data={"into": 2},
            follow=True,
        )
        expected_redirect = reverse("keyword_edit", kwargs={"pk": 2})
        self.assertRedirects(res, expected_redirect)
        self.assertFalse(Keyword.objects.filter(pk=1).exists())
        self.assertContains(res, "updated")
        self.assertContains(res, "deleted")

    @as_auth
    def test_invalid_keyword(self):
        res = self.client.post(
            reverse("keyword_merge", kwargs={"keyword_id": 1}),
            data={"into": 1},
            follow=True,
        )
        expected_redirect = reverse("keyword_merge", kwargs={"keyword_id": 1})
        self.assertRedirects(res, expected_redirect)
        self.assertContains(res, "You cannot merge a keyword into itself")


class KeywordMultiMergeViewTest(TestCase):
    fixtures = ["test.json"]

    def test_render(self):
        privately_available(self, "keyword_multi_merge")

    @as_auth
    def test_post(self):
        res = self.client.post(
            reverse("keyword_multi_merge"),
            data={"sources": [1, 3, 4], "into": 2},
            follow=True,
        )
        expected_redirect = reverse("keyword_edit", kwargs={"pk": 2})
        self.assertRedirects(res, expected_redirect)
        self.assertFalse(Keyword.objects.filter(pk=1).exists())
        self.assertTrue(Keyword.objects.filter(pk=2).exists())
        self.assertFalse(Keyword.objects.filter(pk=3).exists())
        self.assertFalse(Keyword.objects.filter(pk=4).exists())
        self.assertContains(res, "updated")
        self.assertContains(res, "deleted")


class TopicFullListViewTest(TestCase):
    """
    Test full Topic list page
    """

    fixtures = ["test.json"]

    def test_render(self):
        privately_available(self, "full_topic_list")

    @as_auth
    def test_query_filtered_count(self):
        res = self.client.get(reverse("full_topic_list"))
        self.assertEqual(
            res.context["filtered_tags_count"], len(res.context["tag_list"])
        )

    @as_auth
    def test_query_total_count(self):
        res = self.client.get(reverse("full_topic_list"))
        self.assertIsInstance(res.context["available_tags_count"], int)

    @as_auth
    def test_unique(self):
        res = self.client.get(reverse("full_topic_list"))
        self.assertTrue(is_list_unique(res.context["tag_list"]))


class CreateTopicViewTest(TestCase):
    fixtures = ["test.json"]

    def test_render(self):
        privately_available(self, "topic_create")

    @as_auth
    def test_post(self):
        res = self.client.post(
            reverse("topic_create"), data={"title": "foo"}, follow=True
        )
        self.assertContains(res, "created")
        self.assertTrue(Topic.objects.filter(title="foo").exists())


class EditTopicViewTest(TestCase):
    fixtures = ["test.json"]

    def test_render(self):
        privately_available(self, "topic_edit", kwargs={"pk": 1})

    @as_auth
    def test_post(self):
        res = self.client.post(
            reverse("topic_edit", kwargs={"pk": 1}), data={"title": "buzz"}, follow=True
        )
        self.assertContains(res, "updated")
        self.assertTrue(Topic.objects.filter(title="buzz").exists())


class DeleteTopicViewTest(TestCase):
    fixtures = ["test.json"]

    def test_render(self):
        privately_available(self, "topic_delete", kwargs={"pk": 1})

    @as_auth
    def test_post(self):
        res = self.client.post(reverse("topic_delete", kwargs={"pk": 1}), follow=True)
        self.assertFalse(Topic.objects.filter(pk=1).exists())


class TopicMultiMergeViewTest(TestCase):
    fixtures = ["test.json"]

    def test_render(self):
        privately_available(self, "topic_multi_merge")

    @as_auth
    def test_post(self):
        res = self.client.post(
            reverse("topic_multi_merge"),
            data={"sources": [1, 3, 4], "into": 2},
            follow=True,
        )
        expected_redirect = reverse("topic_edit", kwargs={"pk": 2})
        self.assertRedirects(res, expected_redirect)
        self.assertFalse(Topic.objects.filter(pk=1).exists())
        self.assertTrue(Topic.objects.filter(pk=2).exists())
        self.assertFalse(Topic.objects.filter(pk=3).exists())
        self.assertFalse(Topic.objects.filter(pk=4).exists())
        self.assertContains(res, "updated")
        self.assertContains(res, "deleted")


class LanguageFullListViewTest(TestCase):
    """
    Test full Language list page
    """

    fixtures = ["test.json"]

    def test_render(self):
        privately_available(self, "full_language_list")

    @as_auth
    def test_query_filtered_count(self):
        res = self.client.get(reverse("full_language_list"))
        self.assertEqual(
            res.context["filtered_tags_count"], len(res.context["tag_list"])
        )

    @as_auth
    def test_query_total_count(self):
        res = self.client.get(reverse("full_language_list"))
        self.assertIsInstance(res.context["available_tags_count"], int)

    @as_auth
    def test_unique(self):
        res = self.client.get(reverse("full_language_list"))
        self.assertTrue(is_list_unique(res.context["tag_list"]))

    @as_auth
    def test_sort(self):
        res = self.client.get(reverse("full_language_list"), data={"ordering": "a"})
        self.assertTrue(res.context["tag_list"].ordered)
        res = self.client.get(reverse("full_language_list"), data={"ordering": "n_dsc"})
        self.assertTrue(res.context["tag_list"].ordered)
        res = self.client.get(reverse("full_language_list"), data={"ordering": "n_asc"})
        self.assertTrue(res.context["tag_list"].ordered)


class CreateLanguageViewTest(TestCase):
    fixtures = ["test.json"]

    def test_render(self):
        privately_available(self, "language_create")

    @as_auth
    def test_post(self):
        res = self.client.post(
            reverse("language_create"), data={"title": "foo"}, follow=True
        )
        self.assertContains(res, "created")
        self.assertTrue(Language.objects.filter(title="foo").exists())


class EditLanguageViewTest(TestCase):
    fixtures = ["test.json"]

    def test_render(self):
        privately_available(self, "language_edit", kwargs={"pk": 1})

    @as_auth
    def test_post(self):
        res = self.client.post(
            reverse("language_edit", kwargs={"pk": 1}),
            data={"title": "buzz"},
            follow=True,
        )
        self.assertContains(res, "updated")
        self.assertTrue(Language.objects.filter(title="buzz").exists())


class DeleteLanguageViewTest(TestCase):
    fixtures = ["test.json"]

    def test_render(self):
        privately_available(self, "language_delete", kwargs={"pk": 1})

    @as_auth
    def test_post(self):
        res = self.client.post(
            reverse("language_delete", kwargs={"pk": 1}), follow=True
        )
        self.assertFalse(Language.objects.filter(pk=1).exists())


class LanguageMergeViewTest(TestCase):
    fixtures = ["test.json"]

    def test_render(self):
        privately_available(self, "language_merge", kwargs={"language_id": 1})

    @as_auth
    def test_404(self):
        res = self.client.get(
            reverse("language_merge", kwargs={"language_id": 100}), follow=True
        )
        self.assertEqual(res.status_code, 404)

    @as_auth
    def test_post(self):
        res = self.client.post(
            reverse("language_merge", kwargs={"language_id": 1}),
            data={"into": 2},
            follow=True,
        )
        expected_redirect = reverse("language_edit", kwargs={"pk": 2})
        self.assertRedirects(res, expected_redirect)
        self.assertFalse(Language.objects.filter(pk=1).exists())
        self.assertContains(res, "updated")
        self.assertContains(res, "deleted")

    @as_auth
    def test_invalid_language(self):
        res = self.client.post(
            reverse("language_merge", kwargs={"language_id": 1}),
            data={"into": 1},
            follow=True,
        )
        expected_redirect = reverse("language_merge", kwargs={"language_id": 1})
        self.assertRedirects(res, expected_redirect)
        self.assertContains(res, "You cannot merge a language into itself")


class DisciplineFullListViewTest(TestCase):
    """
    Test full Discipline list page
    """

    fixtures = ["test.json"]

    def test_render(self):
        privately_available(self, "full_discipline_list")

    @as_auth
    def test_query_filtered_count(self):
        res = self.client.get(reverse("full_discipline_list"))
        self.assertEqual(
            res.context["filtered_tags_count"], len(res.context["tag_list"])
        )

    @as_auth
    def test_query_total_count(self):
        res = self.client.get(reverse("full_discipline_list"))
        self.assertIsInstance(res.context["available_tags_count"], int)

    @as_auth
    def test_unique(self):
        res = self.client.get(reverse("full_discipline_list"))
        self.assertTrue(is_list_unique(res.context["tag_list"]))

    @as_auth
    def test_sort(self):
        res = self.client.get(reverse("full_discipline_list"), data={"ordering": "a"})
        self.assertTrue(res.context["tag_list"].ordered)
        res = self.client.get(
            reverse("full_discipline_list"), data={"ordering": "n_dsc"}
        )
        self.assertTrue(res.context["tag_list"].ordered)
        res = self.client.get(
            reverse("full_discipline_list"), data={"ordering": "n_asc"}
        )
        self.assertTrue(res.context["tag_list"].ordered)


class CreateDisciplineViewTest(TestCase):
    fixtures = ["test.json"]

    def test_render(self):
        privately_available(self, "discipline_create")

    @as_auth
    def test_post(self):
        res = self.client.post(
            reverse("discipline_create"), data={"title": "foo"}, follow=True
        )
        self.assertContains(res, "created")
        self.assertTrue(Discipline.objects.filter(title="foo").exists())


class EditDisciplineViewTest(TestCase):
    fixtures = ["test.json"]

    def test_render(self):
        privately_available(self, "discipline_edit", kwargs={"pk": 1})

    @as_auth
    def test_post(self):
        res = self.client.post(
            reverse("discipline_edit", kwargs={"pk": 1}),
            data={"title": "buzz"},
            follow=True,
        )
        self.assertContains(res, "updated")
        self.assertTrue(Discipline.objects.filter(title="buzz").exists())


class DeleteDisciplineViewTest(TestCase):
    fixtures = ["test.json"]

    def test_render(self):
        privately_available(self, "discipline_delete", kwargs={"pk": 1})

    @as_auth
    def test_post(self):
        res = self.client.post(
            reverse("discipline_delete", kwargs={"pk": 1}), follow=True
        )
        self.assertFalse(Discipline.objects.filter(pk=1).exists())


class DisciplineMergeViewTest(TestCase):
    fixtures = ["test.json"]

    def test_render(self):
        privately_available(self, "discipline_merge", kwargs={"discipline_id": 1})

    @as_auth
    def test_404(self):
        res = self.client.get(
            reverse("discipline_merge", kwargs={"discipline_id": 100}), follow=True
        )
        self.assertEqual(res.status_code, 404)

    @as_auth
    def test_post(self):
        res = self.client.post(
            reverse("discipline_merge", kwargs={"discipline_id": 1}),
            data={"into": 2},
            follow=True,
        )
        expected_redirect = reverse("discipline_edit", kwargs={"pk": 2})
        self.assertRedirects(res, expected_redirect)
        self.assertFalse(Discipline.objects.filter(pk=1).exists())
        self.assertContains(res, "updated")
        self.assertContains(res, "deleted")

    @as_auth
    def test_invalid_discipline(self):
        res = self.client.post(
            reverse("discipline_merge", kwargs={"discipline_id": 1}),
            data={"into": 1},
            follow=True,
        )
        expected_redirect = reverse("discipline_merge", kwargs={"discipline_id": 1})
        self.assertRedirects(res, expected_redirect)
        self.assertContains(res, "You cannot merge a discipline into itself")


class WorkTypeFullListViewTest(TestCase):
    """
    Test full WorkType list page
    """

    fixtures = ["test.json"]

    def test_render(self):
        privately_available(self, "full_work_type_list")

    @as_auth
    def test_query_filtered_count(self):
        res = self.client.get(reverse("full_work_type_list"))
        self.assertEqual(
            res.context["filtered_tags_count"], len(res.context["tag_list"])
        )

    @as_auth
    def test_query_total_count(self):
        res = self.client.get(reverse("full_work_type_list"))
        self.assertIsInstance(res.context["available_tags_count"], int)

    @as_auth
    def test_unique(self):
        res = self.client.get(reverse("full_work_type_list"))
        self.assertTrue(is_list_unique(res.context["tag_list"]))

    @as_auth
    def test_sort(self):
        res = self.client.get(reverse("full_work_type_list"), data={"ordering": "a"})
        self.assertTrue(res.context["tag_list"].ordered)
        res = self.client.get(
            reverse("full_work_type_list"), data={"ordering": "n_dsc"}
        )
        self.assertTrue(res.context["tag_list"].ordered)
        res = self.client.get(
            reverse("full_work_type_list"), data={"ordering": "n_asc"}
        )
        self.assertTrue(res.context["tag_list"].ordered)


class CreateWorkTypeViewTest(TestCase):
    fixtures = ["test.json"]

    def test_render(self):
        privately_available(self, "work_type_create")

    @as_auth
    def test_post(self):
        res = self.client.post(
            reverse("work_type_create"), data={"title": "foo"}, follow=True
        )
        self.assertContains(res, "created")
        self.assertTrue(WorkType.objects.filter(title="foo").exists())


class EditWorkTypeViewTest(TestCase):
    fixtures = ["test.json"]

    def test_render(self):
        privately_available(self, "work_type_edit", kwargs={"pk": 1})

    @as_auth
    def test_post(self):
        res = self.client.post(
            reverse("work_type_edit", kwargs={"pk": 1}),
            data={"title": "buzz"},
            follow=True,
        )
        self.assertContains(res, "updated")
        self.assertTrue(WorkType.objects.filter(title="buzz").exists())


class DeleteWorkTypeViewTest(TestCase):
    fixtures = ["test.json"]

    def test_render(self):
        privately_available(self, "work_type_delete", kwargs={"pk": 1})

    @as_auth
    def test_post(self):
        res = self.client.post(
            reverse("work_type_delete", kwargs={"pk": 1}), follow=True
        )
        self.assertFalse(WorkType.objects.filter(pk=1).exists())


class WorkTypeMergeViewTest(TestCase):
    fixtures = ["test.json"]

    def test_render(self):
        privately_available(self, "work_type_merge", kwargs={"work_type_id": 1})

    @as_auth
    def test_404(self):
        res = self.client.get(
            reverse("work_type_merge", kwargs={"work_type_id": 100}), follow=True
        )
        self.assertEqual(res.status_code, 404)

    @as_auth
    def test_post(self):
        res = self.client.post(
            reverse("work_type_merge", kwargs={"work_type_id": 1}),
            data={"into": 2},
            follow=True,
        )
        expected_redirect = reverse("work_type_edit", kwargs={"pk": 2})
        self.assertRedirects(res, expected_redirect)
        self.assertFalse(WorkType.objects.filter(pk=1).exists())
        self.assertContains(res, "updated")
        self.assertContains(res, "deleted")

    @as_auth
    def test_invalid_work_type(self):
        res = self.client.post(
            reverse("work_type_merge", kwargs={"work_type_id": 1}),
            data={"into": 1},
            follow=True,
        )
        expected_redirect = reverse("work_type_merge", kwargs={"work_type_id": 1})
        self.assertRedirects(res, expected_redirect)
        self.assertContains(res, "You cannot merge a work_type into itself")


class GenderFullListViewTest(TestCase):
    """
    Test full Gender list page
    """

    fixtures = ["test.json"]

    def test_render(self):
        privately_available(self, "full_gender_list")

    @as_auth
    def test_query_filtered_count(self):
        res = self.client.get(reverse("full_gender_list"))
        self.assertEqual(
            res.context["filtered_tags_count"], len(res.context["tag_list"])
        )

    @as_auth
    def test_query_total_count(self):
        res = self.client.get(reverse("full_gender_list"))
        self.assertIsInstance(res.context["available_tags_count"], int)

    @as_auth
    def test_unique(self):
        res = self.client.get(reverse("full_gender_list"))
        self.assertTrue(is_list_unique(res.context["tag_list"]))

    @as_auth
    def test_sort(self):
        res = self.client.get(reverse("full_gender_list"), data={"ordering": "a"})
        self.assertTrue(res.context["tag_list"].ordered)
        res = self.client.get(reverse("full_gender_list"), data={"ordering": "n_dsc"})
        self.assertTrue(res.context["tag_list"].ordered)
        res = self.client.get(reverse("full_gender_list"), data={"ordering": "n_asc"})
        self.assertTrue(res.context["tag_list"].ordered)


class CreateGenderViewTest(TestCase):
    fixtures = ["test.json"]

    def test_render(self):
        privately_available(self, "gender_create")

    @as_auth
    def test_post(self):
        res = self.client.post(
            reverse("gender_create"), data={"gender": "red"}, follow=True
        )
        self.assertContains(res, "created")
        self.assertTrue(Gender.objects.filter(gender="red").exists())


class EditGenderViewTest(TestCase):
    fixtures = ["test.json"]

    def test_render(self):
        privately_available(self, "gender_edit", kwargs={"pk": 1})

    @as_auth
    def test_post(self):
        res = self.client.post(
            reverse("gender_edit", kwargs={"pk": 1}),
            data={"gender": "blue"},
            follow=True,
        )
        self.assertContains(res, "updated")
        self.assertTrue(Gender.objects.filter(gender="blue").exists())


class DeleteGenderViewTest(TestCase):
    fixtures = ["test.json"]

    def test_render(self):
        privately_available(self, "gender_delete", kwargs={"pk": 1})

    @as_auth
    def test_post(self):
        res = self.client.post(reverse("gender_delete", kwargs={"pk": 1}), follow=True)
        self.assertFalse(Gender.objects.filter(pk=1).exists())


class GenderMergeViewTest(TestCase):
    fixtures = ["test.json"]

    def test_render(self):
        privately_available(self, "gender_merge", kwargs={"gender_id": 1})

    @as_auth
    def test_404(self):
        res = self.client.get(
            reverse("gender_merge", kwargs={"gender_id": 100}), follow=True
        )
        self.assertEqual(res.status_code, 404)

    @as_auth
    def test_post(self):
        res = self.client.post(
            reverse("gender_merge", kwargs={"gender_id": 1}),
            data={"into": 2},
            follow=True,
        )
        expected_redirect = reverse("gender_edit", kwargs={"pk": 2})
        self.assertRedirects(res, expected_redirect)
        self.assertFalse(Gender.objects.filter(pk=1).exists())
        self.assertContains(res, "updated")
        self.assertContains(res, "deleted")

    @as_auth
    def test_invalid_gender(self):
        res = self.client.post(
            reverse("gender_merge", kwargs={"gender_id": 1}),
            data={"into": 1},
            follow=True,
        )
        expected_redirect = reverse("gender_merge", kwargs={"gender_id": 1})
        self.assertRedirects(res, expected_redirect)
        self.assertContains(res, "You cannot merge a gender into itself")
