from django.test import TestCase
from django.urls import reverse

from .models import ConferenceSeries, Conference, Organizer, SeriesMembership

class SeriesIndexViewTests(TestCase):
  def test_no_series(self):
    """
    If no series exist, display appropriate message
    """

    response = self.client.get(reverse("series_list"))
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, "There are no series")
    self.assertQuerysetEqual(response.context['series_list'], [])

  def test_add_series(self):
    """
    If series exist, display series names with links
    """
    s1 = ConferenceSeries.objects.create(title="foobar")

    response = self.client.get(reverse("series_list"))
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, s1.title)

  def test_conf_string_representation(self):
    s1 = ConferenceSeries.objects.create(title="foobar")
    self.assertEqual(str(s1), "foobar")

class SeriesDetailViewTests(TestCase):

  def test_add_conference(self):

    c1 = Conference.objects.create(
        year=1970,
        venue="Los Angeles",
        notes="lorem ipsum")

    s1 = ConferenceSeries.objects.create(title="foobar")
    o1 = Organizer.objects.create(name="Susan")

    sm1 = SeriesMembership.objects.create(
        series=s1, conference=c1, number=17)

    c1.organizers.add(o1)

    response = self.client.get(reverse("series_detail", args=(s1.id,)))
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, "Los Angeles")
    self.assertContains(response, "1970")
