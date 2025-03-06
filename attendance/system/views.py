from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db import connection
from .forms import LoginForm , AbsenceReviewForm
# from .models import AbsenceReview
from datetime import datetime
import calendar
import json

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            Id = form.cleaned_data['Id']    
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            with connection.cursor() as cursor:
                cursor.execute("SELECT role FROM system_user WHERE employee_id = %s AND username=%s AND password=%s", [Id , username, password])
                user = cursor.fetchone()

            if user:
                role = user[0]
                request.session['Id'] = Id
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
            cursor.execute("SELECT attendance FROM attendance_table where employee_id = %s", [request.session.get('Id')])
            result = cursor.fetchone()

            if result: 
                temp = json.loads(result[0])
                dates = list(temp.keys())
                sorted_dates = sorted(dates)
                start_date = sorted_dates[0]
                end_date = sorted_dates[-1]

                start_date_object = datetime.strptime(start_date, '%Y-%m-%d')
                end_date_object = datetime.strptime(end_date, '%Y-%m-%d')


                # start_date_object = start_date.strftime('%Y-%m-%d')
                # end_date_object = end_date.strftime('%Y-%m-%d')

                month_list = ["January", "February", "March", "April", "May", "June",
                          "July", "August", "September", "October", "November", "December"]
                month_wise_attendance = {}
                month_wise_extra_days = {}
                month_wise_absence_dates = {}
                absence_dates = []

                extra_days = 0
                saturday_counter = 0
                attendance_data = {}                

                _, num_days = calendar.monthrange(start_date_object.year , start_date_object.month)

                print(start_date_object.year, start_date_object.month)

                for day in range(start_date_object.day , num_days + 1):
                    date_obj = datetime(start_date_object.year, start_date_object.month, day).date()
                    date_str = date_obj.strftime("%y-%m-%d")

                    if date_obj.weekday() == 5:  # Saturday (Monday=0, ..., Saturday=5)
                        saturday_counter += 1
                        # Mark only the 1st, 3rd, and 5th Saturdays as holiday
                        if saturday_counter in (1, 3, 5):
                            if date_str in temp.keys():
                                attendance_data[date_str] = {"status" : "Holiday" , "InTime" : temp[date_str]["InTime"] , "OutTime" : temp[date_str]["OutTime"]}
                                extra_days += 1
                            else:
                                attendance_data[date_str] = {"status" : "Holiday" , "InTime" : "N/A" , "OutTime" : "N/A"}
                        else:
                            if date_str in temp.keys():                                
                                attendance_data[date_str] = {"status" : "Present" , "InTime" : temp[date_str]["InTime"] , "OutTime" : temp[date_str]["OutTime"]}
                            else:
                                attendance_data[date_str] = {"status" : "Absent" , "InTime" : "N/A" , "OutTime" : "N/A"}
                                absence_dates.append(date_str)
                    elif date_obj.weekday() == 6:  # Sunday (Sunday=6)
                        if date_str in temp.keys():
                                attendance_data[date_str] = {"status" : "Holiday" , "InTime" : temp[date_str]["InTime"] , "OutTime" : temp[date_str]["OutTime"]}
                                extra_days += 1
                        else:
                                attendance_data[date_str] = {"status" : "Holiday" , "InTime" : "N/A" , "OutTime" : "N/A"}
                    else:
                        if date_str in temp.keys():
                            attendance_data[date_str] = {"status" : "Present" , "InTime" : temp[date_str]["InTime"] , "OutTime" : temp[date_str]["OutTime"]}
                        else:
                            attendance_data[date_str] = {"status" : "Absent" , "InTime" : "N/A" , "OutTime" : "N/A"}
                            absence_dates.append(date_str)

                print(attendance_data)
                        
                
                attendance_data = json.dumps(attendance_data)
                month_wise_attendance[month_list[start_date_object.month - 1]] = attendance_data
                month_wise_extra_days[month_list[start_date_object.month - 1]] = extra_days
                month_wise_absence_dates[month_list[start_date_object.month - 1]] = absence_dates

                absence_dates = []

                extra_days = 0

                attendance_data = {}

                for month in range(start_date_object.month + 1 , end_date_object.month):
                    _, num_days = calendar.monthrange(start_date_object.year , month)
                    for day in range(1 , num_days + 1):
                        date_obj = datetime.date(start_date_object.year, month, day)
                        date_str = date_obj.strftime("%y-%m-%d")
                        if date_obj.weekday() == 5:  # Saturday (Monday=0, ..., Saturday=5)
                            saturday_counter += 1
                            # Mark only the 1st, 3rd, and 5th Saturdays as holiday
                            if saturday_counter in (1, 3, 5):
                                if date_str in temp.keys():
                                    attendance_data[date_str] = {"status" : "Holiday" , "InTime" : temp[date_str]["InTime"] , "OutTime" : temp[date_str]["OutTime"]}
                                    extra_days += 1
                                else:
                                    attendance_data[date_str] = {"status" : "Holiday" , "InTime" : "N/A" , "OutTime" : "N/A"}
                            else:
                                if date_str in temp.keys():                                
                                    attendance_data[date_str] = {"status" : "Present" , "InTime" : temp[date_str]["InTime"] , "OutTime" : temp[date_str]["OutTime"]}
                                else:
                                    attendance_data[date_str] = {"status" : "Absent" , "InTime" : "N/A" , "OutTime" : "N/A"}
                                    absence_dates.append(date_str)
                        elif date_obj.weekday() == 6:  # Sunday (Sunday=6)
                            if date_str in temp.keys():
                                    attendance_data[date_str] = {"status" : "Holiday" , "InTime" : temp[date_str]["InTime"] , "OutTime" : temp[date_str]["OutTime"]}
                            else:
                                    attendance_data[date_str] = {"status" : "Holiday" , "InTime" : "N/A" , "OutTime" : "N/A"}
                        else:
                            if date_str in temp.keys():
                                attendance_data[date_str] = {"status" : "Present" , "InTime" : temp[date_str]["InTime"] , "OutTime" : temp[date_str]["OutTime"]}
                                extra_days += 1
                            else:
                                attendance_data[date_str] = {"status" : "Absent" , "InTime" : "N/A" , "OutTime" : "N/A"} 
                                absence_dates.append(date_str)                       

                    attendance_data = json.dumps(attendance_data)
                    month_wise_attendance[month_list[start_date_object.month - 1]] = attendance_data
                    month_wise_extra_days[month_list[start_date_object.month - 1]] = extra_days
                    month_wise_absence_dates[month_list[start_date_object.month - 1]] = absence_dates
                    absence_dates = []
                    extra_days = 0
                    attendance_data = {}


                _, num_days = calendar.monthrange(end_date_object.year , end_date_object.month)

                for day in range(1 , end_date_object.day + 1):
                    date_obj = datetime(end_date_object.year, end_date_object.month, day).date()
                    date_str = date_obj.strftime("%y-%m-%d")

                    if date_obj.weekday() == 5:  # Saturday (Monday=0, ..., Saturday=5)
                        saturday_counter += 1
                        # Mark only the 1st, 3rd, and 5th Saturdays as holiday
                        if saturday_counter in (1, 3, 5):
                            if date_str in temp.keys():
                                attendance_data[date_str] = {"status" : "Holiday" , "InTime" : temp[date_str]["InTime"] , "OutTime" : temp[date_str]["OutTime"]}
                                extra_days += 1
                            else:
                                attendance_data[date_str] = {"status" : "Holiday" , "InTime" : "N/A" , "OutTime" : "N/A"}
                        else:
                            if date_str in temp.keys():                                
                                attendance_data[date_str] = {"status" : "Present" , "InTime" : temp[date_str]["InTime"] , "OutTime" : temp[date_str]["OutTime"]}
                            else:
                                attendance_data[date_str] = {"status" : "Absent" , "InTime" : "N/A" , "OutTime" : "N/A"}
                                absence_dates.append(date_str)
                    elif date_obj.weekday() == 6:  # Sunday (Sunday=6)
                        if date_str in temp.keys():
                                attendance_data[date_str] = {"status" : "Holiday" , "InTime" : temp[date_str]["InTime"] , "OutTime" : temp[date_str]["OutTime"]}
                        else:
                                attendance_data[date_str] = {"status" : "Holiday" , "InTime" : "N/A" , "OutTime" : "N/A"}
                    else:
                        if date_str in temp.keys():
                            attendance_data[date_str] = {"status" : "Present" , "InTime" : temp[date_str]["InTime"] , "OutTime" : temp[date_str]["OutTime"]}
                            extra_days += 1
                        else:
                            attendance_data[date_str] = {"status" : "Absent" , "InTime" : "N/A" , "OutTime" : "N/A"}
                            absence_dates.append(date_str)
                        
                
                attendance_data = json.dumps(attendance_data)
                month_wise_attendance[month_list[start_date_object.month - 1]] = attendance_data
                month_wise_extra_days[month_list[start_date_object.month - 1]] = extra_days
                month_wise_absence_dates[month_list[start_date_object.month - 1]] = absence_dates
                absence_dates = []
                extra_days = 0
                attendance_data = {}

                request.session['month_wise_attendance'] = month_wise_attendance
                request.session['month_wise_absence_dates'] = month_wise_absence_dates
                request.session['month_wise_extra_days'] = month_wise_extra_days

            else:
                print("No attendance data found for the employee")
                    
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
                cursor.execute("INSERT INTO absence_review (employee_id , date ,  explanation , status) VALUES (%s , %s, %s, %s)", [request.session.get('Id') ,date, explanation , "pending"])
                connection.commit()
            
            
            
            return redirect('employee_dashboard')
    else:
        form = AbsenceReviewForm()
        # Set the dropdown choices for GET requests as well.
        form.fields['date'].choices = [(d, d) for d in absence_data]
    
    return render(request, 'absence_review.html', {'form': form})



# def employee_dashboard(request):
#     # Placeholder data: Replace these with your actual logic.
#     # For example, attendance trend data could be a series of dates and attendance status.
#     dummy_attendance_labels = ["2025-01-01", "2025-01-02", "2025-01-03"]
#     dummy_attendance_data = [1, 0, 1]  # Example: 1 for present, 0 for absent
    
#     # Leave patterns: Number of leaves taken each month.
#     dummy_leave_labels = ["January", "February", "March", "April", "May", "June",
#                           "July", "August", "September", "October", "November", "December"]
#     dummy_leave_data = [2, 1, 0, 3, 1, 0, 2, 2, 1, 0, 1, 0]  # Example leave counts per month

#     context = {
#         'attendance_labels': dummy_attendance_labels,
#         'attendance_data': dummy_attendance_data,
#         'leave_labels': dummy_leave_labels,
#         'leave_data': dummy_leave_data,
#     }
#     return render(request, 'employee_dashboard.html', context)