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

    def test_all_accepted(self):
        res = self.client.get(reverse("author_list"))
        for author in res.context["author_list"]:
            self.assertGreaterEqual(author.works.filter(state="ac").count(), 1)


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

    def test_only_accepted(self):
        res = self.client.get(reverse("work_list"))
        for work in res.context["work_list"]:
            self.assertEqual(work.state, "ac")


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

    def test_hide_unaccepted_conferences(self):
        res = self.client.get(reverse("conference_list"))
        self.assertNotIn(
            ConferenceSeries.objects.get(pk=2), res.context["conference_list"]
        )

    def test_has_unaffiliated_conferences(self):
        res = self.client.get(reverse("conference_list"))
        self.assertIn(
            Conference.objects.filter(series__isnull=True, works__state="ac").first(),
            res.context["standalone_conferences"],
        )


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


class EditConferenceViewTest(TestCase):
    fixtures = ["test.json"]

    def test_render(self):
        privately_available(self, "conference_edit", kwargs={"pk": 1})

    @as_auth
    def test_post(self):
        res = self.client.post(
            reverse("conference_edit", kwargs={"pk": 1}),
            data={
                "year": 1987,
                "venue": "foo",
                "venue_abbreviation": "bar",
                "notes": "buzz",
            },
            follow=True,
        )
        self.assertContains(res, "updated")


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
        self.assertContains(res, "updated")


class DeleteWorkViewTest(TestCase):
    fixtures = ["test.json"]

    def test_render(self):
        privately_available(self, "work_delete", kwargs={"pk": 1})

    @as_auth
    def test_post(self):
        res = self.client.post(reverse("work_delete", kwargs={"pk": 1}), follow=True)
        self.assertFalse(Work.objects.filter(pk=1).exists())


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

