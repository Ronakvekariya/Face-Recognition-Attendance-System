from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.db import connection
from .forms import LoginForm, AbsenceReviewForm, SelectMonthForm, AddUser
from datetime import datetime, date
from calendar import monthrange
import calendar
import json
from collections import defaultdict
from django.http import JsonResponse
from django.views.decorators.http import require_POST ,require_GET
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template.loader import render_to_string


def employee_dashboard_details(request):
        attendance_data = []  # Placeholder for attendance data. Add your logic to fetch data.
        with connection.cursor() as cursor:
            cursor.execute("SELECT attendance FROM attendance_table where employee_id = %s", [request.session.get('Id')])
            result = cursor.fetchone()

            if result: 
                temp = json.loads(result[0])
                dates = list(temp.keys())
                sorted_dates = sorted(dates)
                start_date = sorted_dates[0]
                end_date = sorted_dates[-1]

                request.session['start-date'] = start_date
                request.session['end-date'] = end_date

                start_date_object = datetime.strptime(start_date, '%Y-%m-%d')
                end_date_object = datetime.strptime(end_date, '%Y-%m-%d')

                month_list = ["January", "February", "March", "April", "May", "June",
                              "July", "August", "September", "October", "November", "December"]
                month_wise_attendance = {}
                month_wise_extra_days = {}
                month_wise_absence_dates = {}
                absence_dates = []

                extra_days = 0
                saturday_counter = 0
                attendance_data = {}

                _, num_days = calendar.monthrange(start_date_object.year, start_date_object.month)

                for day in range(start_date_object.day, num_days + 1):
                    date_obj = datetime(start_date_object.year, start_date_object.month, day).date()
                    date_str = date_obj.strftime("%Y-%m-%d")
                    if date_obj.weekday() == 5:  # Saturday (Monday=0, ..., Saturday=5)
                        saturday_counter += 1
                        if saturday_counter in (1, 3, 5):
                            if date_str in dates:
                                attendance_data[date_str] = {"status": "Present", "InTime": temp[date_str]["InTime"], "OutTime": temp[date_str]["OutTime"]}
                                extra_days += 1
                            else:
                                attendance_data[date_str] = {"status": "Holiday", "InTime": "N/A", "OutTime": "N/A"}
                        else:
                            if date_str in dates:                                
                                attendance_data[date_str] = {"status": "Present", "InTime": temp[date_str]["InTime"], "OutTime": temp[date_str]["OutTime"]}
                            else:
                                attendance_data[date_str] = {"status": "Absent", "InTime": "N/A", "OutTime": "N/A"}
                                absence_dates.append(date_str)
                    elif date_obj.weekday() == 6:  # Sunday (Sunday=6)
                        if date_str in dates:
                            attendance_data[date_str] = {"status": "Present", "InTime": temp[date_str]["InTime"], "OutTime": temp[date_str]["OutTime"]}
                            extra_days += 1
                        else:
                            attendance_data[date_str] = {"status": "Holiday", "InTime": "N/A", "OutTime": "N/A"}
                    else:
                        if date_str in dates:
                            attendance_data[date_str] = {"status": "Present", "InTime": temp[date_str]["InTime"], "OutTime": temp[date_str]["OutTime"]}
                        else:
                            attendance_data[date_str] = {"status": "Absent", "InTime": "N/A", "OutTime": "N/A"}
                            absence_dates.append(date_str)

                attendance_data = json.dumps(attendance_data)
                month_wise_attendance[month_list[start_date_object.month - 1]] = attendance_data
                month_wise_extra_days[month_list[start_date_object.month - 1]] = extra_days
                month_wise_absence_dates[month_list[start_date_object.month - 1]] = absence_dates

                absence_dates = []
                extra_days = 0
                attendance_data = {}

                for month in range(start_date_object.month + 1, end_date_object.month):
                    _, num_days = calendar.monthrange(start_date_object.year, month)
                    for day in range(1, num_days + 1):
                        date_obj = date(start_date_object.year, month, day)
                        date_str = date_obj.strftime("%Y-%m-%d")
                        if date_obj.weekday() == 5:  # Saturday (Monday=0, ..., Saturday=5)
                            saturday_counter += 1
                            if saturday_counter in (1, 3, 5):
                                if date_str in dates:
                                    attendance_data[date_str] = {"status": "Holiday", "InTime": temp[date_str]["InTime"], "OutTime": temp[date_str]["OutTime"]}
                                    extra_days += 1
                                else:
                                    attendance_data[date_str] = {"status": "Holiday", "InTime": "N/A", "OutTime": "N/A"}
                            else:
                                if date_str in dates:                                
                                    attendance_data[date_str] = {"status": "Present", "InTime": temp[date_str]["InTime"], "OutTime": temp[date_str]["OutTime"]}
                                else:
                                    attendance_data[date_str] = {"status": "Absent", "InTime": "N/A", "OutTime": "N/A"}
                                    absence_dates.append(date_str)
                        elif date_obj.weekday() == 6:  # Sunday (Sunday=6)
                            if date_str in dates:
                                attendance_data[date_str] = {"status": "Holiday", "InTime": temp[date_str]["InTime"], "OutTime": temp[date_str]["OutTime"]}
                            else:
                                attendance_data[date_str] = {"status": "Holiday", "InTime": "N/A", "OutTime": "N/A"}
                        else:
                            if date_str in dates:
                                attendance_data[date_str] = {"status": "Present", "InTime": temp[date_str]["InTime"], "OutTime": temp[date_str]["OutTime"]}
                                extra_days += 1
                            else:
                                attendance_data[date_str] = {"status": "Absent", "InTime": "N/A", "OutTime": "N/A"} 
                                absence_dates.append(date_str)                       

                        attendance_data = json.dumps(attendance_data)
                        month_wise_attendance[month_list[month - 1]] = attendance_data
                        month_wise_extra_days[month_list[month - 1]] = extra_days
                        month_wise_absence_dates[month_list[month - 1]] = absence_dates
                        absence_dates = []
                        extra_days = 0
                        attendance_data = {}

                _, num_days = calendar.monthrange(end_date_object.year, end_date_object.month)

                for day in range(1, end_date_object.day + 1):
                    date_obj = datetime(end_date_object.year, end_date_object.month, day).date()
                    date_str = date_obj.strftime("%Y-%m-%d")
                    
                    if date_obj.weekday() == 5:  # Saturday (Monday=0, ..., Saturday=5)
                        saturday_counter += 1
                        if saturday_counter in (1, 3, 5):
                            if date_str in dates:
                                attendance_data[date_str] = {"status": "Holiday", "InTime": temp[date_str]["InTime"], "OutTime": temp[date_str]["OutTime"]}
                                extra_days += 1
                            else:
                                attendance_data[date_str] = {"status": "Holiday", "InTime": "N/A", "OutTime": "N/A"}
                        else:
                            if date_str in dates:                                
                                attendance_data[date_str] = {"status": "Present", "InTime": temp[date_str]["InTime"], "OutTime": temp[date_str]["OutTime"]}
                            else:
                                attendance_data[date_str] = {"status": "Absent", "InTime": "N/A", "OutTime": "N/A"}
                                absence_dates.append(date_str)
                    elif date_obj.weekday() == 6:  # Sunday (Sunday=6)
                        if date_str in dates:
                            attendance_data[date_str] = {"status": "Holiday", "InTime": temp[date_str]["InTime"], "OutTime": temp[date_str]["OutTime"]}
                        else:
                            attendance_data[date_str] = {"status": "Holiday", "InTime": "N/A", "OutTime": "N/A"}
                    else:
                        if date_str in dates:
                            attendance_data[date_str] = {"status": "Present", "InTime": temp[date_str]["InTime"], "OutTime": temp[date_str]["OutTime"]}
                            extra_days += 1
                        else:
                            attendance_data[date_str] = {"status": "Absent", "InTime": "N/A", "OutTime": "N/A"}
                            absence_dates.append(date_str)

                attendance_data = json.dumps(attendance_data)
                month_wise_attendance[month_list[end_date_object.month - 1]] = attendance_data
                month_wise_extra_days[month_list[end_date_object.month - 1]] = extra_days
                month_wise_absence_dates[month_list[end_date_object.month - 1]] = absence_dates
                absence_dates = []
                extra_days = 0
                attendance_data = {}

                print(month_wise_attendance)

                return month_wise_attendance, month_wise_absence_dates, month_wise_extra_days
            
            else:        
                return None, None, None


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            Id = form.cleaned_data['Id']    
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            with connection.cursor() as cursor:
                cursor.execute("SELECT role FROM system_user WHERE employee_id = %s AND username=%s AND password=%s", [Id, username, password])
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
        month_wise_attendance, month_wise_absence_dates, month_wise_extra_days = employee_dashboard_details(request)
        request.session['month_wise_attendance'] = month_wise_attendance
        request.session['month_wise_absence_dates'] = month_wise_absence_dates
        request.session['month_wise_extra_days'] = month_wise_extra_days                    
        return render(request, 'employee_dashboard.html')
    return HttpResponse("Unauthorized", status=403)

