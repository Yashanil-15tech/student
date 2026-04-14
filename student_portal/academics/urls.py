from django.urls import path
from . import views

urlpatterns = [
    path('courses/', views.courses, name='courses'),
    path('course/<int:course_id>/', views.course_detail, name='course_detail'),
    path('attendance/', views.attendance, name='attendance'),
    path('assignments/', views.assignments, name='assignments'),
    path('assignment/<int:assignment_id>/submit/', views.submit_assignment, name='submit_assignment'),
    path('results/', views.results, name='results'),
    path('results/download/', views.download_academic_report, name='download_academic_report'),
    path('timetable/', views.timetable, name='timetable'),
    path('profile/', views.profile, name='profile'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    # Faculty
    path('faculty/profile/', views.faculty_profile, name='faculty_profile'),
    path('faculty/dashboard/', views.faculty_dashboard, name='faculty_dashboard'),
    path('faculty/attendance/<int:course_id>/', views.faculty_mark_attendance, name='faculty_mark_attendance'),
    path('faculty/marks/<int:course_id>/', views.faculty_upload_marks, name='faculty_upload_marks'),
    path('faculty/grade/<int:submission_id>/', views.faculty_grade_submission, name='faculty_grade_submission'),
    path('faculty/announcement/', views.faculty_create_announcement, name='faculty_create_announcement'),
]
