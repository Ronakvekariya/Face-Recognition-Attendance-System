from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db import connection
from .forms import LoginForm , AbsenceReviewForm
# from .models import AbsenceReview
import datetime
import calendar
import json

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            EmployeeId = form.cleaned_data['EmployeeId']    
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            with connection.cursor() as cursor:
                cursor.execute("SELECT role FROM system_user WHERE id = %s AND username=%s AND password=%s", [EmployeeId , username, password])
                user = cursor.fetchone()

            if user:
                role = user[0]
                request.session['EmployeeId'] = EmployeeId
                request.session['username'] = username
                request.session['role'] = role

                if role == 'HR':
                    return redirect('hr_dashboard')
                else:
                    return redirect('employee_dashboard')

            return HttpResponse("Invalid username or password")

    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})

def logout_view(request):
    request.session.flush()
    return redirect('login')

def hr_dashboard(request):
    if request.session.get('role') == 'HR':
        return render(request, 'hr_dashboard.html')
    return HttpResponse("Unauthorized", status=403)

def employee_dashboard(request):
    if request.session.get('role') == 'Employee':
     # Placeholder for attendance data. Add your logic to fetch data.
        attendance_data = []  # You can replace this with your actual attendance logic.
        with connection.cursor() as cursor:
            cursor.execute("SELECT attendance FROM attendance_table where id = %s", [request.session.get('EmployeeId')])
            result = cursor.fetchone()

            if result: 
                temp = json.loads(result[0])
                today = datetime.date.today()
                year = today.year
                month = today.month

                # Get the total number of days in the current month
                _, num_days = calendar.monthrange(year, month)

                # Initialize a dictionary for the month and a counter for Saturdays
                attendance_data = {}
                absenece_date = []
                saturday_counter = 0

                # Iterate through all days of the month
                for day in range(1, num_days + 1):
                    date_obj = datetime.date(year, month, day)
                    # Format the date as "yy-mm-dd"
                    date_str = date_obj.strftime("%y-%m-%d")
                    
                    
                    if date_obj.weekday() == 5:  # Saturday (Monday=0, ..., Saturday=5)
                        saturday_counter += 1
                        # Mark only the 1st, 3rd, and 5th Saturdays as holiday
                        if saturday_counter in (1, 3, 5):
                            attendance_data[date_str] = {"status" : "Holiday" , "InTime" : "N/A" , "OutTime" : "N/A"}
                        else:
                            if date_str in temp.keys():
                                
                                attendance_data[date_str] = {"status" : "Present" , "InTime" : temp[date_str]["InTime"] , "OutTime" : temp[date_str]["OutTime"]}
                            else:
                                attendance_data[date_str] = {"status" : "Absent" , "InTime" : "N/A" , "OutTime" : "N/A"}
                                absenece_date.append(date_str)
                    elif date_obj.weekday() == 6:  # Sunday (Sunday=6)
                        attendance_data[date_str] = "Holiday"
                    else:
                        if date_str in temp.keys():
                            attendance_data[date_str] = {"status" : "Present" , "InTime" : temp[date_str]["InTime"] , "OutTime" : temp[date_str]["OutTime"]}
                        else:
                            attendance_data[date_str] = {"status" : "Absent" , "InTime" : "N/A" , "OutTime" : "N/A"}
                            absenece_date.append(date_str)

                request.session['absenece_date'] = absenece_date
                request.session['attendance_data'] = attendance_data
                    
        return render(request, 'employee_dashboard.html')
    return HttpResponse("Unauthorized", status=403)

def monthly_attendance(request):
    return render(request, 'monthly_attendance.html', {'attendance_data': request.session.get('attendance_data', {})})

def absence_review(request):
    # Retrieve the absence dates stored in session (e.g., ["2025-03-01", "2025-03-03", ...])
    absence_data = request.session.get('absenece_date', [])
    
    if request.method == 'POST':
        form = AbsenceReviewForm(request.POST)
        # Set the dropdown choices dynamically from session data.
        form.fields['date'].choices = [(d, d) for d in absence_data]
        
        if form.is_valid():
            # Get the cleaned form data
            date = form.cleaned_data['date']
            explanation = form.cleaned_data['explanation']

            with connection.cursor() as cursor:
                cursor.execute("select employee_id , date from absence_review where employee_id = %s and date = %s", [request.session.get('EmployeeId') , date])
                result = cursor.fetchone()
                if result:
                    return render(request , "absence_review.html",{"form" : form , "message" : "You have already submitted an explanation for this date."})
                cursor.execute("INSERT INTO absence_review (employee_id , date ,  explanation , status) VALUES (%s , %s, %s, %s)", [request.session.get('EmployeeId') ,date, explanation , "pending"])
                connection.commit()
            
            
            
            return redirect('employee_dashboard')
    else:
        form = AbsenceReviewForm()
        # Set the dropdown choices for GET requests as well.
        form.fields['date'].choices = [(d, d) for d in absence_data]
    
    return render(request, 'absence_review.html', {'form': form})