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


def publicly_available(testcase, viewname):
    res = testcase.client.get(reverse("home_view"))
    testcase.assertEqual(res.status_code, 200)


def privately_available(testcase, viewname):
    target_url = reverse(viewname)
    redirected_url = f"{reverse('login')}?next={target_url}"
    res = testcase.client.get(target_url, follow=True)
    testcase.assertRedirects(res, redirected_url)
    testcase.client.login(username="root", password="dh-abstracts")
    auth_res = testcase.client.get(target_url)
    testcase.assertEqual(auth_res.status_code, 200)


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


class AuthorFullListViewTest(TestCase):
    """
    Test full Author list page
    """

    fixtures = ["test.json"]

    def test_render(self):
        target_url = reverse("full_author_list")
        redirected_url = f"{reverse('login')}?next={target_url}"
        full_author_list_response = self.client.get(target_url, follow=True)
        self.assertRedirects(full_author_list_response, redirected_url)

    def test_auth_render(self):
        self.client.login(username="root", password="dh-abstracts")
        auth_full_author_list_response = self.client.get(reverse("full_author_list"))
        self.assertEqual(auth_full_author_list_response.status_code, 200)

    def test_query_filtered_count(self):
        self.client.login(username="root", password="dh-abstracts")
        full_author_list_response = self.client.get(reverse("full_author_list"))
        self.assertEqual(
            full_author_list_response.context["filtered_authors_count"],
            len(full_author_list_response.context["author_list"]),
        )

    def test_query_total_count(self):
        self.client.login(username="root", password="dh-abstracts")
        full_author_list_response = self.client.get(reverse("full_author_list"))
        self.assertIsInstance(
            full_author_list_response.context["available_authors_count"], int
        )

    def test_unique(self):
        self.client.login(username="root", password="dh-abstracts")
        full_author_list_response = self.client.get(reverse("full_author_list"))
        self.assertTrue(
            is_list_unique(full_author_list_response.context["author_list"])
        )


class WorkFullListViewTest(TestCase):
    """
    Test full Work list page
    """

    fixtures = ["test.json"]

    def test_render(self):
        target_url = reverse("full_work_list")
        redirected_url = f"{reverse('login')}?next={target_url}"
        full_work_list_response = self.client.get(target_url, follow=True)
        self.assertRedirects(full_work_list_response, redirected_url)

    def test_auth_render(self):
        self.client.login(username="root", password="dh-abstracts")
        auth_full_work_list_response = self.client.get(reverse("full_work_list"))
        self.assertEqual(auth_full_work_list_response.status_code, 200)

    def test_query_filtered_count(self):
        self.client.login(username="root", password="dh-abstracts")
        full_work_list_response = self.client.get(reverse("full_work_list"))
        self.assertEqual(
            full_work_list_response.context["filtered_works_count"],
            len(full_work_list_response.context["work_list"]),
        )

    def test_query_total_count(self):
        self.client.login(username="root", password="dh-abstracts")
        full_work_list_response = self.client.get(reverse("full_work_list"))
        self.assertIsInstance(
            full_work_list_response.context["available_works_count"], int
        )

    def test_unique(self):
        self.client.login(username="root", password="dh-abstracts")
        full_work_list_response = self.client.get(reverse("full_work_list"))
        self.assertTrue(is_list_unique(full_work_list_response.context["work_list"]))


class InstitutionFullListViewTest(TestCase):
    """
    Test full Institution list page
    """

    fixtures = ["test.json"]

    def test_render(self):
        target_url = reverse("full_institution_list")
        redirected_url = f"{reverse('login')}?next={target_url}"
        full_institution_list_response = self.client.get(target_url, follow=True)
        self.assertRedirects(full_institution_list_response, redirected_url)

    def test_auth_render(self):
        self.client.login(username="root", password="dh-abstracts")
        auth_full_institution_list_response = self.client.get(
            reverse("full_institution_list")
        )
        self.assertEqual(auth_full_institution_list_response.status_code, 200)

    def test_query_filtered_count(self):
        self.client.login(username="root", password="dh-abstracts")
        full_institution_list_response = self.client.get(
            reverse("full_institution_list")
        )
        self.assertEqual(
            full_institution_list_response.context["filtered_institutions_count"],
            len(full_institution_list_response.context["institution_list"]),
        )

    def test_query_total_count(self):
        self.client.login(username="root", password="dh-abstracts")
        full_institution_list_response = self.client.get(
            reverse("full_institution_list")
        )
        self.assertIsInstance(
            full_institution_list_response.context["available_institutions_count"], int
        )

    def test_unique(self):
        self.client.login(username="root", password="dh-abstracts")
        full_institution_list_response = self.client.get(
            reverse("full_institution_list")
        )
        self.assertTrue(
            is_list_unique(full_institution_list_response.context["institution_list"])
        )


