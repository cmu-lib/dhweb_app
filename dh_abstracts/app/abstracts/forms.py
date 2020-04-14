from django import forms
from dal.autocomplete import ModelSelect2, ModelSelect2Multiple
from django.forms import formset_factory, inlineformset_factory, modelformset_factory
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit

from .models import (
    Author,
    Authorship,
    Conference,
    Institution,
    Topic,
    Keyword,
    Work,
    WorkType,
    Country,
    Language,
    Discipline,
    License,
    Affiliation,
    SeriesMembership,
    ConferenceSeries,
    Organizer,
)


class WorkFilter(forms.Form):
    text = forms.CharField(max_length=100, strip=True, required=False)
    full_text_available = forms.BooleanField(required=False)
    work_type = forms.ModelChoiceField(
        queryset=WorkType.objects.distinct(), required=False
    )
    conference = forms.ModelChoiceField(
        queryset=Conference.objects.all().prefetch_related("organizers"),
        required=False,
        help_text="Works submitted to a particular conference",
    )
    institution = forms.ModelChoiceField(
        queryset=Institution.objects.filter(
            affiliations__asserted_by__work__isnull=False
        ).distinct(),
        widget=ModelSelect2(url="institution-autocomplete"),
        required=False,
        help_text="Works submitted with at least one author belonging to that institution.",
    )
    keyword = forms.ModelChoiceField(
        queryset=Keyword.objects.all(),
        required=False,
        widget=ModelSelect2(url="keyword-autocomplete"),
    )
    topic = forms.ModelChoiceField(
        queryset=Topic.objects.distinct(),
        required=False,
        widget=ModelSelect2(url="topic-autocomplete"),
    )
    language = forms.ModelChoiceField(
        queryset=Language.objects.distinct(),
        required=False,
        widget=ModelSelect2(url="language-autocomplete"),
    )
    discipline = forms.ModelChoiceField(
        queryset=Discipline.objects.distinct(),
        required=False,
        widget=ModelSelect2(url="discipline-autocomplete"),
    )


class FullWorkForm(WorkFilter):
    affiliation = forms.ModelChoiceField(
        queryset=Affiliation.objects.all(),
        required=False,
        widget=ModelSelect2(url="unrestricted-affiliation-autocomplete"),
        help_text='Search by department+institution combination. This is a more granular search than "Institution" above.',
    )
    n_authors = forms.IntegerField(
        label="Number of authors", min_value=0, required=False
    )
    keyword = forms.ModelChoiceField(
        queryset=Keyword.objects.distinct(),
        required=False,
        widget=ModelSelect2(url="unrestricted-keyword-autocomplete"),
    )


class WorkAuthorshipForm(forms.Form):
    author = forms.ModelChoiceField(
        queryset=Author.objects.all(),
        required=False,
        widget=ModelSelect2(url="unrestricted-author-autocomplete"),
        help_text="If the author currently exists, select them to auto-populate the fields below. Any edits to the details below will be stored as new assertions about this author. If the author does not yet exist, leave this field blank and they will be created from the information you enter below.",
    )
    authorship_order = forms.IntegerField(
        min_value=1,
        help_text="Authorship order must be unique across all the authorships of this work.",
    )
    first_name = forms.CharField(
        max_length=100,
        required=True,
        help_text="First name as it appears in the context of this abstract.",
    )
    last_name = forms.CharField(
        max_length=100,
        required=True,
        help_text="Last name as it appears in the context of this abstract.",
    )
    affiliations = forms.ModelMultipleChoiceField(
        queryset=Affiliation.objects.all(),
        required=False,
        widget=ModelSelect2Multiple(url="unrestricted-affiliation-autocomplete"),
        help_text="If the combination of department and institution is not available in this list, then use the fields below to define it.",
    )