def monthly_attendance(request):
    selected_month = request.GET.get('month')
    temp , _ , _  = employee_dashboard_details(request)
    if selected_month:
        pass
        year = datetime.now().year
        attendance_data = json.loads(temp[selected_month])


        month_list = {"January":1, "February" : 2, "March" : 3, "April" : 4 , "May" : 5, "June" : 6,
                              "July" : 7, "August" : 8, "September" : 9, "October" : 10, "November" : 11, "December" : 12}

        # Get the month number
        month_num = month_list[selected_month]

       # Generate calendar weeks
        _, num_days = monthrange(year, month_num)
        first_day = datetime(year, month_num, 1)
        start_day = (first_day.weekday() - 6) % 7  # Adjust to start on Sunday
        calendar_weeks = []
        week = [0] * start_day
        for day in range(1, num_days + 1):
            week.append(day)
            if len(week) == 7:
                calendar_weeks.append(week)
                week = []
        if week:
            calendar_weeks.append(week)

        return render(request, 'monthly_attendance.html', {
            'months': list(temp.keys()),
            'selected_month': selected_month,
            'year': year,
            'calendar_weeks': calendar_weeks,
            'attendance_data': attendance_data,
            'month_num': month_num,
        })

    else:
        months = list(temp.keys())
        context = {'month_wise_attendance': request.session.get('month_wise_attendance', {}), 'months': months}
        return render(request, 'monthly_attendance.html', context)

