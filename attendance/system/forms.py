from django import forms
# from .models import AbsenceReview

class LoginForm(forms.Form):
    Id = forms.CharField(max_length=150)
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)


class AbsenceReviewForm(forms.Form):
    # The choices for this field will be set dynamically in the view.
    date = forms.ChoiceField(choices=[], widget=forms.Select(attrs={'class': 'form-control'}))
    explanation = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        label="Explanation"
    )