class AuthorDetailViewTest(TestCase):
    """
    Test Author detail page
    """

    fixtures = ["test.json"]

    def test_render(self):
        author_detail_response = self.client.get(
            reverse("author_detail", kwargs={"author_id": 1})
        )
        self.assertEqual(author_detail_response.status_code, 200)

    def test_404(self):
        author_detail_response = self.client.get(
            reverse("author_detail", kwargs={"author_id": 100})
        )
        self.assertEqual(author_detail_response.status_code, 404)

    def test_works_unqiue_in_series(self):
        author_detail_response = self.client.get(
            reverse("author_detail", kwargs={"author_id": 1})
        )
        for series in author_detail_response.context["split_works"]:
            self.assertTrue(is_list_unique(series["works"]))

    def test_appellations_unique(self):
        author_detail_response = self.client.get(
            reverse("author_detail", kwargs={"author_id": 1})
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
            reverse("author_detail", kwargs={"author_id": 1})
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
            reverse("author_detail", kwargs={"author_id": 1})
        )
        for assertion in author_detail_response.context["affiliation_assertions"]:
            self.assertGreaterEqual(len(assertion["works"]), 1)
            self.assertTrue(is_list_unique(assertion["works"]))

    def test_unaccepted_author(self):
        """
        Authors with only submitted papers should redirect with errors
        """
        unaccepted_author_detail_response = self.client.get(
            reverse("author_detail", kwargs={"author_id": 3}), follow=True
        )
        self.assertRedirects(unaccepted_author_detail_response, reverse("author_list"))
        self.assertGreaterEqual(
            len(unaccepted_author_detail_response.context["messages"]), 1
        )


class WorkListViewTest(TestCase):
    """
    Test Work list page
    """

    fixtures = ["test.json"]

    def test_render(self):
        work_list_response = self.client.get(reverse("work_list"))
        self.assertEqual(work_list_response.status_code, 200)

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
        work_detail_response = self.client.get(
            reverse("work_detail", kwargs={"work_id": 1})
        )
        self.assertEqual(work_detail_response.status_code, 200)

    def test_404(self):
        work_detail_response = self.client.get(
            reverse("work_detail", kwargs={"work_id": 100})
        )
        self.assertEqual(work_detail_response.status_code, 404)

    def test_is_work(self):
        work_detail_response = self.client.get(
            reverse("work_detail", kwargs={"work_id": 1})
        )
        self.assertIsInstance(work_detail_response.context["work"], Work)

    def test_authorships_unique(self):
        work_detail_response = self.client.get(
            reverse("work_detail", kwargs={"work_id": 1})
        )
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

    def test_has_unaffiliated_conferences(self):
        conference_list_response = self.client.get(reverse("conference_list"))
        self.assertIn(
            Conference.objects.filter(series__isnull=True, works__state="ac").first(),
            conference_list_response.context["standalone_conferences"],
        )


class AuthorMergeViewTest(TestCase):
    fixtures = ["test.json"]

    def test_render(self):
        target_url = reverse("author_merge", kwargs={"author_id": 1})
        redirected_url = f"{reverse('login')}?next={target_url}"
        merge_response = self.client.get(target_url, follow=True)
        self.assertRedirects(merge_response, redirected_url)

    def test_auth_render(self):
        self.client.login(username="root", password="dh-abstracts")
        auth_merge_response = self.client.get(
            reverse("author_merge", kwargs={"author_id": 1})
        )
        self.assertEqual(auth_merge_response.status_code, 200)

    def test_404(self):
        self.client.login(username="root", password="dh-abstracts")
        auth_merge_response = self.client.get(
            reverse("author_merge", kwargs={"author_id": 100}), follow=True
        )
        self.assertEqual(auth_merge_response.status_code, 404)

    def test_post(self):
        self.client.login(username="root", password="dh-abstracts")
        post_response = self.client.post(
            reverse("author_merge", kwargs={"author_id": 1}),
            data={"into": 2},
            follow=True,
        )
        expected_redirect = reverse("author_detail", kwargs={"author_id": 2})
        self.assertRedirects(post_response, expected_redirect)
        self.assertFalse(Author.objects.filter(pk=1).exists())
        self.assertContains(post_response, "updated")
        self.assertContains(post_response, "deleted")

    def test_invalid_author(self):
        self.client.login(username="root", password="dh-abstracts")
        post_response = self.client.post(
            reverse("author_merge", kwargs={"author_id": 1}),
            data={"into": 1},
            follow=True,
        )
        expected_redirect = reverse("author_merge", kwargs={"author_id": 1})
        self.assertRedirects(post_response, expected_redirect)
        self.assertContains(post_response, "You cannot merge an author into themselves")