def get_attendance(request):
    selected_month = request.GET.get('month')
    temp = request.session.get('month_wise_attendance', {})
    attendance = temp[selected_month]

    return render(request, 'monthly_attendance.html', {'attendance': attendance})

def absence_review(request):
    month_wise_attendance = request.session.get('month_wise_attendance', {})
    months = list(month_wise_attendance.keys())
    month_wise_absence_dates = request.session.get('month_wise_absence_dates', {})

    selected_month = None
    absence_data = []
    message = None

    month_form = SelectMonthForm(months=months)
    absence_form = AbsenceReviewForm()

    if request.method == "POST":
        print("POST Data:", request.POST)

        if 'month' in request.POST:
            month_form = SelectMonthForm(request.POST, months=months)
            if month_form.is_valid():
                selected_month = month_form.cleaned_data['month']
                absence_data = month_wise_absence_dates.get(selected_month, [])
                absence_form.fields['date'].choices = [(d, d) for d in absence_data]
            else:
                print("Month Form errors:", month_form.errors)
                message = "Invalid Month Selection"

        elif 'selected_month' in request.POST:
            selected_month = request.POST.get('selected_month')
            absence_data = month_wise_absence_dates.get(selected_month, [])
            absence_form = AbsenceReviewForm()
            absence_form.fields['date'].choices = [(d, d) for d in absence_data]
            absence_form = AbsenceReviewForm(request.POST)
            absence_form.fields['date'].choices = [(d, d) for d in absence_data]

            print("Review form is got")
            if absence_form.is_valid():
                print("form is valid")
                date = absence_form.cleaned_data['date']
                explanation = absence_form.cleaned_data['explanation']
                leave_type = absence_form.cleaned_data['leave_type']

                if datetime.strptime(date, "%Y-%m-%d") > datetime.today():
                    message = "You cannot submit a review for a future date."
                else:
                    employee_id = request.session.get('Id')
                    with connection.cursor() as cursor:
                        cursor.execute(
                            "SELECT employee_id, date FROM absence_review WHERE employee_id = %s AND date = %s",
                            [employee_id, date]
                        )
                        result = cursor.fetchone()
                        if result:
                            message = "You have already submitted an explanation for this date."
                        else:
                            cursor.execute(
                                "INSERT INTO absence_review (employee_id, date, explanation, status , leave_type , hr_response) VALUES (%s, %s, %s, %s, %s , %s)",
                                [employee_id, date, explanation, "pending", leave_type , "HR has not responded yet"]
                            )
                            connection.commit()
                            return redirect('employee_dashboard')
            else:
                print("Absence Form errors:", absence_form.errors)
                message = "Form submission failed. Please check your input."

    if selected_month and absence_data:
        absence_form.fields['date'].choices = [(d, d) for d in absence_data]

    return render(request, 'absence_review.html', {
        'month_form': month_form,
        'form': absence_form,
        'months': months,
        'selected_month': selected_month,
        'message': message
    })

