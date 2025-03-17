from django import forms
# from .models import AbsenceReview

class LoginForm(forms.Form):
    Id = forms.CharField(max_length=150)
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)


class AbsenceReviewForm(forms.Form):
    # The choices for this field will be set dynamically in the view.
    LEAVE_TYPE_CHOICES = [
        ('sick_leave', 'Sick Leave'),
        ('paid_leave', 'Paid Leave'),
        ('informed_leave', 'Informed Leave'),
    ]

    date = forms.ChoiceField(choices=[], widget=forms.Select(attrs={'class': 'form-control'}))
    explanation = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        label="Explanation"
    )
    leave_type = forms.ChoiceField(
        choices=LEAVE_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Leave Type"
    )


class SelectMonthForm(forms.Form):
    month = forms.ChoiceField(choices=[], widget=forms.Select(attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        months = kwargs.pop('months', [])  # Get months from view
        super().__init__(*args, **kwargs)
        self.fields['month'].choices = [(m, m) for m in months]

class AddUser(forms.Form):
    userid = forms.CharField()
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    role = forms.ChoiceField(choices=[('employee', 'Employee'), ('hr', 'HR')], widget=forms.Select(attrs={'class': 'form-control'}))

