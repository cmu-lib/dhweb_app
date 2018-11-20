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
    self.assertQuerysetEqual(response.context['series_list'], [])

  def test_no_conference(self):
    """
    If no conferences exist, display appropriate message
    """

    response = self.client.get(reverse("conference_list"))
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, "There are no conferences")
    self.assertQuerysetEqual(response.context['conference_list'], [])

class AbstractsTest(TestCase):
  def setUp(self):
    """
    Build minimal databae with examples
    """
    self.conference1 = Conference.objects.create(
        year=1970,
        venue="Los Angeles",
        notes="lorem ipsum")

    self.conference2 = Conference.objects.create(
        year=1971,
        venue="Berlin",
        notes="dolor lamet")

    self.series1 = ConferenceSeries.objects.create(title="foobar")
    self.series2 = ConferenceSeries.objects.create(title="foobar")

    self.organizer1 = Organizer.objects.create(name="Susan")
    self.organizer2 = Organizer.objects.create(name="Bob")

    self.series_membership1 = SeriesMembership.objects.create(
        series=self.series1, conference=self.conference1, number=1)
    self.series_membership2 = SeriesMembership.objects.create(
        series=self.series1, conference=self.conference2, number=2)
    self.series_membership2 = SeriesMembership.objects.create(
        series=self.series2, conference=self.conference2, number=1)

    self.conference1.organizers.add(self.organizer1)

  def test_series_list(self):
    """
    If series exist, display series names with links
    """
    response = self.client.get(reverse("series_list"))
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, self.series1.title)

  def test_series_detail(self):
    response = self.client.get(reverse("series_detail", args=(self.series1.id,)))
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, "Los Angeles")
    self.assertContains(response, "1970")

  def test_conference_list(self):
    """
    If conference exist, display conference names with links
    """
    response = self.client.get(reverse("conference_list"))
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, self.conference1.venue)

  def test_string_representations(self):
    self.assertEqual(str(self.conference1), "1970 - Los Angeles")