class InstitutionMergeViewTest(TestCase):
    fixtures = ["test.json"]

    def test_render(self):
        target_url = reverse("institution_merge", kwargs={"institution_id": 1})
        redirected_url = f"{reverse('login')}?next={target_url}"
        merge_response = self.client.get(target_url, follow=True)
        self.assertRedirects(merge_response, redirected_url)

    def test_auth_render(self):
        self.client.login(username="root", password="dh-abstracts")
        auth_merge_response = self.client.get(
            reverse("institution_merge", kwargs={"institution_id": 1})
        )
        self.assertEqual(auth_merge_response.status_code, 200)

    def test_404(self):
        self.client.login(username="root", password="dh-abstracts")
        auth_merge_response = self.client.get(
            reverse("institution_merge", kwargs={"institution_id": 100}), follow=True
        )
        self.assertEqual(auth_merge_response.status_code, 404)

    def test_post(self):
        self.client.login(username="root", password="dh-abstracts")
        post_response = self.client.post(
            reverse("institution_merge", kwargs={"institution_id": 1}),
            data={"into": 2},
            follow=True,
        )
        expected_redirect = reverse("institution_edit", kwargs={"pk": 2})
        self.assertRedirects(post_response, expected_redirect)
        self.assertFalse(Institution.objects.filter(pk=1).exists())
        self.assertContains(post_response, "updated")

    def test_invalid_institution(self):
        self.client.login(username="root", password="dh-abstracts")
        post_response = self.client.post(
            reverse("institution_merge", kwargs={"institution_id": 1}),
            data={"into": 1},
            follow=True,
        )
        expected_redirect = reverse("institution_merge", kwargs={"institution_id": 1})
        self.assertRedirects(post_response, expected_redirect)
        self.assertContains(
            post_response, "You cannot merge an institution into itself"
        )


class AffiliationMergeViewTest(TestCase):
    fixtures = ["test.json"]

    def test_render(self):
        target_url = reverse("affiliation_merge", kwargs={"affiliation_id": 1})
        redirected_url = f"{reverse('login')}?next={target_url}"
        merge_response = self.client.get(target_url, follow=True)
        self.assertRedirects(merge_response, redirected_url)

    def test_auth_render(self):
        self.client.login(username="root", password="dh-abstracts")
        auth_merge_response = self.client.get(
            reverse("affiliation_merge", kwargs={"affiliation_id": 1})
        )
        self.assertEqual(auth_merge_response.status_code, 200)

    def test_404(self):
        self.client.login(username="root", password="dh-abstracts")
        auth_merge_response = self.client.get(
            reverse("affiliation_merge", kwargs={"affiliation_id": 100}), follow=True
        )
        self.assertEqual(auth_merge_response.status_code, 404)

    def test_post(self):
        self.client.login(username="root", password="dh-abstracts")
        post_response = self.client.post(
            reverse("affiliation_merge", kwargs={"affiliation_id": 1}),
            data={"into": 2},
            follow=True,
        )
        expected_redirect = reverse("affiliation_edit", kwargs={"pk": 2})
        self.assertRedirects(post_response, expected_redirect)
        self.assertFalse(Affiliation.objects.filter(pk=1).exists())
        self.assertContains(post_response, "updated")

    def test_invalid_affiliation(self):
        self.client.login(username="root", password="dh-abstracts")
        post_response = self.client.post(
            reverse("affiliation_merge", kwargs={"affiliation_id": 1}),
            data={"into": 1},
            follow=True,
        )
        expected_redirect = reverse("affiliation_merge", kwargs={"affiliation_id": 1})
        self.assertRedirects(post_response, expected_redirect)
        self.assertContains(
            post_response, "You cannot merge an affiliation into itself"
        )