class WorkForm(forms.ModelForm):
    keywords = forms.ModelMultipleChoiceField(
        queryset=Keyword.objects.all(),
        required=False,
        widget=ModelSelect2Multiple(url="unrestricted-keyword-autocomplete"),
        help_text="Optional keywords that are supplied by authors during submission in the modern ADHO DH conferences.",
    )

    topics = forms.ModelMultipleChoiceField(
        queryset=Topic.objects.all(),
        required=False,
        widget=ModelSelect2Multiple(url="unrestricted-topic-autocomplete"),
        help_text="Optional topics from a controlled vocabulary established by the ADHO DH conferences.",
    )

    languages = forms.ModelMultipleChoiceField(
        queryset=Language.objects.all(),
        required=False,
        widget=ModelSelect2Multiple(url="unrestricted-language-autocomplete"),
        help_text="Optional language tag to indicate the language(s) of the text of an abstract (not to be confused with e.g. 'English' as a keyword, where the topic of the abstract concerns English.)",
    )

    disciplines = forms.ModelMultipleChoiceField(
        queryset=Discipline.objects.all(),
        required=False,
        widget=ModelSelect2Multiple(url="unrestricted-discipline-autocomplete"),
        help_text="Optional discipline tag from a controlled vocabulary established by the ADHO DH conferences.",
    )

    conference = forms.ModelChoiceField(
        queryset=Conference.objects.all().prefetch_related("organizers"),
        help_text="The conference where this abstract was submitted/published.",
    )

    title = forms.CharField(max_length=500, help_text="Abstract title")

    url = forms.URLField(
        max_length=500,
        help_text="Optional URL pointing directly to this abstract",
        required=False,
    )

    work_type = forms.ModelChoiceField(
        queryset=WorkType.objects.all(),
        help_text='Abstracts may belong to one type that has been defined by editors based on a survey of all the abstracts in this collection, e.g. "poster", "workshop", "long paper".',
    )

    full_text_license = forms.ModelChoiceField(
        queryset=License.objects.all(),
        required=False,
        help_text="License information to be displayed with the full text of the abstract.",
    )

    full_text_type = forms.ChoiceField(
        choices=Work.FT_TYPE,
        initial="",
        help_text="Currently text can either be plain text, or entered as XML which will then be rendered into HTML.",
        required=False,
    )

    class Meta:
        model = Work
        fields = [
            "conference",
            "title",
            "url",
            "work_type",
            "full_text",
            "full_text_type",
            "full_text_license",
            "keywords",
            "languages",
            "disciplines",
            "topics",
        ]

    def clean(self):
        cleaned_data = super().clean()
        full_text = cleaned_data.get("full_text")
        full_text_type = cleaned_data.get("full_text_type")
        licence_type = cleaned_data.get("full_text_license")
        if full_text != "" and full_text_type == "":
            self.add_error(
                "full_text_type",
                "When full text is present, you must select a text type.",
            )
        if full_text == "" and full_text_type != "":
            self.add_error(
                "full_text",
                "When there is no full text, you may not select a text type.",
            )

        if full_text == "" and licence_type is not None:
            self.add_error(
                "full_text",
                "When there is no full text, you may not select a license type.",
            )


class AuthorFilter(forms.Form):
    ordering = forms.ChoiceField(
        choices=(
            ("last_name", "Last name (A-Z)"),
            ("-last_name", "Last name (Z-A)"),
            ("-n_works", "By number of abstracts (descending)"),
            ("n_works", "By number of abstracts (ascending)"),
        ),
        required=False,
        initial="last_name",
    )
    name = forms.CharField(max_length=100, strip=True, required=False)
    first_name = forms.CharField(
        max_length=100, strip=True, required=False, help_text="Search only first names"
    )
    last_name = forms.CharField(
        max_length=100, strip=True, required=False, help_text="Search only last names"
    )
    country = forms.ModelChoiceField(
        queryset=Country.objects.all(),
        required=False,
        help_text="Authors who were once affiliated with an institution in this country",
        widget=ModelSelect2(url="country-autocomplete"),
    )
    institution = forms.ModelChoiceField(
        queryset=Institution.objects.all(),
        required=False,
        widget=ModelSelect2(url="institution-autocomplete"),
        help_text="Authors who were once affiliated with this institution",
    )
    affiliation = forms.ModelChoiceField(
        queryset=Affiliation.objects.all(),
        required=False,
        widget=ModelSelect2(url="unrestricted-affiliation-autocomplete"),
        help_text='Search by department+institution combination. This is a more granular search than "Institution" above.',
    )


class AuthorMergeForm(forms.Form):
    into = forms.ModelChoiceField(
        queryset=Author.objects.all(),
        widget=ModelSelect2(url="unrestricted-author-autocomplete"),
        required=True,
        help_text="Select the author that will be used to replace the one you are merging.",
    )


class InstitutionMergeForm(forms.Form):
    into = forms.ModelChoiceField(
        queryset=Institution.objects.all(),
        widget=ModelSelect2(url="unrestricted-institution-autocomplete"),
        required=True,
        help_text="Select the institution that will be used to replace the one you are deleting.",
    )


class AffiliationMergeForm(forms.Form):
    into = forms.ModelChoiceField(
        queryset=Affiliation.objects.all(),
        widget=ModelSelect2(url="unrestricted-affiliation-autocomplete"),
        required=True,
        help_text="Select the affiliation that will be used to replace the one you are deleting.",
    )


class AffiliationMultiMergeForm(forms.Form):
    sources = forms.ModelMultipleChoiceField(
        queryset=Affiliation.objects.all(),
        widget=ModelSelect2Multiple(url="unrestricted-affiliation-autocomplete"),
        required=True,
        help_text="Select the affiliations that you want to merge together",
    )
    into = forms.ModelChoiceField(
        queryset=Affiliation.objects.all(),
        widget=ModelSelect2(url="unrestricted-affiliation-autocomplete"),
        required=True,
        help_text="Select the target affiliation to merge into",
    )


class InstitutionMultiMergeForm(forms.Form):
    sources = forms.ModelMultipleChoiceField(
        queryset=Institution.objects.all(),
        widget=ModelSelect2Multiple(url="unrestricted-institution-autocomplete"),
        required=True,
        help_text="Select the institutions that you want to merge together",
    )
    into = forms.ModelChoiceField(
        queryset=Institution.objects.all(),
        widget=ModelSelect2(url="unrestricted-institution-autocomplete"),
        required=True,
        help_text="Select the target institution to merge into",
    )