# def user_management(request):
#     if request.session.get('role') == 'HR':
#         result_hr, result_employee, hr_count, employee_count = UpdateObject(request)

#         if result_hr and result_employee:
#             context = {"hr_count": len(result_hr), "employee_count": len(result_employee), "employee_users": result_employee, "hr_users": result_hr}
#         else:
#             context = {"hr_count": None, "employee_count": None, "employee_users": None, "hr_users": None}

#         return render(request, 'user_management.html', context=context)
#     return HttpResponse("Unauthorized", status=403)

def delete_user(request):
    user_id = request.GET.get('user_id')
    context = {"hr_count": request.session.get("hr_count"), "employee_count": request.session.get("employee_count"), "employee_users": request.session.get("hr_users"), "hr_users": request.session.get("employee_users")}
    if user_id:
        user_id = int(user_id)
        with connection.cursor() as cursor:
            try:
                cursor.execute("DELETE FROM system_user WHERE employee_id = %s", [user_id])
                connection.commit()

                result_hr, result_employee, hr_count, employee_count = UpdateObject(request)
                context['hr_users'] = result_hr
                context['employee_users'] = result_employee
                context['hr_count'] = len(result_hr)
                context['employee_count'] = len(result_employee)
                context["status"] = "User deleted successfully"
                return render(request, 'user_management.html', context=context)
            except Exception as e:
                context["status"] = "Failed to delete user"
                return render(request, 'user_management.html', context=context)
    else:
        context["status"] = "User ID not provided"
        return render(request, 'user_management.html', context=context)

    year = 2025  # Default year
    month_num = 0  # Default month number

    if selected_month and selected_month in month_wise_attendance:
        # Parse the JSON string stored for the selected month.
        attendance_data = json.loads(month_wise_attendance[selected_month])
        # Try to extract the year and month number from one of the keys.
        if attendance_data:
            first_date = list(attendance_data.keys())[0]  # e.g., "2025-02-01"
            parts = first_date.split('-')
            if len(parts) >= 2:
                year = int(parts[0])
                month_num = int(parts[1])
            else:
                month_num = 1
        else:
            # Fallback: Map month name to number.
            month_map = {
                "January": 1, "February": 2, "March": 3, "April": 4,
                "May": 5, "June": 6, "July": 7, "August": 8,
                "September": 9, "October": 10, "November": 11, "December": 12
            }
            month_num = month_map.get(selected_month, 1)
        
        # Set the first weekday to Sunday so that the grid aligns with your header.
        calendar.setfirstweekday(calendar.SUNDAY)
        # Generate the calendar grid (weeks) for the given year and month.
        calendar_weeks = calendar.monthcalendar(year, month_num)
    else:
        selected_month = ''  # No valid month selected; no calendar will be shown.
    
    context = {
        'months': months,
        'selected_month': selected_month,
        'calendar_weeks': calendar_weeks,
        'attendance_data': attendance_data,
        'year': year,
        'month_num': month_num,
    }
    return render(request, 'monthly_attendance.html', context)


