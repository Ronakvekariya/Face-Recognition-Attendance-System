from django.db import models

class User(models.Model):
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=255)  # Use hashed passwords
    role = models.CharField(max_length=10, choices=[('HR', 'HR'), ('Employee', 'Employee')])

    def __str__(self):
        return self.username

from django.db import models

class AbsenceReview(models.Model):
    employee_username = models.CharField(max_length=150)
    date = models.DateField()
    explanation = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee_username} - {self.date}"
