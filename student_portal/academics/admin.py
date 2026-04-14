from django.contrib import admin
from .models import (Student, Faculty, UserProfile, Announcement, Course,
                     Enrollment, Attendance, Assignment, Submission, Exam, Result, Timetable)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role']
    list_filter = ['role']
    search_fields = ['user__username']

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['user', 'registration_number', 'branch', 'semester']
    search_fields = ['user__username', 'registration_number', 'user__first_name', 'user__last_name']
    list_filter = ['branch', 'semester']

@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ['user', 'employee_id', 'department']
    search_fields = ['user__username', 'employee_id', 'user__first_name']
    list_filter = ['department']
    filter_horizontal = ['courses']

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_by', 'created_at', 'is_active', 'target_course']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'content']

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'credits', 'semester']
    search_fields = ['code', 'name']
    list_filter = ['semester', 'credits']

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'enrolled_date']
    search_fields = ['student__user__username', 'course__code']
    list_filter = ['enrolled_date', 'course']

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['enrollment', 'date', 'status']
    search_fields = ['enrollment__student__user__username', 'enrollment__course__code']
    list_filter = ['status', 'date']

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'due_date', 'max_marks']
    search_fields = ['title', 'course__code']
    list_filter = ['course', 'due_date']

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ['student', 'assignment', 'submitted_at', 'marks']
    search_fields = ['student__user__username', 'assignment__title']
    list_filter = ['submitted_at', 'assignment']

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ['name', 'course', 'exam_type', 'date', 'max_marks']
    search_fields = ['name', 'course__code']
    list_filter = ['exam_type', 'date', 'course']

@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ['student', 'exam', 'marks_obtained', 'grade']
    search_fields = ['student__user__username', 'exam__name']
    list_filter = ['grade', 'exam']

@admin.register(Timetable)
class TimetableAdmin(admin.ModelAdmin):
    list_display = ['course', 'day', 'start_time', 'end_time', 'room']
    search_fields = ['course__code', 'room']
    list_filter = ['day', 'course']