def dashboard_data(request):
    # Retrieve start and end date strings from the GET parameters
    start_date_str = request.GET.get('startDate')
    end_date_str = request.GET.get('endDate')
    message = ''

    # Convert the date strings to date objects (if provided)
    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else None
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else None
    except ValueError:
        # If the date format is incorrect, return an error response
        return JsonResponse({'error': 'Invalid date format. Please use YYYY-MM-DD.'}, status=400)
    
    
    start_date_employee = datetime.strptime(request.session.get('start-date'), '%Y-%m-%d').date()
    end_date_employee = datetime.strptime(request.session.get('end-date') , '%Y-%m-%d').date()

    # Check if the end date is provided and greater than the current date
    if end_date and end_date > end_date_employee:
        message = f"End date is greater than the employee's last attendance. This is {end_date_employee} last attendance date"
    elif start_date and start_date < start_date_employee:
        message = f"Start date is less than employee's first attendance. This is {start_date_employee} first attendance date"

    month_wise_attendance = request.session.get('month_wise_attendance' , {})
    month_wise_absence_dates =  request.session.get('month_wise_absence_dates' , {})
    # Convert start and end dates to the correct format
    start_date = datetime.strptime(f"{start_date_str}", "%Y-%m-%d")
    end_date = datetime.strptime(f"{end_date_str}", "%Y-%m-%d")

    attendance_data = []
    attendance_labels = []
    leave_data = []
    leave_labels = []

    month_wise_absence_dates = request.session.get('month_wise_absence_dates' , {})

    for month , details in month_wise_absence_dates.items():
        leave_data.append(month)
        leave_labels.append(len(details))

    # Iterate through each month's data
    for month_json in month_wise_attendance.values():
        month_data = json.loads(month_json)
        for date_str, details in month_data.items():
            current_date = datetime.strptime(date_str, "%Y-%m-%d")
            # Check if the date is within the specified range
            if start_date <= current_date <= end_date:
                status = details['status']
                attendance_data.append(date_str)
                if status == 'Holiday':
                    continue
                elif status == 'Absent':
                    attendance_labels.append(0)
                else:
                    attendance_labels.append(1)
    
    # For demonstration, we're just reading from session.
    response_data = {
        'attendance_labels': attendance_labels,
        'attendance_data': attendance_data,
        'leave_labels': leave_labels,
        'leave_data': leave_data , 
        'message': message
    }
    return JsonResponse(response_data)

