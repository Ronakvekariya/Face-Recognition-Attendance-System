from django import forms
# from .models import AbsenceReview

class LoginForm(forms.Form):
    Id = forms.CharField(max_length=150)
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)


class AbsenceReviewForm(forms.Form):
    # The choices for this field will be set dynamically in the view.
    LEAVE_TYPE_CHOICES = [
        ('Sick Leave', 'Sick Leave'),
        ('Paid Leave', 'Paid Leave'),
        ('Informed Leave', 'Informed Leave'),
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
    userid = forms.CharField(label='User ID', max_length=100)
    username = forms.CharField(label='Username', max_length=100)
    middlename = forms.CharField(label='Middlename', max_length=100)
    surname = forms.CharField(label='Surname', max_length=100)
    mobile_number = forms.CharField(max_length=10, required=True, label="Mobile Number")
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    email = forms.EmailField(label='Email')
    role = forms.ChoiceField(
        label='Role',
        choices=[('employee', 'Employee'), ('hr', 'HR')],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    job_title = forms.ChoiceField(
        label='Job Title',
        choices=[
            ('.NET Developer', '.NET Developer'),
            ('ERP', 'ERP'),
            ('HRMS', 'HRMS'),
            ('Data Scientist', 'Data Scientist'),
            ('React Developer', 'React Developer'),
            ('DBA', 'DBA')
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    job_position = forms.ChoiceField(
        label='Job Position',
        choices=[
            ('Fresher', 'Fresher'),
            ('Junior Developer', 'Junior Developer'),
            ('Senior Developer', 'Senior Developer'),
            ('Managing Director', 'Managing Director'),
            ('Deputy Chief Head', 'Deputy Chief Head')
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )


