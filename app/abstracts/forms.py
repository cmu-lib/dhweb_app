from django import forms

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
        required=False,
        help_text="Works submitted with at least one author belonging to that institution.",
    )
    keyword = forms.ModelChoiceField(
        queryset=Keyword.objects.filter(works__state="ac").distinct(), required=False
    )
    topic = forms.ModelChoiceField(
        queryset=Topic.objects.filter(works__state="ac").distinct(), required=False
    )
    full_text_available = forms.BooleanField(required=False)


class AuthorFilter(forms.Form):
    name = forms.CharField(max_length=100, strip=True, required=False)
    institution = forms.ModelChoiceField(
        queryset=Institution.objects.filter(
            affiliations__asserted_by__work__state="ac"
        ).distinct(),
        required=False,
        help_text="Authors who were once affiliated with this institution",
    )
    country = forms.ModelChoiceField(
        queryset=Country.objects.filter(
            institutions__affiliations__asserted_by__work__state="ac"
        ).distinct(),
        required=False,
        help_text="Authors who were once affiliated with an institution in this country",
    )


class AuthorMergeForm(forms.Form):
    into = forms.IntegerField(
        required=True,
        help_text="Enter the id number (found in the URL) of the author that will be used to replace the one you are merging.",
    )

