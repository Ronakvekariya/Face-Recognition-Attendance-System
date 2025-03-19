from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.db import connection
from .forms import LoginForm, AbsenceReviewForm, SelectMonthForm, AddUser
from datetime import datetime, date
from calendar import monthrange
import calendar
import json
from collections import defaultdict

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
                        date_obj = datetime.date(start_date_object.year, month, day)
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

                request.session['month_wise_attendance'] = month_wise_attendance
                request.session['month_wise_absence_dates'] = month_wise_absence_dates
                request.session['month_wise_extra_days'] = month_wise_extra_days

            else:
                print("No attendance data found for the employee")
                    
        return render(request, 'employee_dashboard.html')
    return HttpResponse("Unauthorized", status=403)

def monthly_attendance(request):
    selected_month = request.GET.get('month')
    temp = request.session.get('month_wise_attendance', {})
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
            leave_requests.append({"id" : rows[1] , "full_name" :  str(result[1]) + " " + str(result[8]) + " " + str(result[9]) , "leave_type" : rows[5] , "job_position" :result[7] , "job_title" : result[6] , "message" : rows[3] , "status" : rows[4]})
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
    leave_type = request.GET.get("leave_type" , "")
    job_position = request.GET.get("job_position", "")
    job_title = request.GET.get("job_title", "")

    leave_requests = LeaveRequest.objects.all()

    if status:
        leave_requests = leave_requests.filter(status=status)
    if job_position:
        leave_requests = leave_requests.filter(job_position=job_position)
    if job_title:
        leave_requests = leave_requests.filter(job_title=job_title)


    return render(request, "leave_requests.html", {
        "leave_requests": leave_requests,
        "job_positions": job_position,
        "leave_types": job_title
    })

def update_leave_status(request):
    print("update leave status")