from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib import messages
from django.db.models import Avg, Count, Q
from django.utils import timezone
from django.http import HttpResponse
from .models import (Student, Faculty, UserProfile, Announcement, Course,
                     Enrollment, Attendance, Assignment, Submission, Exam, Result, Timetable,
                     ROLE_STUDENT, ROLE_FACULTY, ATTENDANCE_THRESHOLD)
from datetime import date
import io

# ─── Helpers ─────────────────────────────────────────────────────────────────

def _get_role(user):
    try:
        return user.profile.role
    except UserProfile.DoesNotExist:
        try:
            user.faculty
            UserProfile.objects.get_or_create(user=user, defaults={'role': ROLE_FACULTY})
            return ROLE_FACULTY
        except Faculty.DoesNotExist:
            pass
        return ROLE_STUDENT


def _require_faculty(request):
    if _get_role(request.user) not in ('faculty', 'admin'):
        messages.error(request, 'Access denied. Faculty only.')
        return None
    try:
        return request.user.faculty
    except Faculty.DoesNotExist:
        messages.error(request, 'Faculty profile not found.')
        return None


def _attendance_stats_for_student(student):
    enrollments = Enrollment.objects.filter(student=student).select_related('course')
    stats = []
    shortage = []
    for enrollment in enrollments:
        total = Attendance.objects.filter(enrollment=enrollment).count()
        present = Attendance.objects.filter(enrollment=enrollment, status='Present').count()
        pct = round((present / total * 100), 2) if total > 0 else 0
        stat = {'course': enrollment.course, 'percentage': pct, 'present': present, 'total': total}
        stats.append(stat)
        if total > 0 and pct < ATTENDANCE_THRESHOLD:
            shortage.append(stat)
    return stats, shortage


# ─── Auth / Home ─────────────────────────────────────────────────────────────

def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'base/home.html')


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        role = request.POST.get('role', ROLE_STUDENT)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user, role=role)
            login(request, user)
            messages.success(request, 'Registration successful! Please complete your profile.')
            if role == ROLE_FACULTY:
                return redirect('faculty_profile_setup')
            return redirect('profile_setup')
    else:
        form = UserCreationForm()
    return render(request, 'auth/register.html', {'form': form})


@login_required
def profile_setup(request):
    try:
        _ = request.user.student
        return redirect('dashboard')
    except Student.DoesNotExist:
        pass

    if request.method == 'POST':
        reg_no = request.POST.get('registration_number', '').strip()
        branch = request.POST.get('branch', '').strip()
        semester = request.POST.get('semester', '').strip()
        phone = request.POST.get('phone', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()

        errors = []
        if not reg_no:
            errors.append('Registration number is required.')
        elif Student.objects.filter(registration_number=reg_no).exists():
            errors.append('Registration number already in use.')
        if not branch:
            errors.append('Branch is required.')
        if not semester or not semester.isdigit() or not (1 <= int(semester) <= 8):
            errors.append('Semester must be between 1 and 8.')

        if errors:
            for e in errors:
                messages.error(request, e)
        else:
            request.user.first_name = first_name
            request.user.last_name = last_name
            request.user.save()
            Student.objects.create(
                user=request.user, registration_number=reg_no,
                branch=branch, semester=int(semester), phone=phone,
            )
            messages.success(request, 'Profile created successfully!')
            return redirect('dashboard')

    return render(request, 'academics/profile_setup.html')


@login_required
def faculty_profile_setup(request):
    try:
        _ = request.user.faculty
        return redirect('faculty_dashboard')
    except Faculty.DoesNotExist:
        pass

    if request.method == 'POST':
        emp_id = request.POST.get('employee_id', '').strip()
        department = request.POST.get('department', '').strip()
        phone = request.POST.get('phone', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()

        errors = []
        if not emp_id:
            errors.append('Employee ID is required.')
        elif Faculty.objects.filter(employee_id=emp_id).exists():
            errors.append('Employee ID already in use.')
        if not department:
            errors.append('Department is required.')

        if errors:
            for e in errors:
                messages.error(request, e)
        else:
            request.user.first_name = first_name
            request.user.last_name = last_name
            request.user.save()
            Faculty.objects.create(user=request.user, employee_id=emp_id, department=department, phone=phone)
            messages.success(request, 'Faculty profile created successfully!')
            return redirect('faculty_dashboard')

    return render(request, 'academics/faculty_profile_setup.html')

@login_required
def faculty_profile(request):
    try:
        faculty = request.user.faculty
    except Faculty.DoesNotExist:
        return redirect('faculty_profile_setup')

    if request.method == 'POST':
        faculty.department = request.POST.get('department', faculty.department)
        faculty.phone = request.POST.get('phone', faculty.phone)
        if request.FILES.get('profile_picture'):
            faculty.profile_picture = request.FILES['profile_picture']
        faculty.user.first_name = request.POST.get('first_name', faculty.user.first_name)
        faculty.user.last_name = request.POST.get('last_name', faculty.user.last_name)
        faculty.user.email = request.POST.get('email', faculty.user.email)
        faculty.user.save()
        faculty.save()
        messages.success(request, 'Profile updated successfully.')
        return redirect('faculty_profile')

    return render(request, 'academics/faculty_profile.html', {'faculty': faculty})
# ─── Student Dashboard ────────────────────────────────────────────────────────

@login_required
def dashboard(request):
    role = _get_role(request.user)
    if role == ROLE_FACULTY:
        return redirect('faculty_dashboard')

    try:
        request.user.faculty
        return redirect('faculty_dashboard')
    except Faculty.DoesNotExist:
        pass

    try:
        student = request.user.student
    except Student.DoesNotExist:
        messages.warning(request, 'Please complete your student profile.')
        return redirect('profile_setup')

    enrollments = Enrollment.objects.filter(student=student).select_related('course')
    courses = [e.course for e in enrollments]
    attendance_stats, shortage_alerts = _attendance_stats_for_student(student)

    recent_assignments = Assignment.objects.filter(course__in=courses).order_by('-due_date')[:5]
    upcoming_exams = Exam.objects.filter(course__in=courses, date__gte=date.today()).order_by('date')[:5]
    recent_results = Result.objects.filter(student=student).select_related('exam', 'exam__course').order_by('-exam__date')[:5]

    announcements = Announcement.objects.filter(is_active=True).filter(
        Q(target_course__in=courses) | Q(target_course__isnull=True)
    ).order_by('-created_at')[:5]

    cgpa = student.calculate_cgpa()

    context = {
        'student': student, 'courses': courses, 'attendance_stats': attendance_stats,
        'shortage_alerts': shortage_alerts, 'recent_assignments': recent_assignments,
        'upcoming_exams': upcoming_exams, 'recent_results': recent_results,
        'announcements': announcements, 'cgpa': cgpa,
    }
    return render(request, 'academics/dashboard.html', context)


# ─── Faculty Dashboard ────────────────────────────────────────────────────────

@login_required
def faculty_dashboard(request):
    role = _get_role(request.user)
    if role not in ('faculty', 'admin'):
        return redirect('dashboard')

    try:
        faculty = request.user.faculty
    except Faculty.DoesNotExist:
        messages.warning(request, 'Please complete your faculty profile.')
        return redirect('faculty_profile_setup')

    courses = faculty.courses.all()
    if not courses:
        courses = Course.objects.all()

    enrollment_count = Enrollment.objects.filter(course__in=courses).count()
    pending_submissions = Submission.objects.filter(
        assignment__course__in=courses, marks__isnull=True
    ).count()

    recent_quizzes = []
    try:
        from quiz.models import Quiz
        recent_quizzes = Quiz.objects.filter(course__in=courses).order_by('-created_at')[:5]
    except Exception:
        pass

    announcements = Announcement.objects.filter(created_by=request.user).order_by('-created_at')[:5]

    context = {
        'faculty': faculty, 'courses': courses, 'enrollment_count': enrollment_count,
        'pending_submissions': pending_submissions, 'recent_quizzes': recent_quizzes,
        'announcements': announcements,
    }
    return render(request, 'academics/faculty_dashboard.html', context)


def faculty_mark_attendance(request, course_id):
    faculty = _require_faculty(request)
    if not faculty:
        return redirect('dashboard')
    course = get_object_or_404(Course, id=course_id)
    enrollments = Enrollment.objects.filter(course=course).select_related('student__user')

    if request.method == 'POST':
        att_date = request.POST.get('date')
        for enrollment in enrollments:
            status = request.POST.get(f'status_{enrollment.id}', 'Absent')
            Attendance.objects.update_or_create(
                enrollment=enrollment, date=att_date, defaults={'status': status}
            )
        messages.success(request, f'Attendance saved for {att_date}.')
        return redirect('faculty_mark_attendance', course_id=course_id)

    selected_date = request.GET.get('date', str(date.today()))

    enrollment_data = []
    already_marked = False
    for enrollment in enrollments:
        existing_record = Attendance.objects.filter(
            enrollment=enrollment, date=selected_date
        ).first()
        existing_status = existing_record.status if existing_record else None
        if existing_record:
            already_marked = True
        enrollment_data.append({
            'enrollment': enrollment,
            'existing': existing_status,
        })

    from django.db.models import Count, Case, When, IntegerField as IntF
    history_dates = (
        Attendance.objects
        .filter(enrollment__course=course)
        .values('date')
        .annotate(
            total=Count('id'),
            present=Count(Case(When(status='Present', then=1), output_field=IntF())),
            absent=Count(Case(When(status='Absent', then=1), output_field=IntF())),
            late=Count(Case(When(status='Late', then=1), output_field=IntF())),
        )
        .order_by('-date')[:10]
    )

    context = {
        'course': course,
        'enrollment_data': enrollment_data,
        'selected_date': selected_date,
        'already_marked': already_marked,
        'attendance_history': history_dates,
    }
    return render(request, 'academics/faculty_mark_attendance.html', context)

@login_required
def faculty_upload_marks(request, course_id):
    faculty = _require_faculty(request)
    if not faculty:
        return redirect('dashboard')
    course = get_object_or_404(Course, id=course_id)
    exams = Exam.objects.filter(course=course)
    enrollments = Enrollment.objects.filter(course=course).select_related('student__user')

    if request.method == 'POST':
        exam_id = request.POST.get('exam_id')
        exam = get_object_or_404(Exam, id=exam_id, course=course)
        saved = 0
        for enrollment in enrollments:
            marks_str = request.POST.get(f'marks_{enrollment.student.id}', '').strip()
            if marks_str:
                try:
                    marks = float(marks_str)
                    Result.objects.update_or_create(
                        exam=exam, student=enrollment.student, defaults={'marks_obtained': marks}
                    )
                    saved += 1
                except ValueError:
                    pass
        messages.success(request, f'Marks saved for {saved} student(s).')
        return redirect('faculty_dashboard')

    context = {'course': course, 'exams': exams, 'enrollments': enrollments}
    return render(request, 'academics/faculty_upload_marks.html', context)


@login_required
def faculty_grade_submission(request, submission_id):
    faculty = _require_faculty(request)
    if not faculty:
        return redirect('dashboard')
    submission = get_object_or_404(Submission, id=submission_id)

    if request.method == 'POST':
        marks = request.POST.get('marks')
        feedback = request.POST.get('feedback', '')
        if marks:
            submission.marks = int(marks)
            submission.feedback = feedback
            submission.save()
            messages.success(request, 'Submission graded.')
        return redirect('faculty_dashboard')

    context = {'submission': submission}
    return render(request, 'academics/faculty_grade_submission.html', context)


@login_required
def faculty_create_announcement(request):
    faculty = _require_faculty(request)
    if not faculty:
        return redirect('dashboard')

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        content = request.POST.get('content', '').strip()
        course_id = request.POST.get('course_id') or None
        if title and content:
            course = Course.objects.filter(id=course_id).first() if course_id else None
            Announcement.objects.create(title=title, content=content,
                                        created_by=request.user, target_course=course)
            messages.success(request, 'Announcement published.')
            return redirect('faculty_dashboard')
        messages.error(request, 'Title and content are required.')

    courses = faculty.courses.all()
    if not courses:
        courses = Course.objects.all()
    return render(request, 'academics/faculty_create_announcement.html', {'courses': courses})


# ─── Student Feature Views ────────────────────────────────────────────────────

def _faculty_guard(request):
    """Returns True if user is faculty and already redirected."""
    try:
        request.user.faculty
        return True
    except Faculty.DoesNotExist:
        return False


@login_required
def courses(request):
    if _faculty_guard(request):
        return redirect('faculty_dashboard')
    student = get_object_or_404(Student, user=request.user)
    enrollments = Enrollment.objects.filter(student=student).select_related('course')
    return render(request, 'academics/courses.html', {'enrollments': enrollments})


@login_required
def course_detail(request, course_id):
    if _faculty_guard(request):
        return redirect('faculty_dashboard')
    course = get_object_or_404(Course, id=course_id)
    student = get_object_or_404(Student, user=request.user)
    enrollment = get_object_or_404(Enrollment, student=student, course=course)

    attendance_records = Attendance.objects.filter(enrollment=enrollment).order_by('-date')
    total_classes = attendance_records.count()
    present = attendance_records.filter(status='Present').count()
    attendance_percentage = round((present / total_classes * 100), 2) if total_classes > 0 else 0

    assignments = Assignment.objects.filter(course=course).order_by('-due_date')
    timetable = Timetable.objects.filter(course=course).order_by('day', 'start_time')

    context = {
        'course': course, 'attendance_records': attendance_records,
        'attendance_percentage': attendance_percentage, 'present': present,
        'total_classes': total_classes, 'assignments': assignments, 'timetable': timetable,
    }
    return render(request, 'academics/course_detail.html', context)


@login_required
def attendance(request):
    if _faculty_guard(request):
        return redirect('faculty_dashboard')
    student = get_object_or_404(Student, user=request.user)
    enrollments = Enrollment.objects.filter(student=student).select_related('course')
    attendance_data = []
    for enrollment in enrollments:
        records = Attendance.objects.filter(enrollment=enrollment).order_by('-date')
        total = records.count()
        present = records.filter(status='Present').count()
        percentage = round((present / total * 100), 2) if total > 0 else 0
        attendance_data.append({
            'course': enrollment.course, 'records': records[:10],
            'total': total, 'present': present, 'percentage': percentage,
            'shortage': percentage < ATTENDANCE_THRESHOLD and total > 0,
            'threshold': ATTENDANCE_THRESHOLD,
        })
    return render(request, 'academics/attendance.html', {'attendance_data': attendance_data})


@login_required
def assignments(request):
    if _faculty_guard(request):
        return redirect('faculty_dashboard')
    student = get_object_or_404(Student, user=request.user)
    enrollments = Enrollment.objects.filter(student=student)
    courses_list = [e.course for e in enrollments]
    all_assignments = Assignment.objects.filter(course__in=courses_list).order_by('-due_date')
    assignment_list = []
    for assignment in all_assignments:
        try:
            submission = Submission.objects.get(assignment=assignment, student=student)
        except Submission.DoesNotExist:
            submission = None
        assignment_list.append({
            'assignment': assignment, 'submission': submission,
            'is_overdue': assignment.due_date < timezone.now(),
        })
    return render(request, 'academics/assignments.html', {'assignment_list': assignment_list})


@login_required
def submit_assignment(request, assignment_id):
    if _faculty_guard(request):
        return redirect('faculty_dashboard')
    assignment = get_object_or_404(Assignment, id=assignment_id)
    student = get_object_or_404(Student, user=request.user)
    if request.method == 'POST' and request.FILES.get('file'):
        submission, _ = Submission.objects.get_or_create(assignment=assignment, student=student)
        submission.file = request.FILES['file']
        submission.save()
        messages.success(request, 'Assignment submitted successfully!')
        return redirect('assignments')
    return render(request, 'academics/submit_assignment.html', {'assignment': assignment})


@login_required
def results(request):
    if _faculty_guard(request):
        return redirect('faculty_dashboard')
    student = get_object_or_404(Student, user=request.user)
    all_results = Result.objects.filter(student=student).select_related(
        'exam', 'exam__course'
    ).order_by('exam__course__semester', '-exam__date')

    if all_results:
        avg_percentage = sum(
            float(r.marks_obtained) / r.exam.max_marks * 100 for r in all_results
        ) / len(all_results)
    else:
        avg_percentage = 0

    semester_data = {}
    for r in all_results:
        sem = r.exam.course.semester
        semester_data.setdefault(sem, []).append(r)

    semester_gpas = {sem: student.calculate_gpa(sem) for sem in semester_data}
    cgpa = student.calculate_cgpa()

    context = {
        'results': all_results, 'avg_percentage': round(avg_percentage, 2),
        'semester_data': sorted(semester_data.items()),
        'semester_gpas': semester_gpas, 'cgpa': cgpa,
    }
    return render(request, 'academics/results.html', context)


@login_required
def download_academic_report(request):
    if _faculty_guard(request):
        return redirect('faculty_dashboard')
    student = get_object_or_404(Student, user=request.user)
    all_results = Result.objects.filter(student=student).select_related(
        'exam', 'exam__course'
    ).order_by('exam__course__semester', '-exam__date')

    from reportlab.lib.pagesizes import A4  # type: ignore
    from reportlab.lib import colors  # type: ignore
    from reportlab.lib.styles import getSampleStyleSheet  # type: ignore
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer  # type: ignore
    from reportlab.lib.units import cm  # type: ignore

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm
    )
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("Academic Report", styles['Title']))
    elements.append(Paragraph(
        f"Student: {student.user.get_full_name() or student.user.username}  |  "
        f"Reg No: {student.registration_number}  |  "
        f"Branch: {student.branch}  |  Semester: {student.semester}",
        styles['Normal']
    ))
    elements.append(Spacer(1, 0.4*cm))
    cgpa = student.calculate_cgpa()
    elements.append(Paragraph(f"CGPA: {cgpa if cgpa else 'N/A'}", styles['Heading3']))
    elements.append(Spacer(1, 0.4*cm))

    elements.append(Paragraph("Attendance Summary", styles['Heading2']))
    att_data = [['Course', 'Present', 'Total', 'Percentage', 'Status']]
    enrollments = Enrollment.objects.filter(student=student).select_related('course')
    for enrollment in enrollments:
        total = Attendance.objects.filter(enrollment=enrollment).count()
        present = Attendance.objects.filter(enrollment=enrollment, status='Present').count()
        pct = round((present / total * 100), 2) if total > 0 else 0
        status = 'OK' if pct >= ATTENDANCE_THRESHOLD else 'SHORTAGE'
        att_data.append([enrollment.course.code, str(present), str(total), f'{pct}%', status])

    att_table = Table(att_data, colWidths=[4*cm, 2.5*cm, 2.5*cm, 3*cm, 3*cm])
    att_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0d6efd')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
    ]))
    elements.append(att_table)
    elements.append(Spacer(1, 0.5*cm))

    elements.append(Paragraph("Exam Results", styles['Heading2']))
    res_data = [['Course', 'Exam', 'Type', 'Marks', 'Max', 'Grade']]
    for r in all_results:
        res_data.append([
            r.exam.course.code, r.exam.name, r.exam.exam_type,
            str(r.marks_obtained), str(r.exam.max_marks), r.grade
        ])

    if len(res_data) > 1:
        res_table = Table(res_data, colWidths=[2.5*cm, 4.5*cm, 3*cm, 2*cm, 2*cm, 1.5*cm])
        res_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#198754')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
        ]))
        elements.append(res_table)
    else:
        elements.append(Paragraph("No results recorded.", styles['Normal']))

    doc.build(elements)
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = (
        f'attachment; filename="academic_report_{student.registration_number}.pdf"'
    )
    return response


@login_required
def timetable(request):
    if _faculty_guard(request):
        return redirect('faculty_dashboard')
    student = get_object_or_404(Student, user=request.user)
    enrollments = Enrollment.objects.filter(student=student)
    courses_list = [e.course for e in enrollments]
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    timetable_data = []
    for day in days:
        slots = Timetable.objects.filter(
            course__in=courses_list, day=day
        ).select_related('course').order_by('start_time')
        timetable_data.append((day, slots))
    return render(request, 'academics/timetable.html', {'timetable_data': timetable_data})


@login_required
def profile(request):
    try:
        request.user.faculty
        return redirect('faculty_dashboard')
    except Faculty.DoesNotExist:
        pass
    student = get_object_or_404(Student, user=request.user)
    if request.method == 'POST':
        student.branch = request.POST.get('branch', student.branch)
        semester = request.POST.get('semester')
        if semester and semester.isdigit():
            student.semester = int(semester)
        student.phone = request.POST.get('phone', student.phone)
        if request.FILES.get('profile_picture'):
            student.profile_picture = request.FILES['profile_picture']
        student.user.first_name = request.POST.get('first_name', student.user.first_name)
        student.user.last_name = request.POST.get('last_name', student.user.last_name)
        student.user.email = request.POST.get('email', student.user.email)
        student.user.save()
        student.save()
        messages.success(request, 'Profile updated successfully.')
        return redirect('profile')
    return render(request, 'academics/profile.html', {'student': student})


@login_required
def leaderboard(request):
    from quiz.models import QuizAttempt
    from django.db.models import Sum, Count
    from django.db.models import Avg as DjAvg

    leaderboard_data = (
        QuizAttempt.objects.filter(is_completed=True)
        .values('student__user__first_name', 'student__user__last_name',
                'student__user__username', 'student__registration_number', 'student__branch')
        .annotate(total_score=Sum('score'), quizzes_taken=Count('id'), avg_score=DjAvg('score'))
        .order_by('-total_score')[:50]
    )

    ranked = []
    for rank, entry in enumerate(leaderboard_data, start=1):
        name = (f"{entry['student__user__first_name']} {entry['student__user__last_name']}".strip()
                or entry['student__user__username'])
        ranked.append({
            'rank': rank, 'name': name, 'username': entry['student__user__username'],
            'reg_no': entry['student__registration_number'], 'branch': entry['student__branch'],
            'total_score': entry['total_score'], 'quizzes_taken': entry['quizzes_taken'],
            'avg_score': round(float(entry['avg_score'] or 0), 2),
        })

    return render(request, 'academics/leaderboard.html', {'leaderboard': ranked})