class WipeUnusedViewTest(TestCase):
    fixtures = ["test.json"]

    def test_render(self):
        target_url = reverse("wipe_unused")
        redirected_url = f"{reverse('login')}?next={target_url}"
        wipe_unused_response = self.client.get(target_url, follow=True)
        self.assertRedirects(wipe_unused_response, redirected_url)

    def test_auth_render(self):
        self.client.login(username="root", password="dh-abstracts")
        wipe_unused_response = self.client.get(reverse("wipe_unused"))
        self.assertEqual(wipe_unused_response.status_code, 200)

    def test_has_dict(self):
        self.client.login(username="root", password="dh-abstracts")
        wipe_unused_response = self.client.get(reverse("wipe_unused"))
        self.assertIsInstance(wipe_unused_response.context["deletions"], dict)
        self.assertIsInstance(wipe_unused_response.context["hanging_items"], bool)
        self.assertTrue(wipe_unused_response.context["hanging_items"])

    def test_post(self):
        self.client.login(username="root", password="dh-abstracts")
        wipe_unused_response = self.client.post(reverse("wipe_unused"))
        self.assertFalse(wipe_unused_response.context["hanging_items"])


class CreateConferenceViewTest(TestCase):
    fixtures = ["test.json"]

    def test_render(self):
        target_url = reverse("conference_create")
        redirected_url = f"{reverse('login')}?next={target_url}"
        res = self.client.get(target_url, follow=True)
        self.assertRedirects(res, redirected_url)

    def test_auth_render(self):
        self.client.login(username="root", password="dh-abstracts")
        res = self.client.get(reverse("conference_create"))
        self.assertEqual(res.status_code, 200)

    def test_post(self):
        self.client.login(username="root", password="dh-abstracts")
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
        target_url = reverse("conference_edit", kwargs={"pk": 1})
        redirected_url = f"{reverse('login')}?next={target_url}"
        res = self.client.get(target_url, follow=True)
        self.assertRedirects(res, redirected_url)

    def test_auth_render(self):
        self.client.login(username="root", password="dh-abstracts")
        res = self.client.get(reverse("conference_edit", kwargs={"pk": 1}))
        self.assertEqual(res.status_code, 200)

    def test_post(self):
        self.client.login(username="root", password="dh-abstracts")
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
        target_url = reverse("series_create")
        redirected_url = f"{reverse('login')}?next={target_url}"
        res = self.client.get(target_url, follow=True)
        self.assertRedirects(res, redirected_url)

    def test_auth_render(self):
        self.client.login(username="root", password="dh-abstracts")
        res = self.client.get(reverse("series_create"))
        self.assertEqual(res.status_code, 200)

    def test_post(self):
        self.client.login(username="root", password="dh-abstracts")
        res = self.client.post(
            reverse("series_create"),
            data={"title": "foo", "abbreviation": "bar", "notes": "buzz"},
            follow=True,
        )
        self.assertContains(res, "created")


class EditSeriesViewTest(TestCase):
    fixtures = ["test.json"]

    def test_render(self):
        target_url = reverse("series_edit", kwargs={"pk": 1})
        redirected_url = f"{reverse('login')}?next={target_url}"
        res = self.client.get(target_url, follow=True)
        self.assertRedirects(res, redirected_url)

    def test_auth_render(self):
        self.client.login(username="root", password="dh-abstracts")
        res = self.client.get(reverse("series_edit", kwargs={"pk": 1}))
        self.assertEqual(res.status_code, 200)

    def test_post(self):
        self.client.login(username="root", password="dh-abstracts")
        res = self.client.post(
            reverse("series_edit", kwargs={"pk": 1}),
            data={"title": "foo", "abbreviation": "bar", "notes": "buzz"},
            follow=True,
        )
        self.assertContains(res, "updated")


class CreateOrganizerViewTest(TestCase):
    fixtures = ["test.json"]

    def test_render(self):
        target_url = reverse("organizer_create")
        redirected_url = f"{reverse('login')}?next={target_url}"
        res = self.client.get(target_url, follow=True)
        self.assertRedirects(res, redirected_url)

    def test_auth_render(self):
        self.client.login(username="root", password="dh-abstracts")
        res = self.client.get(reverse("organizer_create"))
        self.assertEqual(res.status_code, 200)

    def test_post(self):
        self.client.login(username="root", password="dh-abstracts")
        res = self.client.post(
            reverse("organizer_create"),
            data={"title": "foo", "abbreviation": "bar", "notes": "buzz"},
            follow=True,
        )
        self.assertContains(res, "created")