def UpdateObject(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM system_user where role = 'HR'")
        result_hr = cursor.fetchall()
            
        cursor.execute("SELECT * FROM system_user where role = 'Employee'")
        result_employee = cursor.fetchall()

        if result_hr and result_employee:
            # request.session['hr_users'] = result_hr
            # request.session['employee_users'] = result_employee
            # request.session['hr_count'] = len(result_hr)
            # request.session['employee_count'] = len(result_employee)
            return result_hr , result_employee , len(result_hr) , len(result_employee)
        else:
            return None , None , None , None

def user_management(request):
    if request.session.get('role') == 'HR':

        result_hr , result_employee , hr_count , employee_count = UpdateObject(request)

        if result_hr and result_employee:
            context = {"hr_count" : len(result_hr) , "employee_count" : len(result_employee) , "employee_users" : result_employee  , "hr_users" : result_hr}
        else:
            context = {"hr_count" : None , "employee_count" : None , "employee_users" : None  , "hr_users" : None}

        return render(request, 'user_management.html' , context=context)
    return HttpResponse("Unauthorized", status=403)


def delete_user(request):
    user_id = request.GET.get('user_id')
    context = {"hr_count" : request.session.get("hr_count") , "employee_count" : request.session.get("employee_count")  , "employee_users" : request.session.get("hr_users")  , "hr_users" : request.session.get("employee_users")}
    if user_id:
        user_id = int(user_id)
        with connection.cursor() as cursor:
            try:
                cursor.execute("DELETE FROM system_user WHERE employee_id = %s", [user_id])
                connection.commit()

                result_hr , result_employee , hr_count , employee_count = UpdateObject(request)
                context['hr_users'] = result_hr
                context['employee_users'] = result_employee
                context['hr_count'] = len(result_hr)
                context['employee_count'] = len(result_employee)
                context["status"] = "User deleted successfully"
                return render(request, 'user_management.html' , context=context)
            except Exception as e:
                context["status"] = "Failed to delete user"
                return render(request, 'user_management.html' , context=context)
    else:
        context["status"] = "User ID not provided"
        return render(request, 'user_management.html' , context=context)
    

def add_user(request):
    if request.method == 'POST':
        form = AddUser(request.POST)
        print("post request got")
        if form.is_valid():
            print("processing form")
            userid = form.cleaned_data['userid']
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            role = form.cleaned_data['role']
            email = form.cleaned_data['email']
            job_title = form.cleaned_data['job_title']
            job_position = form.cleaned_data['job_position']
            mobile_number = form.cleaned_data['mobile_number']
            middlename = form.cleaned_data['middlename']
            surname = form.cleaned_data['surname']
            with connection.cursor() as cursor:
                cursor.execute("INSERT INTO system_user (username, password, role , employee_id, email , job_title , job_position , middlename , surname , mobilenumber) VALUES (%s, %s, %s, %s , %s , %s , %s, %s , %s , %s)", [username, password, role , userid , email , job_title , job_position , middlename , surname , mobile_number])
                connection.commit()
                return redirect('user_management')
        else:
            return render(request, 'add_user.html' , {'form' : form , 'status' : "Invalid form data"})
    # else:
        # form = AddUser()
    return render(request, 'add_user.html', {'form': AddUser(), 'status': "Form is Empty"})

def get_leave_data():
    pass
    # return result

def leave_management(request):
    leave_type = ['Sick Leave' , 'Paid Leave' , 'Informed Leave']
    job_positions = ['Fresher' , 'Junior Developer' , 'Senior Developer' ,'Managing Director' , 'Deputy General Manager' ]
    job_title = ['.NET Developer' , 'ERP' , 'HRMS' , 'Data Scientist' , 'React Developer' , 'DBA']
    leave_requests = []
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM absence_review")
        absent_result = cursor.fetchall()

        for rows in absent_result:
            cursor.execute("select * from system_user where employee_id = %s" , [rows[1]])
            result = cursor.fetchone()
            leave_requests.append({"id" : rows[1] , "full_name" :  str(result[1]) + " " + str(result[8]) + " " + str(result[9]) , "leave_type" : rows[5] , "job_position" :result[7] , "job_title" : result[6] , "message" : rows[3] , "status" : rows[4] , "date" : rows[2] , "mobile" : result[10] , "email" : result[5]})
    grouped_leave_requests = defaultdict(list)
    for leave in leave_requests:
        grouped_leave_requests[leave['id']].append(leave)

    leave_requests = []

    for ky , val in grouped_leave_requests.items():
        for index in val:
            leave_requests.append(index)
    result = {'leave_type' : leave_type , 'job_positions' : job_positions , 'job_title' : job_title , "leave_requests": leave_requests }
    return render(request, 'leave_management.html' , context=result)

def leave_requests(request):
    if request.method == "POST":
        leave_type = request.POST.get("leave_type" , "")
        job_position = request.POST.get("job_position", "")
        job_title = request.POST.get("job_title", "")

        print("Leave Type:", leave_type)
        print("Job Position:", job_position)
        print("Job Title:", job_title)

        leave_requests_lst = []

        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM absence_review")
            absent_result = cursor.fetchall()
        
            for rows in absent_result:
                cursor.execute("select * from system_user where employee_id = %s" , [rows[1]])
                result = cursor.fetchone()
                if leave_type and leave_type == rows[5]:
                    leave_requests_lst.append({"id" : rows[1] , "full_name" :  str(result[1]) + " " + str(result[8]) + " " + str(result[9]) , "leave_type" : rows[5] , "job_position" :result[7] , "job_title" : result[6] , "message" : rows[3] , "status" : rows[4] , "date" : rows[2] , "mobile" : result[10] , "email" : result[5]})
                if job_position and job_position == result[7]:
                    leave_requests_lst.append({"id" : rows[1] , "full_name" :  str(result[1]) + " " + str(result[8]) + " " + str(result[9]) , "leave_type" : rows[5] , "job_position" :result[7] , "job_title" : result[6] , "message" : rows[3] , "status" : rows[4] , "date" : rows[2] , "mobile" : result[10] , "email" : result[5]})
                if job_title and job_title == result[6]:
                    leave_requests_lst.append({"id" : rows[1] , "full_name" :  str(result[1]) + " " + str(result[8]) + " " + str(result[9]) , "leave_type" : rows[5] , "job_position" :result[7] , "job_title" : result[6] , "message" : rows[3] , "status" : rows[4] , "date" : rows[2] , "mobile" : result[10] , "email" : result[5]})

        
        leave_type = ['Sick Leave' , 'Paid Leave' , 'Informed Leave']
        job_positions = ['Fresher' , 'Junior Developer' , 'Senior Developer' ,'Managing Director' , 'Deputy General Manager' ]
        job_title = ['.NET Developer' , 'ERP' , 'HRMS' , 'Data Scientist' , 'React Developer' , 'DBA']

        grouped_leave_requests = defaultdict(list)

        for leave in leave_requests_lst:
            grouped_leave_requests[leave['id']].append(leave)

        leave_requests_lst = []

        for ky , val in grouped_leave_requests.items():
            for index in val:
                leave_requests_lst.append(index)

        return render(request, "leave_management.html", {
            "leave_requests": leave_requests_lst,
            "job_positions": job_positions,
            "job_title": job_title,
            "leave_type": leave_type,
        })

@csrf_exempt  # Use this if you're not using CSRF tokens; otherwise, ensure CSRF tokens are included
def update_leave_status(request):
    if request.method == "POST":
        try:
            # Parse the JSON data from the request body
            data = json.loads(request.body)
            leave_id = data.get('leave_id')
            leave_date = data.get('leave_date')
            action = data.get('action')
            rejection_reason = data.get('rejection_reason', None)

            # Convert the date string to a datetime object
            date_object = datetime.strptime(leave_date, "%b. %d, %Y")

            # Format the datetime object to the desired string format
            leave_date = date_object.strftime("%Y-%m-%d")

            print("Leave ID:", leave_id)
            print("Action:", action)
            print(leave_date)
            print(rejection_reason)

            with connection.cursor() as cursor:
                if action == "approve":
                    cursor.execute("UPDATE absence_review SET status = %s , hr_response = %s WHERE employee_id = %s and date = %s ", ["approved", "HR is approved the request",leave_id , leave_date])
                    result1 = cursor.rowcount
                    if cursor.rowcount == 0:
                        return JsonResponse({'success': False, 'error': 'Query Execution failed'})
                    cursor.execute("select attendance from attendance_table where employee_id = %s" , [leave_id])
                    attendance = cursor.fetchone()[0]
                    if attendance:
                        attendance = json.loads(attendance)
                        # Time strings
                        time_string_1 = ["09:00:00"]
                        time_string_2 = ["17:45:00"]

                        attendance[leave_date] = {'InTime' : time_string_1  , 'OutTime' : time_string_2}
                        cursor.execute('UPDATE attendance_table SET attendance = %s WHERE employee_id = %s', [json.dumps(attendance),leave_id])
                        result2 = cursor.rowcount

                        if result1 == 0:
                            return JsonResponse({'success': False, 'error': 'Query Execution failed'})
                            connection.rollback()
                    else:
                        return JsonResponse({'success': False, 'error': 'No Attendanec data found for the employee ' + leave_id})
                elif action == "reject":
                    cursor.execute("UPDATE absence_review SET status = %s , hr_response = %s WHERE employee_id = %s and date = %s ", ["rejected", rejection_reason , leave_id , leave_date])
                    if cursor.rowcount == 0:
                        return JsonResponse({'success': False, 'error': 'Query Execution failed'})
            # Return a success response
            return JsonResponse({'success': True})
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON data'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method'})


