from django.core.management.base import BaseCommand
from abstracts import models
import re
import csv
from django.db import transaction


class Command(BaseCommand):
    help = "One-time load of DH 2020"

    def add_arguments(self, parser):
        pass

    @transaction.atomic
    def handle(self, *args, **options):

        allowed_topics = [
            "English",
            "Contemporary",
            "Europe",
            "North America",
            "20th Century",
            "Global",
            "19th Century",
            "Literary studies",
            "Interface design, development, and analysis",
            "digital libraries creation, management, and analysis",
            "music and sound digitization, encoding, and analysis",
            "manuscripts description, representation, and analysis",
            "database creation, management, and analysis",
            "text encoding and markup language creation, deployment, and analysis",
            "virtual and augmented reality creation, systems, and analysis",
            "annotation structures, systems, and methods",
            "software development, systems, analysis and methods",
            "data publishing projects, systems, and methods",
            "sustainable procedures, systems, and methods",
            "metadata standards, systems, and methods",
            "digital publishing projects, systems, and methods",
            "copyright, licensing, and permissions standards, systems, and processes",
            "Humanities computing",
            "History",
            "scholarly editing and editions development, analysis, and methods",
            "text mining and analysis",
            "Library & information science",
            "18th Century",
            "15th-17th Century",
            "Asia",
            "Computer science",
            "Comparative (2 or more geographical areas)",
            "project design, organization, management",
            "public humanities collaborations and methods",
            "artificial intelligence and machine learning",
            "spatial & spatio-temporal analysis, modeling and visualization",
            "Cultural studies",
            "Education/ pedagogy",
            "cultural analytics",
            "natural language processing",
            "digital archiving",
            "BCE-4th Century",
            "meta-criticism (reflections on digital humanities and humanities computing)",
            "data modeling",
            "Media studies",
            "curricular and pedagogical development and analysis",
            "Book and print history",
            "Linguistics",
            "network analysis and graphs theory and application",
            "Africa",
            "digital research infrastructures development and analysis",
            "digital access, privacy, and ethics analysis",
            "Art history",
            "social media analysis and methods",
            "linked (open) data",
            "South America",
            "Geography and geo-humanities",
            "digital activism and advocacy",
            "Asian studies",
            "information retrieval and querying algorithms and methods",
            "crowdsourcing",
            "First nations and indigenous studies",
            "Informatics",
            "image processing and analysis",
            "Feminist studies",
            "Philology",
            "Musicology",
            "semantic analysis",
            "attribution studies and stylometric analysis",
            "Gender and sexuality studies",
            "bibliographic analysis",
            "electronic literature production and analysis",
            "Spanish",
            "History of science",
            "digitization (2D & 3D)",
            "data, object, and artefact preservation",
            "Design studies",
            "Communication studies",
            "African and African American Studies",
            "Performance Studies: Dance, Theatre",
            "Central/Eastern European Studies",
            "Philosophy",
            "Literacy, composition, and creative writing",
            "Sociology",
            "French",
            "open access methods",
            "digital biography, personography, and prosopography",
            "Translation studies",
            "Theology and religious studies",
            "Law and legal studies",
            "Australia/Oceania",
            "digital ecologies and digital communities creation management and analysis",
            "rhetorical analysis",
            "Galleries and museum studies",
            "Archaeology",
            "physical & minimal computing",
            "Political science",
            "Anthropology",
            "user experience design and analysis",
            "eco-criticism and environmental analysis",
            "Film and cinema arts studies",
            "Environmental, ocean, and waterway studies",
            "Chicano/a/x, Latino/a/x studies",
            "mixed-media analysis",
            "optical character recognition and handwriting recognition",
            "ethnographic analysis",
            "digital art production and analysis",
            "mobile applications development and analysis",
            "Games studies",
            "South Asian studies",
            "systems and information architecture and usability",
            "Cognitive sciences and psychology",
            "concordancing and indexing",
            "Disability and differently-abled studies",
            "Language acquisition",
            "3D printing, critical making",
            "media archaeology",
            "Logic and epistemology",
            "Ethnography and folklore",
            "Transgender and non-binary studies",
            "Statistics",
        ]

        for t in allowed_topics:
            res = models.Topic.objects.get_or_create(title=t)
            print(res)

        with open("/vol/data/metadata_V4.csv", "r") as csvfile:
            reader = csv.DictReader(csvfile)
            adho2020 = models.Conference.objects.get(id=495)
            for work in reader:
                # Get work
                print(work["title_plain"])
                target_work = models.Work.objects.get(
                    conference=adho2020, title=work["title_plain"]
                )
                print(target_work)
                # Check allowed topics
                topics = work["topics"]
                matching_topic_strings = [t for t in allowed_topics if t in topics]
                print(matching_topic_strings)
                # Add matching ones
                if len(matching_topic_strings) < 1:
                    raise
                for t in matching_topic_strings:
                    target_work.topics.add(models.Topic.objects.get(title=t))

