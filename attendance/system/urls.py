from django.urls import path
from .views import login_view, logout_view, hr_dashboard, employee_dashboard,monthly_attendance,absence_review , get_attendance , dashboard_data , user_management , delete_user , add_user

urlpatterns = [
    path('', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('hr-dashboard/', hr_dashboard, name='hr_dashboard'),
    path('employee-dashboard/', employee_dashboard, name='employee_dashboard'),
    path('employee-dashboard/monthly-attendance/', monthly_attendance, name='monthly_attendance'),
    path('employee-dashboard/absence-review/', absence_review, name='absence_review'),
    path('employee-dashboard/get-attendance/', get_attendance, name='get_attendance'),
    path('employee-dashboard/dashboard-data/', dashboard_data, name='dashboard_data'),
    path('hr-dashboard/user-management/', user_management, name='user_management'),
    path('hr-dashboard/user-management/delete-user', delete_user, name='delete_user'),
    path('hr-dashboard/user-management/add-user', add_user, name='add_user'),
]