def request_display(request):
    # Get the employee ID from the session
    requests_qs = []
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM absence_review WHERE employee_id = %s", [request.session['Id']])
        result = cursor.fetchall()

        if result:
            for row in result:
                requests_qs.append(list(row))
            requests_qs = sorted(requests_qs, key=lambda x: x[2])        
    
    # Convert each request from list to dictionary for easier access in the template.
    requests_list = []
    for req in requests_qs:
        request_dict = {
            'id': req[0],
            'employee_id': req[1],
            'date': req[2],
            'explanation': req[3],
            'hr_decision_status': req[4],
            'type_of_leave': req[5],
            'hr_response_message': req[6],
        }
        requests_list.append(request_dict)
        
    # Group requests by month (formatted as "Month Year", e.g., "January 2025")
    monthly_groups = defaultdict(list)
    for req in requests_list:
        month_str = req['date'].strftime("%B %Y")
        monthly_groups[month_str].append(req)
        
    # Paginate each monthly group: three requests per page.
    monthly_groups_paginated = {}
    for month, requests in monthly_groups.items():
        paginator = Paginator(requests, 3)
        
        # If the current query parameter 'month' matches this group, try to get its 'page' parameter; else default to page 1.
        if request.GET.get('month') == month:
            page = request.GET.get('page')
        else:
            page = 1
        
        try:
            paginated_requests = paginator.page(page)
        except PageNotAnInteger:
            paginated_requests = paginator.page(1)
        except EmptyPage:
            paginated_requests = paginator.page(paginator.num_pages)
        
        monthly_groups_paginated[month] = paginated_requests
    
    context = {
        'monthly_groups': monthly_groups_paginated,
    }
    
    return render(request, 'request_display.html' , context=context)

