from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from .views import login_view, logout_view, hr_dashboard, employee_dashboard,monthly_attendance,absence_review , get_attendance , dashboard_data , user_management , delete_user , add_user , leave_management , leave_requests , update_leave_status , request_display , employee_detail , chart_data , leave_requests_ajax , search_suggestions

urlpatterns = [
    path('', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('hr-dashboard/', hr_dashboard, name='hr_dashboard'),
    path('employee-dashboard/', employee_dashboard, name='employee_dashboard'),
    path('employee-dashboard/monthly-attendance/', monthly_attendance, name='monthly_attendance'),
    path('employee-dashboard/absence-review/', absence_review, name='absence_review'),
    path('employee-dashboard/get-attendance/', get_attendance, name='get_attendance'),
    path('employee-dashboard/dashboard-data/', dashboard_data, name='dashboard_data'),
    path('employee-dashboard/request-page', request_display, name='request_display'),
    path('hr-dashboard/user-management/', user_management, name='user_management'),
    path('hr-dashboard/employee-details/', employee_detail, name='employee_detail'),
    path('hr-dashboard/employee-details/<int:employee_id>/charts-data/', chart_data, name='chart_data'),
    path('hr-dashboard/employee-details/<int:employee_id>/leave-request-ajax/', leave_requests_ajax, name='leave_requests_ajax'),
    path('hr-dashboard/employee-details/search-suggestions', search_suggestions, name='search_suggestions'),
    path('hr-dashboard/user-management/delete-user', delete_user, name='delete_user'),
    path('hr-dashboard/user-management/add-user', add_user, name='add_user'),
    path('hr-dashboard/leave-management', leave_management, name='leave_management'),
    path('hr-dashboard/leave-requests', leave_requests, name='leave_requests'),
    path('hr-dashboard/update-leave-status', update_leave_status, name='update_leave_status'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += staticfiles_urlpatterns()