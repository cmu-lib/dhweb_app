import random
from locust import HttpUser, task, between
from faker import Faker
import json

all_ids = json.load(open("../data/all_ids.json", "r"))
fake = Faker()


class QuickstartUser(HttpUser):
    wait_time = between(5, 9)

    @task(10)
    def index_page(self):
        self.client.get("/")
        self.client.get("/conferences")
        self.client.get("/works")
        self.client.get("/authors")
        self.client.get("/pages/about")

    @task(4)
    def view_work(self):
        item_id = random.choice(all_ids["works"])
        self.client.get(f"/works/{item_id}", name="/works")

    @task(4)
    def view_work_pages(self):
        page = random.randint(1, 100)
        self.client.get(f"/works?page={page}", name="/works?page")

    @task(3)
    def view_author(self):
        item_id = random.choice(all_ids["authors"])
        self.client.get(f"/authors/{item_id}", name="/authors")

    @task(4)
    def view_author_pages(self):
        page = random.randint(1, 100)
        self.client.get(f"/authors?page={page}", name="/authors?page")

    @task(4)
    def works_by_conference(self):
        conference_id = random.choice(all_ids["conferences"])
        self.client.get(f"/works?conference={conference_id}", name="/works?conference")

    @task(1)
    def works_by_keyword(self):
        kw_id = random.choice(all_ids["keywords"])
        self.client.get(f"/works?keywords={kw_id}", name="/works?keyword")

    @task(2)
    def works_by_text(self):
        self.client.get(f"/works?text={fake.word()}", name="/works?text")

    @task(2)
    def works_by_affiliation(self):
        aff_id = random.choice(all_ids["affiliations"])
        self.client.get(f"/works?affiliation={aff_id}", name="/works?affiliation")

    @task(2)
    def works_by_author(self):
        author_id = random.choice(all_ids["authors"])
        self.client.get(f"/works?author={author_id}", name="/works?author")

    @task(2)
    def author_by_name(self):
        self.client.get(f"/authors?name={fake.word()}", name="/authors?name")

    @task(2)
    def author_by_institution(self):
        inst_id = random.choice(all_ids["institutions"])
        self.client.get(f"/authors?institution={inst_id}", name="/authors?institution")

    @task(2)
    def author_by_affiliation(self):
        inst_id = random.choice(all_ids["affiliations"])
        self.client.get(f"/authors?affiliation={inst_id}", name="/authors?affiliation")

    @task(4)
    def author_autocomplete(self):
        self.client.get(f"/author-autocomplete", name="/author-autocomplete")

    @task(4)
    def author_autocomplete_q(self):
        self.client.get(
            f"/author-autocomplete?q={fake.random_lowercase_letter()}",
            name="/author-autocomplete?q",
        )

    @task(4)
    def affiliation_autocomplete(self):
        self.client.get(f"/affiliation-autocomplete", name="/affiliation-autocomplete")

    @task(4)
    def affiliation_autocomplete_q(self):
        self.client.get(
            f"/affiliation-autocomplete?q={fake.random_lowercase_letter()}",
            name="/affiliation-autocomplete?q",
        )

    @task(4)
    def institution_autocomplete(self):
        self.client.get(f"/institution-autocomplete", name="/institution-autocomplete")

    @task(4)
    def institution_autocomplete_q(self):
        self.client.get(
            f"/institution-autocomplete?q={fake.random_lowercase_letter()}",
            name="/institution-autocomplete?q",
        )