def get_leave_requests(employee_id, page=1, filters=None):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM absence_review WHERE employee_id = %s", [employee_id])
        leave_requests = cursor.fetchall()
        leave_requests_list = []
        count = 0

        for req in leave_requests:
            count +=1
            leave_requests_list.append({'id':count , 'date' : req[2] , 'explanation' : req[3] , 'status' : req[4] , 'leave_type' : req[5] , 'hr_response' : req[6]})
        
         # Filter the results if filters are provided.
        if filters:
            if 'leave_type' in filters and filters['leave_type']:
                leave_requests_list = [r for r in leave_requests_list if r['leave_type'] == filters['leave_type']]
            if 'status' in filters and filters['status']:
                leave_requests_list = [r for r in leave_requests_list if r['status'] == filters['status']]
        
        paginator = Paginator(leave_requests_list, 5)
        try:
            leave_requests_page = paginator.page(page)
        except PageNotAnInteger:
            leave_requests_page = paginator.page(1)
        except EmptyPage:
            leave_requests_page = paginator.page(paginator.num_pages)
        
        return leave_requests_page


def employee_detail(request):
    employee_id = request.POST.get('search' , '')
    print(employee_id)
    # Fetch initial leave request data for the employee (e.g., first 5 entries)
    leave_requests = get_leave_requests(employee_id, page=1)
    employee_details = {}
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM system_user WHERE employee_id = %s", [employee_id])
        employee_data = cursor.fetchone()
        print(employee_data)
        employee_details['name'] = employee_data[1] + " " + employee_data[8] + " " + employee_data[9]
        employee_details['photo_url'] = 'images/download (1).jpeg'
        employee_details['job_title'] = employee_data[6]
        employee_details['email'] = employee_data[5]
        employee_details['phone'] = employee_data[10]

    context = {
        'employee_id': employee_id,
        'leave_requests': leave_requests,
        'employee_details': employee_details
        # Include any initial data you want to show
    }
    return render(request, 'employee_details.html' , context=context)

@require_GET
def search_suggestions(request ):
    query = request.GET.get('query', '')
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM system_user")
        result = cursor.fetchall()  
        suggestions = []
        for row in result:
            suggestions.append({'employee_id' :row[4] , 'name':row[1] ,'job_title': row[6]})
        
            # Filter the list based on the query (this is a simple case-insensitive search)
    filtered = [
        emp for emp in suggestions
        if query.lower() in emp['name'].lower() or query.lower() in emp['job_title'].lower()
    ]
    return JsonResponse(filtered, safe=False)

@require_GET
def chart_data(request, employee_id):
    approved , rejected = 0 , 0
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM absence_review WHERE employee_id = %s", [employee_id])
        leave_requests = cursor.fetchall()

        for leave_request in leave_requests:
            if leave_request[4] == "approved":
                approved += 1
            elif leave_request[4] == "rejected":
                rejected += 1
            
        cursor.execute("select attendance from attendance_table where employee_id = %s" , [employee_id])

        attendance_data = cursor.fetchone()
        attendance_data = json.loads(attendance_data[0])


        monthly_entry_count = defaultdict(int)

        for data_Str , times in attendance_data.items():
            month = datetime.strptime(data_Str, "%Y-%m-%d").strftime("%B")
            monthly_entry_count[month] += 1
        monthly_entry_count = dict(monthly_entry_count)

        final_dict = []

        for key , value in monthly_entry_count.items():
            final_dict.append({'month' : key , 'present_days' : value})
    # Example data structure:
    data = {
        'pie': {
            'approved': approved,
            'rejected': rejected,
            'pending' : len(leave_requests) - (approved + rejected)
        },
        'bar': final_dict,
        'total_requests': len(leave_requests),  # For the simple graph/image
    }
    # In practice, fetch these values based on your queries.
    return JsonResponse(data)


def leave_requests_ajax(request, employee_id):
    # Extract filtering parameters and pagination from request.GET or request.POST
    page = request.GET.get('page', 1)
    # For example, filtering parameters can be: job_title, leave_type, etc.
    filters = {
        'status': request.GET.get('status', None),
        'leave_type': request.GET.get('leave_type', None),
        # Add other filters as needed
    }
    print(filters)
    leave_requests = get_leave_requests(employee_id, page=page, filters=filters)
    # Render a partial template that represents the leave request table
    table_html = render_to_string('leave_request_table.html', {'leave_requests': leave_requests})
    return JsonResponse({'table_html': table_html})



