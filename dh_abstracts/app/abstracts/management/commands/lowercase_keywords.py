from django.core.management.base import BaseCommand
from abstracts import models
from django.db import transaction


class Command(BaseCommand):
    help = "Lowercase keywords and merge them"

    def handle(self, *args, **options):
        for kw in models.Keyword.objects.all():
            newtitle = kw.title.lower().strip()
            kw.title = newtitle
            try:
                kw.save()
            except:
                print(f"merging {newtitle}")
                extant_kw = models.Keyword.objects.get(title=newtitle)
                kw.merge(extant_kw)
