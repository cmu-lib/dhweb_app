from django import forms
from dal.autocomplete import ModelSelect2, ModelSelect2Multiple


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


class AuthorshipForm(forms.ModelForm):
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
    )

    topics = forms.ModelMultipleChoiceField(
        queryset=Topic.objects.all(),
        required=False,
        widget=ModelSelect2Multiple(url="unrestricted-topic-autocomplete"),
    )

    languages = forms.ModelMultipleChoiceField(
        queryset=Language.objects.all(),
        required=False,
        widget=ModelSelect2Multiple(url="unrestricted-language-autocomplete"),
    )

    disciplines = forms.ModelMultipleChoiceField(
        queryset=Discipline.objects.all(),
        required=False,
        widget=ModelSelect2Multiple(url="unrestricted-discipline-autocomplete"),
    )

    published_version = forms.ModelChoiceField(
        queryset=Work.objects.filter(state="ac"),
        required=False,
        widget=ModelSelect2(url="unrestricted-work-autocomplete"),
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
        widget=ModelSelect2(url="author-autocomplete"),
        required=True,
        help_text="Select the author that will be used to replace the one you are merging.",
    )

