from django import forms

from main import models


class SubmissionForm(forms.ModelForm):
    """Form for submitting films to the festival."""

    class Meta:
        model = models.Submission
        fields = [
            "title",
            "director_name",
            "email",
            "synopsis",
            "genre",
            "film_link",
            "consent",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-input"}),
            "director_name": forms.TextInput(attrs={"class": "form-input"}),
            "email": forms.EmailInput(attrs={"class": "form-input"}),
            "synopsis": forms.Textarea(attrs={"rows": 5, "class": "form-textarea"}),
            "genre": forms.TextInput(attrs={"class": "form-input"}),
            "film_link": forms.URLInput(attrs={"class": "form-input"}),
            "consent": forms.CheckboxInput(attrs={"class": "form-checkbox"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["consent"].required = True
        self.fields[
            "consent"
        ].label = "I give permission to use the above info for promotional material"
