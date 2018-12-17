from django.test import TestCase
from django.urls import reverse

from .models import ConferenceSeries, Conference, Organizer, SeriesMembership


class EmptyTest(TestCase):
    """
    Test pages when the database is empty
    """

    def test_no_series(self):
        """
        If no series exist, display appropriate message
        """

        response = self.client.get(reverse("series_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "There are no series")
        self.assertQuerysetEqual(response.context["series_list"], [])

    def test_no_conference(self):
        """
        If no conferences exist, display appropriate message
        """

        response = self.client.get(reverse("conference_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "There are no conferences")
        self.assertQuerysetEqual(response.context["conference_list"], [])


class AbstractsTest(TestCase):
    def setUp(self):
        """
        Build minimal databae with examples
        """
        # Establish series
        self.series1 = ConferenceSeries.objects.create(
            title="foobar", notes="A premier conference on foobar."
        )
        self.series2 = ConferenceSeries.objects.create(
            title="bazbat", notes="The international BazBat society."
        )

        # Establish organizers
        self.organizer1 = Organizer.objects.create(name="Susan")
        self.organizer2 = Organizer.objects.create(name="Bob")

        # Establish conferences
        self.conference1 = Conference.objects.create(
            year=1970,
            venue="Los Angeles",
            notes="Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum. Donec elementum ligula eu sapien consequat eleifend. Donec nec dolor erat, condimentum sagittis sem. Praesent porttitor porttitor risus, dapibus rutrum ipsum gravida et. Integer lectus nisi, facilisis",
        )

        self.conference2 = Conference.objects.create(
            year=1971,
            venue="Berlin",
            notes="Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud",
        )

        self.series_membership1 = SeriesMembership.objects.create(
            series=self.series1, conference=self.conference1, number=1
        )
        self.series_membership2 = SeriesMembership.objects.create(
            series=self.series1, conference=self.conference2, number=2
        )
        self.series_membership2 = SeriesMembership.objects.create(
            series=self.series2, conference=self.conference2, number=1
        )

        self.conference1.organizers.add(self.organizer1)
        self.conference2.organizers.add(self.organizer1)
        self.conference2.organizers.add(self.organizer2)

    def test_series_list(self):
        """
        If series exist, display series names with links
        """
        response = self.client.get(reverse("series_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.series1.title)
        self.assertContains(response, reverse("series_detail", args=[self.series1.id]))
        self.assertContains(response, self.series2.title)
        self.assertContains(response, reverse("series_detail", args=[self.series2.id]))

    def test_series_detail(self):
        response = self.client.get(reverse("series_detail", args=[self.series1.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.conference1.venue)
        self.assertContains(response, self.conference1.year)
        self.assertContains(
            response, reverse("conference_detail", args=[self.conference1.id])
        )
        self.assertContains(response, self.series1.notes)

    def test_conference_list(self):
        """
        If conference exist, display conference names with links
        """
        response = self.client.get(reverse("conference_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.conference1.venue)
        self.assertContains(response, self.conference1.year)
        self.assertContains(
            response, reverse("conference_detail", args=[self.conference1.id])
        )

    def test_string_representations(self):
        self.assertEqual(str(self.conference1), "1970 - Los Angeles")
