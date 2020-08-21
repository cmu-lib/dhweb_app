from django.core.management.base import BaseCommand
from abstracts import models
from urllib import request
from urllib.error import HTTPError
import math
from time import sleep


class BackOff:
    """
    A simple counter to track an exponential backoff timer
    """

    def __init__(self, initial, exponent=2):
        self.initial = initial
        self.exponent = exponent
        self.timer = self.initial

    def get_time(self):
        return self.timer

    def increase_time(self):
        self.timer = self.timer ** self.exponent
        print(f"Increasing time to {self.timer}")

    def reduce_time(self):
        reduced_time = math.sqrt(self.timer)
        if reduced_time >= self.initial:
            self.timer = reduced_time
        else:
            self.timer = self.initial
        print(f"Reducing time to {self.timer}")


def get_all_paths():
    works = [w.get_absolute_url() for w in models.Work.objects.all()]
    authors = [w.get_absolute_url() for w in models.Author.objects.all()]
    conference_series = [
        w.get_absolute_url() for w in models.ConferenceSeries.objects.all()
    ]
    conferences = [f"/works?conference={c.id}" for c in models.Conference.objects.all()]
    manual = ["/", "/about", "/cv", "/colophon", "/project_team", "/downloads"]

    return works + authors + conference_series + conferences + manual


def attempt_url(path, backoff):
    sleep(backoff.get_time())
    try:
        res = request.urlopen(
            f"https://web.archive.org/save/https://dh-abstracts.library.cmu.edu{path}"
        )
        backoff.increase_time()
        print(f"{res.status}: {path}")
        return
    except HTTPError as err:
        if err.code == 429:
            backoff.increase_time()
            attempt_url(path, backoff)
        else:
            print(f"{err.code}! {path}")
            return


class Command(BaseCommand):
    help = "Submit site pages to Internet Archive"

    def handle(self, *args, **options):
        all_paths = get_all_paths()

        backoff = BackOff(initial=3)

        for path in all_paths:
            attempt_url(path, backoff)
