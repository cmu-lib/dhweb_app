from django.test import TestCase
from django.urls import reverse

from .models import ConferenceSeries

# Create your tests here.

def create_series(series_title):
  """
  Create a dummy series
  """
  return ConferenceSeries.objects.create(title=series_title)

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

    create_series("foobar")
    response = self.client.get(reverse("series_list"))
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, "foobar")
