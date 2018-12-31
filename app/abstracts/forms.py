from django import forms

from .models import Author, Authorship, Conference, Institution, Topic, Keyword, Work


class WorkFilter(forms.Form):
    # submission_type = forms.ChoiceField(
    #     choices=Work.objects.values_list("submission_type").distinct()
    # )
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
