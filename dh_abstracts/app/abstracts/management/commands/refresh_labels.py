from django.core.management.base import BaseCommand
from django.conf import settings
from abstracts import models


class Command(BaseCommand):
    help = "Refresh appellation autocomplete field on authors"

    def handle(self, *args, **options):
        for author in models.Author.objects.all():
            print(author.id)
            author.save()
            print(author.appellations_index)
