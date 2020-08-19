from django import forms
from dal import forward
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
    License,
    Affiliation,
    SeriesMembership,
    ConferenceSeries,
    Organizer,
)


class WorkFilter(forms.ModelForm):
    ordering = forms.ChoiceField(
        choices=(
            ("year", "Conference year (ascending)"),
            ("-year", "Conference year (descending)"),
            ("rank", "Text search relevance"),
            ("title", "Title (A-Z)"),
            ("-title", "Title (Z-A)"),
            ("last_name", "First author, last name (A-Z)"),
            ("-last_name", "First author, last name (Z-A)"),
        ),
        required=False,
        initial="year",
    )
    text = forms.CharField(
        max_length=100,
        strip=True,
        required=False,
        help_text="Search abstracts by title and full text content (when available)",
    )
    full_text_available = forms.BooleanField(
        required=False, label="Full text has been indexed"
    )
    full_text_viewable = forms.BooleanField(
        required=False, label="Full text is publicly viewable"
    )
    work_type = forms.ModelChoiceField(
        queryset=WorkType.objects.distinct(),
        required=False,
        help_text='Abstracts may belong to one type that has been defined by editors based on a survey of all the abstracts in this collection, e.g. "poster", "workshop", "long paper".',
    )
    author = forms.ModelMultipleChoiceField(
        queryset=Author.objects.all(),
        required=False,
        widget=ModelSelect2Multiple(
            url="author-autocomplete", attrs={"data-html": True}
        ),
        help_text="Abstract authorship must include this person",
    )
    conference = forms.ModelChoiceField(
        queryset=Conference.objects.all(),
        required=False,
        widget=ModelSelect2(url="conference-autocomplete"),
        help_text="The conference where this abstract was submitted/published.",
    )
    institution = forms.ModelMultipleChoiceField(
        queryset=Institution.objects.all(),
        widget=ModelSelect2Multiple(
            url="institution-autocomplete", attrs={"data-html": True}
        ),
        required=False,
        help_text="Works having at least one author belonging to ANY of the selected institutions.",
    )
    affiliation = forms.ModelMultipleChoiceField(
        queryset=Affiliation.objects.all(),
        widget=ModelSelect2Multiple(
            url="affiliation-autocomplete", attrs={"data-html": True}
        ),
        required=False,
        help_text="Works having at least one author belonging to a specific department or other center within a larger institution.",
    )

    class Meta:
        model = Work
        fields = [
            "ordering",
            "text",
            "conference",
            "full_text_available",
            "full_text_viewable",
            "work_type",
            "author",
            "institution",
            "affiliation",
            "keywords",
            "languages",
            "topics",
        ]
        field_classes = {
            "keywords": forms.ModelMultipleChoiceField,
            "topics": forms.ModelMultipleChoiceField,
            "languages": forms.ModelMultipleChoiceField,
        }
        widgets = {
            "keywords": ModelSelect2Multiple(
                url="keyword-autocomplete", attrs={"data-html": True}
            ),
            "topics": ModelSelect2Multiple(
                url="topic-autocomplete", attrs={"data-html": True}
            ),
            "languages": ModelSelect2Multiple(
                url="language-autocomplete", attrs={"data-html": True}
            ),
        }


class WorkAuthorshipForm(forms.Form):
    author = forms.ModelChoiceField(
        queryset=Author.objects.all(),
        required=False,
        widget=ModelSelect2(url="author-autocomplete", attrs={"data-html": True}),
        help_text="If the author currently exists, select them to auto-populate the fields below. Any edits to the details below will be stored as new assertions about this author. If the author does not yet exist, leave this field blank and they will be created from the information you enter below.",
    )
    authorship_order = forms.IntegerField(
        min_value=1,
        help_text="Authorship order must be unique across all the authorships of this work.",
    )
    first_name = forms.CharField(
        max_length=100,
        required=True,
        label="First and middle names",
        help_text="First and middle names/initials as it appears in the context of this abstract.",
    )
    last_name = forms.CharField(
        max_length=100,
        required=True,
        help_text="Last name as it appears in the context of this abstract.",
    )
    affiliations = forms.ModelMultipleChoiceField(
        queryset=Affiliation.objects.all(),
        required=False,
        widget=ModelSelect2Multiple(
            url="affiliation-autocomplete",
            attrs={"data-html": True},
            forward=["institution"],
        ),
        help_text="If the combination of department and institution is not available in this list, then use the fields below to define it.",
    )
    institution = forms.ModelChoiceField(
        queryset=Institution.objects.all(),
        required=False,
        widget=ModelSelect2(url="institution-autocomplete", attrs={"data-html": True}),
        help_text="Use this optional menu to filter the affiliation list below. This value is only used for filtering and does not affect the final affiliation data that gets saved.",
    )

    def clean(self):
        cleaned_data = super().clean()
        affiliations = cleaned_data.get("affiliations")
        institution = cleaned_data.get("institution")
        if institution is not None and len(affiliations) < 1:
            self.add_error(
                "affiliations",
                "You must enter a specific affiliation for each author. It is not sufficient to only select an institution - that field is used only to filter the available affiliations.",
            )