class EditOrganizerViewTest(TestCase):
    fixtures = ["test.json"]

    def test_render(self):
        target_url = reverse("organizer_edit", kwargs={"pk": 1})
        redirected_url = f"{reverse('login')}?next={target_url}"
        res = self.client.get(target_url, follow=True)
        self.assertRedirects(res, redirected_url)

    def test_auth_render(self):
        self.client.login(username="root", password="dh-abstracts")
        res = self.client.get(reverse("organizer_edit", kwargs={"pk": 1}))
        self.assertEqual(res.status_code, 200)

    def test_post(self):
        self.client.login(username="root", password="dh-abstracts")
        res = self.client.post(
            reverse("organizer_edit", kwargs={"pk": 1}),
            data={"title": "foo", "abbreviation": "bar", "notes": "buzz"},
            follow=True,
        )
        self.assertContains(res, "updated")


class DeleteWorkViewTest(TestCase):
    fixtures = ["test.json"]

    def test_render(self):
        target_url = reverse("work_delete", kwargs={"pk": 1})
        redirected_url = f"{reverse('login')}?next={target_url}"
        res = self.client.get(target_url, follow=True)
        self.assertRedirects(res, redirected_url)

    def test_auth_render(self):
        self.client.login(username="root", password="dh-abstracts")
        res = self.client.get(reverse("work_delete", kwargs={"pk": 1}))
        self.assertEqual(res.status_code, 200)

    def test_post(self):
        self.client.login(username="root", password="dh-abstracts")
        res = self.client.post(reverse("work_delete", kwargs={"pk": 1}), follow=True)
        self.assertFalse(Work.objects.filter(pk=1).exists())


class KeywordFullListViewTest(TestCase):
    """
    Test full Keyword list page
    """

    fixtures = ["test.json"]

    def test_render(self):
        target_url = reverse("full_keyword_list")
        redirected_url = f"{reverse('login')}?next={target_url}"
        full_keyword_list_response = self.client.get(target_url, follow=True)
        self.assertRedirects(full_keyword_list_response, redirected_url)

    def test_auth_render(self):
        self.client.login(username="root", password="dh-abstracts")
        auth_full_keyword_list_response = self.client.get(reverse("full_keyword_list"))
        self.assertEqual(auth_full_keyword_list_response.status_code, 200)

    def test_query_filtered_count(self):
        self.client.login(username="root", password="dh-abstracts")
        full_keyword_list_response = self.client.get(reverse("full_keyword_list"))
        self.assertEqual(
            full_keyword_list_response.context["filtered_tags_count"],
            len(full_keyword_list_response.context["tag_list"]),
        )

    def test_query_total_count(self):
        self.client.login(username="root", password="dh-abstracts")
        full_keyword_list_response = self.client.get(reverse("full_keyword_list"))
        self.assertIsInstance(
            full_keyword_list_response.context["available_tags_count"], int
        )

    def test_unique(self):
        self.client.login(username="root", password="dh-abstracts")
        full_keyword_list_response = self.client.get(reverse("full_keyword_list"))
        self.assertTrue(is_list_unique(full_keyword_list_response.context["tag_list"]))


class TopicFullListViewTest(TestCase):
    """
    Test full Topic list page
    """

    fixtures = ["test.json"]

    def test_render(self):
        target_url = reverse("full_topic_list")
        redirected_url = f"{reverse('login')}?next={target_url}"
        full_topic_list_response = self.client.get(target_url, follow=True)
        self.assertRedirects(full_topic_list_response, redirected_url)

    def test_auth_render(self):
        self.client.login(username="root", password="dh-abstracts")
        auth_full_topic_list_response = self.client.get(reverse("full_topic_list"))
        self.assertEqual(auth_full_topic_list_response.status_code, 200)

    def test_query_filtered_count(self):
        self.client.login(username="root", password="dh-abstracts")
        full_topic_list_response = self.client.get(reverse("full_topic_list"))
        self.assertEqual(
            full_topic_list_response.context["filtered_tags_count"],
            len(full_topic_list_response.context["tag_list"]),
        )

    def test_query_total_count(self):
        self.client.login(username="root", password="dh-abstracts")
        full_topic_list_response = self.client.get(reverse("full_topic_list"))
        self.assertIsInstance(
            full_topic_list_response.context["available_tags_count"], int
        )

    def test_unique(self):
        self.client.login(username="root", password="dh-abstracts")
        full_topic_list_response = self.client.get(reverse("full_topic_list"))
        self.assertTrue(is_list_unique(full_topic_list_response.context["tag_list"]))

