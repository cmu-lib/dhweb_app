from django.core.management.base import BaseCommand
from abstracts import models
from django.db import transaction


class Command(BaseCommand):
    help = "Lowercase topics and merge them"

    def handle(self, *args, **options):
        for topic in models.Topic.objects.all():
            newtitle = topic.title.lower().strip()
            topic.title = newtitle
            try:
                topic.save()
            except:
                print(f"merging {newtitle}")
                extant_topic = models.Topic.objects.get(title=newtitle)
                topic.merge(extant_topic)