class AffiliationEditForm(forms.ModelForm):
    institution = forms.ModelChoiceField(
        queryset=Institution.objects.all(),
        widget=ModelSelect2(url="unrestricted-institution-autocomplete"),
        required=True,
    )

    class Meta:
        model = Affiliation
        fields = ["department", "institution"]


class FullInstitutionForm(forms.Form):
    department = forms.CharField(
        max_length=500, required=False, help_text="This free-text field is searchable"
    )
    no_department = forms.BooleanField(
        required=False,
        help_text="Show institutions with at least one affiliation that does not specifiy a department?",
    )
    affiliation = forms.ModelChoiceField(
        queryset=Affiliation.objects.all(),
        required=False,
        widget=ModelSelect2(url="unrestricted-affiliation-autocomplete"),
    )
    institution = forms.ModelChoiceField(
        queryset=Institution.objects.all(),
        required=False,
        widget=ModelSelect2(url="unrestricted-institution-autocomplete"),
    )
    country = forms.ModelChoiceField(
        queryset=Country.objects.filter().all(),
        required=False,
        widget=ModelSelect2(url="unrestricted-country-autocomplete"),
    )
    ordering = forms.ChoiceField(
        choices=(
            ("a", "A-Z"),
            ("n_dsc", "By number of abstracts (descending)"),
            ("n_asc", "By number of abstracts (ascending)"),
        ),
        required=True,
        initial="n_dsc",
    )


class KeywordMergeForm(forms.Form):
    into = forms.ModelChoiceField(
        queryset=Keyword.objects.all(),
        widget=ModelSelect2(url="unrestricted-keyword-autocomplete"),
        required=True,
        help_text="Select the keyword that will be used to replace the one you are deleting.",
    )


class KeywordMultiMergeForm(forms.Form):
    sources = forms.ModelMultipleChoiceField(
        queryset=Keyword.objects.all(),
        widget=ModelSelect2Multiple(url="unrestricted-keyword-autocomplete"),
        required=True,
        help_text="Select the keywords that you want to merge together",
    )
    into = forms.ModelChoiceField(
        queryset=Keyword.objects.all(),
        widget=ModelSelect2(url="unrestricted-keyword-autocomplete"),
        required=True,
        help_text="Select the target keyword to merge into",
    )


class TopicMultiMergeForm(forms.Form):
    sources = forms.ModelMultipleChoiceField(
        queryset=Topic.objects.all(),
        widget=ModelSelect2Multiple(url="unrestricted-topic-autocomplete"),
        required=True,
        help_text="Select the topics that you want to merge together",
    )
    into = forms.ModelChoiceField(
        queryset=Topic.objects.all(),
        widget=ModelSelect2(url="unrestricted-topic-autocomplete"),
        required=True,
        help_text="Select the target topic to merge into",
    )


class TopicMergeForm(forms.Form):
    into = forms.ModelChoiceField(
        queryset=Topic.objects.all(),
        widget=ModelSelect2(url="unrestricted-topic-autocomplete"),
        required=True,
        help_text="Select the topic that will be used to replace the one you are deleting.",
    )


class LanguageMergeForm(forms.Form):
    into = forms.ModelChoiceField(
        queryset=Language.objects.all(),
        widget=ModelSelect2(url="unrestricted-language-autocomplete"),
        required=True,
        help_text="Select the language that will be used to replace the one you are deleting.",
    )


class DisciplineMergeForm(forms.Form):
    into = forms.ModelChoiceField(
        queryset=Discipline.objects.all(),
        widget=ModelSelect2(url="unrestricted-discipline-autocomplete"),
        required=True,
        help_text="Select the discipline that will be used to replace the one you are deleting.",
    )


class WorkTypeMergeForm(forms.Form):
    into = forms.ModelChoiceField(
        queryset=WorkType.objects.all(),
        required=True,
        help_text="Select the type that will be used to replace the one you are deleting.",
    )


class TagForm(forms.Form):
    name = forms.CharField(
        max_length=100, required=False, help_text="Search by tag name"
    )
    ordering = forms.ChoiceField(
        choices=(
            ("a", "A-Z"),
            ("n_asc", "Number of Works (ascending)"),
            ("n_dsc", "Number of works (descending)"),
        ),
        required=True,
        initial="a",
    )


class ConferenceForm(forms.ModelForm):
    organizers = forms.ModelMultipleChoiceField(
        queryset=Organizer.objects.all(),
        required=False,
        help_text="Organizers of the conference",
    )

    class Meta:
        model = Conference
        fields = ["year", "venue", "venue_abbreviation", "notes", "url", "organizers"]


class ConferenceSeriesInline(forms.Form):
    series = forms.ModelChoiceField(
        queryset=ConferenceSeries.objects.all(), required=True
    )
    number = forms.IntegerField(
        min_value=1,
        required=False,
        help_text="Number in the sequence of this conference series.",
    )
