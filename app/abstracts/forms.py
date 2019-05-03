from django import forms
from dal.autocomplete import ModelSelect2, ModelSelect2Multiple
from django.forms import inlineformset_factory, modelformset_factory

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
)


class WorkFilter(forms.Form):
    text = forms.CharField(max_length=100, strip=True, required=False)
    work_type = forms.ModelChoiceField(
        queryset=WorkType.objects.filter(works__state="ac").distinct(), required=False
    )
    conference = forms.ModelChoiceField(
        queryset=Conference.objects.filter(works__state="ac").distinct(),
        required=False,
        help_text="Works submitted to a particular conference",
    )
    institution = forms.ModelChoiceField(
        queryset=Institution.objects.filter(
            affiliations__asserted_by__work__state="ac"
        ).distinct(),
        widget=ModelSelect2(url="institution-autocomplete"),
        required=False,
        help_text="Works submitted with at least one author belonging to that institution.",
    )
    keyword = forms.ModelChoiceField(
        queryset=Keyword.objects.filter(works__state="ac").distinct(),
        required=False,
        widget=ModelSelect2(url="keyword-autocomplete"),
    )
    topic = forms.ModelChoiceField(
        queryset=Topic.objects.filter(works__state="ac").distinct(),
        required=False,
        widget=ModelSelect2(url="topic-autocomplete"),
    )
    language = forms.ModelChoiceField(
        queryset=Language.objects.filter(works__state="ac").distinct(),
        required=False,
        widget=ModelSelect2(url="language-autocomplete"),
    )
    discipline = forms.ModelChoiceField(
        queryset=Discipline.objects.filter(works__state="ac").distinct(),
        required=False,
        widget=ModelSelect2(url="discipline-autocomplete"),
    )


class WorkAuthorshipForm(forms.ModelForm):
    work = forms.ModelChoiceField(
        queryset=Work.objects.distinct(),
        required=True,
        widget=ModelSelect2(url="work-autocomplete"),
    )
    author = (
        forms.ModelChoiceField(
            queryset=Author.objects.distinct(),
            required=True,
            widget=ModelSelect2(url="author-autocomplete"),
        ),
    )
    authorship_order = forms.IntegerField(min_value=0)

    class Meta:
        model = Authorship
        fields = ["work", "author", "authorship_order"]


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

    published_version = forms.ModelChoiceField(
        queryset=Work.objects.filter(state="ac"),
        required=False,
        widget=ModelSelect2(url="unrestricted-work-autocomplete"),
        help_text='Abstracts with the state "submitted" may be associated with "accepted" abstracts, establishing a link that will be visible in the editing interface. Note: one accepted work may be associated with many submitted works, but a submitted work may only be associated with one final accepted work. TODO: do not show unaccepted works in select interface.',
    )

    conference = forms.ModelChoiceField(
        queryset=Conference.objects.all(),
        help_text="The conference where this abstract was submitted/published.",
    )

    title = forms.CharField(max_length=500, help_text="Abstract title")

    work_type = forms.ModelChoiceField(
        queryset=WorkType.objects.all(),
        help_text='Abstracts may belong to one type that has been defined by editors based on a survey of all the abstracts in this collection, e.g. "poster", "workshop", "long paper".',
    )

    state = forms.ChoiceField(
        choices=Work.WORK_STATE,
        widget=forms.RadioSelect,
        help_text='Abstracts may be either "Accepted" or "Submitted". Abstracts that aren\'t marked "Accepted" will not display to public viewers, and none of the names or affiliations asserted by those abstracts will be listed publicly in author profiles.',
    )

    full_text_license = forms.ModelChoiceField(
        queryset=License.objects.all(),
        help_text="License information to be displayed with the full text of the abstract.",
    )

    full_text_type = forms.ChoiceField(
        choices=Work.FT_TYPE,
        widget=forms.RadioSelect,
        help_text="Currently text can either be plain text, or entered as XML which will then be rendered into HTML.",
    )

    class Meta:
        model = Work
        fields = [
            "conference",
            "title",
            "work_type",
            "state",
            "full_text",
            "full_text_type",
            "full_text_license",
            "keywords",
            "languages",
            "disciplines",
            "topics",
        ]


class AuthorFilter(forms.Form):
    name = forms.CharField(max_length=100, strip=True, required=False)
    institution = forms.ModelChoiceField(
        queryset=Institution.objects.filter(
            affiliations__asserted_by__work__state="ac"
        ).distinct(),
        required=False,
        widget=ModelSelect2(url="institution-autocomplete"),
        help_text="Authors who were once affiliated with this institution",
    )
    country = forms.ModelChoiceField(
        queryset=Country.objects.filter(
            institutions__affiliations__asserted_by__work__state="ac"
        ).distinct(),
        required=False,
        help_text="Authors who were once affiliated with an institution in this country",
        widget=ModelSelect2(url="country-autocomplete"),
    )


class AuthorMergeForm(forms.Form):
    into = forms.ModelChoiceField(
        queryset=Author.objects.all(),
        widget=ModelSelect2(url="unrestricted-author-autocomplete"),
        required=True,
        help_text="Select the author that will be used to replace the one you are merging.",
    )


AuthorshipWorkFormset = modelformset_factory(Authorship, exclude=["work"], extra=0)