class WorkForm(forms.ModelForm):
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
            "topics",
            "parent_session",
        ]
        widgets = {
            "keywords": ModelSelect2Multiple(url="keyword-autocomplete"),
            "topics": ModelSelect2Multiple(url="topic-autocomplete"),
            "languages": ModelSelect2Multiple(url="language-autocomplete"),
            "conference": ModelSelect2(url="conference-autocomplete"),
            "parent_session": ModelSelect2(
                url="work-autocomplete",
                forward=["conference", forward.Const(True, "parents_only")],
            ),
        }

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
        work_type = cleaned_data.get("work_type")
        parent_session = cleaned_data.get("parent_session")
        if work_type.is_parent and parent_session is not None:
            self.add_error(
                "parent_session",
                f"Works of type '{work_type}' cannot have parent sessions.",
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
    author = forms.ModelChoiceField(
        queryset=Author.objects.all(),
        required=False,
        widget=ModelSelect2(url="author-autocomplete", attrs={"data-html": True}),
    )
    name = forms.CharField(max_length=100, strip=True, required=False)
    first_name = forms.CharField(
        max_length=100,
        strip=True,
        required=False,
        label="First/middle name",
        help_text="Search only first and middle names",
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
        widget=ModelSelect2(url="institution-autocomplete", attrs={"data-html": True}),
        help_text="Authors who were once affiliated with this institution",
    )
    affiliation = forms.ModelChoiceField(
        queryset=Affiliation.objects.all(),
        required=False,
        widget=ModelSelect2(url="affiliation-autocomplete", attrs={"data-html": True}),
        help_text='Search by department+institution combination. This is a more granular search than "Institution" above.',
    )


class AuthorMergeForm(forms.Form):
    into = forms.ModelChoiceField(
        queryset=Author.objects.all(),
        widget=ModelSelect2(url="author-autocomplete", attrs={"data-html": True}),
        required=True,
        help_text="Select the author that will be used to replace the one you are merging.",
    )


class InstitutionMergeForm(forms.Form):
    into = forms.ModelChoiceField(
        queryset=Institution.objects.all(),
        widget=ModelSelect2(url="institution-autocomplete", attrs={"data-html": True}),
        required=True,
        help_text="Select the institution that will be used to replace the one you are deleting.",
    )


class AffiliationMergeForm(forms.Form):
    into = forms.ModelChoiceField(
        queryset=Affiliation.objects.all(),
        widget=ModelSelect2(url="affiliation-autocomplete", attrs={"data-html": True}),
        required=True,
        help_text="Select the affiliation that will be used to replace the one you are deleting.",
    )


class AffiliationMultiMergeForm(forms.Form):
    sources = forms.ModelMultipleChoiceField(
        queryset=Affiliation.objects.all(),
        widget=ModelSelect2Multiple(
            url="affiliation-autocomplete", attrs={"data-html": True}
        ),
        required=True,
        help_text="Select the affiliations that you want to merge together",
    )
    into = forms.ModelChoiceField(
        queryset=Affiliation.objects.all(),
        widget=ModelSelect2(url="affiliation-autocomplete", attrs={"data-html": True}),
        required=True,
        help_text="Select the target affiliation to merge into",
    )


class InstitutionMultiMergeForm(forms.Form):
    sources = forms.ModelMultipleChoiceField(
        queryset=Institution.objects.all(),
        widget=ModelSelect2Multiple(
            url="institution-autocomplete", attrs={"data-html": True}
        ),
        required=True,
        help_text="Select the institutions that you want to merge together",
    )
    into = forms.ModelChoiceField(
        queryset=Institution.objects.all(),
        widget=ModelSelect2(url="institution-autocomplete", attrs={"data-html": True}),
        required=True,
        help_text="Select the target institution to merge into",
    )


class AffiliationEditForm(forms.ModelForm):
    institution = forms.ModelChoiceField(
        queryset=Institution.objects.all(),
        widget=ModelSelect2(url="institution-autocomplete", attrs={"data-html": True}),
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
        widget=ModelSelect2(url="affiliation-autocomplete", attrs={"data-html": True}),
    )
    institution = forms.ModelChoiceField(
        queryset=Institution.objects.all(),
        required=False,
        widget=ModelSelect2(url="institution-autocomplete", attrs={"data-html": True}),
    )
    country = forms.ModelChoiceField(
        queryset=Country.objects.filter().all(),
        required=False,
        widget=ModelSelect2(url="country-autocomplete"),
    )
    ordering = forms.ChoiceField(
        choices=(
            ("a", "A-Z"),
            ("n_dsc", "By number of abstracts (descending)"),
            ("n_asc", "By number of abstracts (ascending)"),
        ),
        required=False,
        initial="n_dsc",
    )


class KeywordMergeForm(forms.Form):
    into = forms.ModelChoiceField(
        queryset=Keyword.objects.all(),
        widget=ModelSelect2(url="keyword-autocomplete"),
        required=True,
        help_text="Select the keyword that will be used to replace the one you are deleting.",
    )


class KeywordMultiMergeForm(forms.Form):
    sources = forms.ModelMultipleChoiceField(
        queryset=Keyword.objects.all(),
        widget=ModelSelect2Multiple(url="keyword-autocomplete"),
        required=True,
        help_text="Select the keywords that you want to merge together",
    )
    into = forms.ModelChoiceField(
        queryset=Keyword.objects.all(),
        widget=ModelSelect2(url="keyword-autocomplete"),
        required=True,
        help_text="Select the target keyword to merge into",
    )


class TopicMultiMergeForm(forms.Form):
    sources = forms.ModelMultipleChoiceField(
        queryset=Topic.objects.all(),
        widget=ModelSelect2Multiple(url="topic-autocomplete"),
        required=True,
        help_text="Select the topics that you want to merge together",
    )
    into = forms.ModelChoiceField(
        queryset=Topic.objects.all(),
        widget=ModelSelect2(url="topic-autocomplete"),
        required=True,
        help_text="Select the target topic to merge into",
    )


class TopicMergeForm(forms.Form):
    into = forms.ModelChoiceField(
        queryset=Topic.objects.all(),
        widget=ModelSelect2(url="topic-autocomplete"),
        required=True,
        help_text="Select the topic that will be used to replace the one you are deleting.",
    )


class LanguageMergeForm(forms.Form):
    into = forms.ModelChoiceField(
        queryset=Language.objects.all(),
        widget=ModelSelect2(url="language-autocomplete"),
        required=True,
        help_text="Select the language that will be used to replace the one you are deleting.",
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


class ConferenceCheckoutForm(forms.Form):
    USER_CHOICES = (
        ("self", "Assign self (replacing any currently-associated user)"),
        ("clear", "Clear self/others from conference"),
    )

    entry_status = forms.ChoiceField(
        choices=Conference.ENTRY_STATUS,
        widget=forms.RadioSelect(choices=Conference.ENTRY_STATUS),
    )

    assign_user = forms.ChoiceField(
        choices=USER_CHOICES,
        initial="self",
        widget=forms.RadioSelect(choices=USER_CHOICES),
    )


class ConferenceForm(forms.ModelForm):
    organizers = forms.ModelMultipleChoiceField(
        queryset=Organizer.objects.all(),
        required=False,
        help_text="Organizers of the conference",
    )

    class Meta:
        model = Conference
        fields = [
            "full_text_public",
            "year",
            "short_title",
            "theme_title",
            "hosting_institutions",
            "url",
            "city",
            "state_province_region",
            "country",
            "organizers",
            "start_date",
            "end_date",
            "notes",
            "references",
            "contributors",
            "attendance",
            "entry_status",
            "program_available",
            "abstracts_available",
        ]
        widgets = {
            "entry_status": forms.RadioSelect(choices=Conference.ENTRY_STATUS),
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
            "country": ModelSelect2(url="country-autocomplete"),
            "hosting_institutions": ModelSelect2Multiple(
                url="institution-autocomplete", attrs={"data-html": True}
            ),
            "references": forms.Textarea(attrs={"rows": 2}),
            "contributors": forms.Textarea(attrs={"rows": 2}),
            "attendance": forms.Textarea(attrs={"rows": 2}),
        }

    def clean(self, *args, **kwargs):
        cleaned_data = super().clean(*args, **kwargs)
        short_title = cleaned_data.get("short_title")
        theme_title = cleaned_data.get("theme_title")
        hosting_institutions = cleaned_data.get("hosting_institutions")
        if (
            short_title == ""
            and theme_title == ""
            and city == ""
            and len(hosting_institutions) == 0
        ):
            self.add_error(
                "Conference creation error",
                "You must supply at least one of either: short title, theme title, city, or at least one hosting institution",
            )


class ConferenceSeriesInline(forms.Form):
    series = forms.ModelChoiceField(
        queryset=ConferenceSeries.objects.all(), required=True
    )
    number = forms.IntegerField(
        min_value=1,
        required=False,
        help_text="Number in the sequence of this conference series.",
    )
