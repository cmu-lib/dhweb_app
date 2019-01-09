"""
query to vocab.getty.edu/sparql

SELECT DISTINCT ?country ?country_pref ?name ?name_label WHERE {
  ?country gvp:placeTypePreferred aat:300128207 ;
           xl:prefLabel ?country_pref;
           xl:altLabel|xl:prefLabel ?name.
  ?name xl:literalForm ?name_label.
  ?country_pref xl:literalForm ?pref_literal.
  FILTER(lang(?pref_literal)="en")
 }
"""

import json
from django.core.management.base import BaseCommand
from abstracts.models import Country, Nation, NationLabel


class Command(BaseCommand):
    def handle(self, *args, **options):
        with open("xml/sparql.json", "r") as js_file:
            cj = json.loads(js_file.read())
            for c in cj["results"]["bindings"]:
                target_country = Nation.objects.get_or_create(
                    tgn_id=c["country"]["value"]
                )[0]
                new_label = NationLabel(
                    name=c["name_label"]["value"], nation=target_country
                )
                new_label.save()
                if c["country_pref"]["value"] == c["name"]["value"]:
                    target_country.pref_name = new_label
                    target_country.save()

