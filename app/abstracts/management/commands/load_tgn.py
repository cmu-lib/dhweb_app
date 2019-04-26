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
from abstracts.models import Country, CountryLabel


class Command(BaseCommand):
    def handle(self, *args, **options):
        with open("/vol/data/json/tgn.json", "r") as js_file:
            cj = json.loads(js_file.read())
            for c in cj["results"]["bindings"]:
                new_label = CountryLabel.objects.get_or_create(
                    name=c["name_label"]["value"],
                    pref_name = c["pref_literal"]["value"],
                    tgn_id = c["country"]["value"],
                    )
            for cn in Country.objects.all():
                candidate_label = CountryLabel.objects.filter(name=cn.name).first()
                if candidate_label is not None:
                    labels_to_associate = CountryLabel.objects.filter(tgn_id=candidate_label.tgn_id).all()
                    print(f"Matching {labels_to_associate.count()} with {cn}")
                    cn.pref_name = candidate_label.pref_name
                    cn.tgn_id = candidate_label.tgn_id
                    cn.save()
                    labels_to_associate.update(country=cn)

            for unmatched_label in CountryLabel.objects.filter(country__isnull=True).all():
                target_country = Country.objects.get_or_create(
                    name = unmatched_label.pref_name,
                    tgn_id = unmatched_label.tgn_id,
                    pref_name = unmatched_label.pref_name,
                )[0]
                print(f"Matching {target_country} to {unmatched_label}")
                unmatched_label.country = target_country
                unmatched_label.save()
