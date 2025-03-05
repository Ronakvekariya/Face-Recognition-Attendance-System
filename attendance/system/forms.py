from django import forms
from .models import AbsenceReview

class LoginForm(forms.Form):
    EmployeeId = forms.CharField(max_length=150)
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)


class AbsenceReviewForm(forms.ModelForm):
    class Meta:
        model = AbsenceReview
        fields = ['date', 'explanation']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'explanation': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

