from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

ROLE_STUDENT = 'student'
ROLE_FACULTY = 'faculty'
ROLE_ADMIN = 'admin'
ROLE_CHOICES = [(ROLE_STUDENT, 'Student'), (ROLE_FACULTY, 'Faculty'), (ROLE_ADMIN, 'Admin')]

ATTENDANCE_THRESHOLD = 75  # percentage below which shortage alert is shown


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=ROLE_STUDENT)

    def __str__(self):
        return f"{self.user.username} ({self.role})"


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    registration_number = models.CharField(max_length=20, unique=True)
    branch = models.CharField(max_length=100)
    semester = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(8)])
    phone = models.CharField(max_length=15)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.registration_number}"

    def calculate_gpa(self, semester):
        """Calculate GPA for a specific semester."""
        results = Result.objects.filter(student=self, exam__course__semester=semester)
        if not results:
            return None
        total_weighted = sum(r.grade_points() * r.exam.course.credits for r in results)
        total_credits = sum(r.exam.course.credits for r in results)
        return round(total_weighted / total_credits, 2) if total_credits else None

    def calculate_cgpa(self):
        """Calculate cumulative GPA across all semesters."""
        results = Result.objects.filter(student=self).select_related('exam__course')
        if not results:
            return None
        total_weighted = sum(r.grade_points() * r.exam.course.credits for r in results)
        total_credits = sum(r.exam.course.credits for r in results)
        return round(total_weighted / total_credits, 2) if total_credits else None


class Faculty(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    employee_id = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, blank=True)
    profile_picture = models.ImageField(upload_to='faculty_profiles/', blank=True, null=True)
    courses = models.ManyToManyField('Course', blank=True, related_name='faculty_members')

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.employee_id}"

    class Meta:
        verbose_name_plural = 'Faculty'


class Announcement(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    target_course = models.ForeignKey('Course', on_delete=models.SET_NULL, null=True, blank=True,
                                      help_text="Leave blank to show to all students")

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']

class Course(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=200)
    credits = models.IntegerField(validators=[MinValueValidator(1)])
    semester = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(8)])
    description = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.code} - {self.name}"

class Enrollment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    enrolled_date = models.DateField(auto_now_add=True)
    
    class Meta:
        unique_together = ['student', 'course']
    
    def __str__(self):
        return f"{self.student.user.username} - {self.course.code}"

class Attendance(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=10, choices=[
        ('Present', 'Present'),
        ('Absent', 'Absent'),
        ('Late', 'Late')
    ])
    remarks = models.CharField(max_length=200, blank=True)
    
    class Meta:
        unique_together = ['enrollment', 'date']
    
    def __str__(self):
        return f"{self.enrollment.student.user.username} - {self.enrollment.course.code} - {self.date}"

class Assignment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    due_date = models.DateTimeField()
    max_marks = models.IntegerField(validators=[MinValueValidator(1)])
    file = models.FileField(upload_to='assignments/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.course.code} - {self.title}"

class Submission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    file = models.FileField(upload_to='submissions/')
    submitted_at = models.DateTimeField(auto_now_add=True)
    marks = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0)])
    feedback = models.TextField(blank=True)
    
    class Meta:
        unique_together = ['assignment', 'student']
    
    def __str__(self):
        return f"{self.student.user.username} - {self.assignment.title}"

class Exam(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    exam_type = models.CharField(max_length=50, choices=[
        ('Mid-Term', 'Mid-Term'),
        ('End-Term', 'End-Term'),
        ('Quiz', 'Quiz'),
        ('Assignment', 'Assignment')
    ])
    date = models.DateField()
    max_marks = models.IntegerField(validators=[MinValueValidator(1)])
    
    def __str__(self):
        return f"{self.course.code} - {self.name}"

class Result(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    marks_obtained = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0)])
    grade = models.CharField(max_length=2, blank=True)
    
    class Meta:
        unique_together = ['exam', 'student']
    
    def save(self, *args, **kwargs):
        percentage = (self.marks_obtained / self.exam.max_marks) * 100
        if percentage >= 90:
            self.grade = 'A+'
        elif percentage >= 80:
            self.grade = 'A'
        elif percentage >= 70:
            self.grade = 'B+'
        elif percentage >= 60:
            self.grade = 'B'
        elif percentage >= 50:
            self.grade = 'C'
        elif percentage >= 40:
            self.grade = 'D'
        else:
            self.grade = 'F'
        super().save(*args, **kwargs)

    def grade_points(self):
        grade_map = {'A+': 10, 'A': 9, 'B+': 8, 'B': 7, 'C': 6, 'D': 5, 'F': 0}
        return grade_map.get(self.grade, 0)

    def __str__(self):
        return f"{self.student.user.username} - {self.exam.name} - {self.marks_obtained}/{self.exam.max_marks}"

class Timetable(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    day = models.CharField(max_length=10, choices=[
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday')
    ])
    start_time = models.TimeField()
    end_time = models.TimeField()
    room = models.CharField(max_length=50)
    
    def __str__(self):
        return f"{self.course.code} - {self.day} - {self.start_time}"
