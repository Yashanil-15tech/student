from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Quiz, Question, Choice, QuizAttempt, Answer
from academics.models import Student, Enrollment, Faculty, UserProfile, Course


def _is_faculty(user):
    try:
        role = user.profile.role
        return role in ('faculty', 'admin')
    except UserProfile.DoesNotExist:
        try:
            user.faculty
            return True
        except Faculty.DoesNotExist:
            return False


# ─── Student Views ────────────────────────────────────────────────────────────

@login_required
def quiz_list(request):
    if _is_faculty(request.user):
        return redirect('faculty_manage_quizzes')

    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        messages.error(request, 'Student profile not found.')
        return redirect('dashboard')

    enrollments = Enrollment.objects.filter(student=student)
    courses = [e.course for e in enrollments]

    now = timezone.now()
    available_quizzes = Quiz.objects.filter(
        course__in=courses, is_active=True,
        start_time__lte=now, end_time__gte=now
    ).order_by('-start_time')

    upcoming_quizzes = Quiz.objects.filter(
        course__in=courses, is_active=True, start_time__gt=now
    ).order_by('start_time')

    completed_quizzes = Quiz.objects.filter(
        course__in=courses, is_active=True, end_time__lt=now
    ).order_by('-end_time')

    attempts = QuizAttempt.objects.filter(student=student)
    attempted_quiz_ids = attempts.values_list('quiz_id', flat=True)

    context = {
        'available_quizzes': available_quizzes,
        'upcoming_quizzes': upcoming_quizzes,
        'completed_quizzes': completed_quizzes,
        'attempted_quiz_ids': list(attempted_quiz_ids),
        'attempts': attempts,
    }
    return render(request, 'quiz/quiz_list.html', context)


@login_required
def quiz_detail(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    student = get_object_or_404(Student, user=request.user)

    enrollment = Enrollment.objects.filter(student=student, course=quiz.course).first()
    if not enrollment:
        messages.error(request, 'You are not enrolled in this course.')
        return redirect('quiz_list')

    now = timezone.now()
    if now < quiz.start_time:
        messages.warning(request, 'This quiz has not started yet.')
        return redirect('quiz_list')
    if now > quiz.end_time:
        messages.warning(request, 'This quiz has ended.')
        return redirect('quiz_list')

    attempt = QuizAttempt.objects.filter(quiz=quiz, student=student).first()
    context = {
        'quiz': quiz,
        'attempt': attempt,
        'question_count': quiz.questions.count(),
    }
    return render(request, 'quiz/quiz_detail.html', context)


@login_required
def start_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    student = get_object_or_404(Student, user=request.user)

    if QuizAttempt.objects.filter(quiz=quiz, student=student).exists():
        messages.warning(request, 'You have already attempted this quiz.')
        return redirect('quiz_list')

    attempt = QuizAttempt.objects.create(quiz=quiz, student=student)
    return redirect('take_quiz', attempt_id=attempt.id)


@login_required
def take_quiz(request, attempt_id):
    attempt = get_object_or_404(QuizAttempt, id=attempt_id)
    student = get_object_or_404(Student, user=request.user)

    if attempt.student != student:
        messages.error(request, 'Invalid quiz attempt.')
        return redirect('quiz_list')

    if attempt.is_completed:
        messages.info(request, 'You have already completed this quiz.')
        return redirect('quiz_result', attempt_id=attempt.id)

    questions = list(attempt.quiz.questions.all().prefetch_related('choices'))

    if attempt.quiz.shuffle_questions:
        session_key = f'quiz_order_{attempt.id}'
        if session_key not in request.session:
            import random
            order = [q.id for q in questions]
            random.shuffle(order)
            request.session[session_key] = order
        order = request.session[session_key]
        questions_dict = {q.id: q for q in questions}
        questions = [questions_dict[qid] for qid in order if qid in questions_dict]

    time_elapsed = (timezone.now() - attempt.start_time).total_seconds()
    time_limit = attempt.quiz.duration_minutes * 60
    time_remaining = max(0, time_limit - time_elapsed)

    if time_remaining <= 0:
        return submit_quiz(request, attempt_id)

    context = {
        'attempt': attempt,
        'quiz': attempt.quiz,
        'questions': questions,
        'time_remaining': int(time_remaining),
    }
    return render(request, 'quiz/take_quiz.html', context)


@login_required
def submit_quiz(request, attempt_id):
    attempt = get_object_or_404(QuizAttempt, id=attempt_id)
    student = get_object_or_404(Student, user=request.user)

    if attempt.student != student:
        messages.error(request, 'Invalid quiz attempt.')
        return redirect('quiz_list')

    if attempt.is_completed:
        messages.info(request, 'This quiz has already been submitted.')
        return redirect('quiz_result', attempt_id=attempt.id)

    if request.method == 'POST':
        total_score = 0
        for question in attempt.quiz.questions.all():
            answer_key = f'question_{question.id}'
            if question.question_type in ('MCQ', 'TF'):
                choice_id = request.POST.get(answer_key)
                if choice_id:
                    choice = Choice.objects.get(id=choice_id)
                    is_correct = choice.is_correct
                    marks = question.marks if is_correct else 0
                    Answer.objects.create(
                        attempt=attempt, question=question,
                        selected_choice=choice, is_correct=is_correct, marks_obtained=marks
                    )
                    if is_correct:
                        total_score += marks
            elif question.question_type == 'SA':
                text_answer = request.POST.get(answer_key, '')
                Answer.objects.create(
                    attempt=attempt, question=question,
                    text_answer=text_answer, marks_obtained=0
                )

        attempt.score = total_score
        attempt.end_time = timezone.now()
        attempt.is_completed = True
        attempt.save()

        messages.success(request, 'Quiz submitted successfully!')
        return redirect('quiz_result', attempt_id=attempt.id)

    return redirect('take_quiz', attempt_id=attempt_id)


@login_required
def quiz_result(request, attempt_id):
    attempt = get_object_or_404(QuizAttempt, id=attempt_id)
    student = get_object_or_404(Student, user=request.user)

    if attempt.student != student:
        messages.error(request, 'Invalid quiz attempt.')
        return redirect('quiz_list')

    if not attempt.is_completed:
        messages.warning(request, 'This quiz is not yet completed.')
        return redirect('take_quiz', attempt_id=attempt.id)

    answers = Answer.objects.filter(attempt=attempt).select_related('question', 'selected_choice')
    total_questions = attempt.quiz.questions.count()
    correct_answers = answers.filter(is_correct=True).count()
    percentage = (attempt.score / attempt.quiz.total_marks * 100) if attempt.quiz.total_marks > 0 else 0
    passed = attempt.score >= attempt.quiz.passing_marks
    time_taken = (attempt.end_time - attempt.start_time).total_seconds() / 60

    context = {
        'attempt': attempt, 'quiz': attempt.quiz, 'answers': answers,
        'total_questions': total_questions, 'correct_answers': correct_answers,
        'percentage': round(percentage, 2), 'passed': passed,
        'time_taken': round(time_taken, 2),
    }
    return render(request, 'quiz/quiz_result.html', context)


@login_required
def my_attempts(request):
    student = get_object_or_404(Student, user=request.user)
    attempts = QuizAttempt.objects.filter(student=student).select_related(
        'quiz', 'quiz__course'
    ).order_by('-start_time')
    return render(request, 'quiz/my_attempts.html', {'attempts': attempts})


# ─── Faculty Quiz Management ──────────────────────────────────────────────────

@login_required
def faculty_manage_quizzes(request):
    if not _is_faculty(request.user):
        return redirect('quiz_list')
    try:
        faculty = request.user.faculty
    except Faculty.DoesNotExist:
        return redirect('faculty_profile_setup')

    courses = faculty.courses.all() or Course.objects.all()
    quizzes = Quiz.objects.filter(course__in=courses).order_by('-created_at')
    return render(request, 'quiz/faculty_manage_quizzes.html', {
        'quizzes': quizzes, 'courses': courses
    })


@login_required
def faculty_create_quiz(request):
    if not _is_faculty(request.user):
        return redirect('quiz_list')
    try:
        faculty = request.user.faculty
    except Faculty.DoesNotExist:
        return redirect('faculty_profile_setup')

    courses = faculty.courses.all() or Course.objects.all()

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        course_id = request.POST.get('course_id')
        description = request.POST.get('description', '').strip()
        duration = request.POST.get('duration_minutes')
        total_marks = request.POST.get('total_marks')
        passing_marks = request.POST.get('passing_marks')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        shuffle = request.POST.get('shuffle_questions') == 'on'
        show_results = request.POST.get('show_results') == 'on'

        errors = []
        if not title:
            errors.append('Title is required.')
        if not course_id:
            errors.append('Course is required.')
        if not duration or not duration.isdigit():
            errors.append('Duration must be a number.')
        if not total_marks or not total_marks.isdigit():
            errors.append('Total marks must be a number.')
        if not passing_marks or not passing_marks.isdigit():
            errors.append('Passing marks must be a number.')
        if not start_time or not end_time:
            errors.append('Start and end time are required.')

        if errors:
            for e in errors:
                messages.error(request, e)
        else:
            course = get_object_or_404(Course, id=course_id)
            quiz = Quiz.objects.create(
                title=title, course=course, description=description,
                duration_minutes=int(duration), total_marks=int(total_marks),
                passing_marks=int(passing_marks), start_time=start_time,
                end_time=end_time, shuffle_questions=shuffle,
                show_results=show_results, is_active=True,
            )
            messages.success(request, f'Quiz "{title}" created! Now add questions.')
            return redirect('faculty_add_question', quiz_id=quiz.id)

    return render(request, 'quiz/faculty_create_quiz.html', {'courses': courses})


@login_required
def faculty_edit_quiz(request, quiz_id):
    if not _is_faculty(request.user):
        return redirect('quiz_list')
    quiz = get_object_or_404(Quiz, id=quiz_id)

    if request.method == 'POST':
        quiz.title = request.POST.get('title', quiz.title)
        quiz.description = request.POST.get('description', quiz.description)
        duration = request.POST.get('duration_minutes')
        if duration and duration.isdigit():
            quiz.duration_minutes = int(duration)
        total = request.POST.get('total_marks')
        if total and total.isdigit():
            quiz.total_marks = int(total)
        passing = request.POST.get('passing_marks')
        if passing and passing.isdigit():
            quiz.passing_marks = int(passing)
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        if start_time:
            quiz.start_time = start_time
        if end_time:
            quiz.end_time = end_time
        quiz.shuffle_questions = request.POST.get('shuffle_questions') == 'on'
        quiz.show_results = request.POST.get('show_results') == 'on'
        quiz.is_active = request.POST.get('is_active') == 'on'
        quiz.save()
        messages.success(request, 'Quiz updated successfully.')
        return redirect('faculty_manage_quizzes')

    return render(request, 'quiz/faculty_edit_quiz.html', {'quiz': quiz})


@login_required
def faculty_delete_quiz(request, quiz_id):
    if not _is_faculty(request.user):
        return redirect('quiz_list')
    quiz = get_object_or_404(Quiz, id=quiz_id)
    quiz.delete()
    messages.success(request, 'Quiz deleted.')
    return redirect('faculty_manage_quizzes')


@login_required
def faculty_add_question(request, quiz_id):
    if not _is_faculty(request.user):
        return redirect('quiz_list')
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = quiz.questions.all().prefetch_related('choices')

    if request.method == 'POST':
        question_text = request.POST.get('question_text', '').strip()
        question_type = request.POST.get('question_type', 'MCQ')
        marks = request.POST.get('marks', '1')

        if not question_text:
            messages.error(request, 'Question text is required.')
        else:
            order = quiz.questions.count() + 1
            question = Question.objects.create(
                quiz=quiz, question_text=question_text,
                question_type=question_type,
                marks=int(marks) if marks.isdigit() else 1,
                order=order,
            )

            if question_type == 'MCQ':
                for i in range(1, 5):
                    choice_text = request.POST.get(f'choice_{i}', '').strip()
                    is_correct = request.POST.get('correct_choice') == str(i)
                    if choice_text:
                        Choice.objects.create(
                            question=question, choice_text=choice_text, is_correct=is_correct
                        )
            elif question_type == 'TF':
                correct = request.POST.get('tf_correct', 'True')
                Choice.objects.create(question=question, choice_text='True', is_correct=(correct == 'True'))
                Choice.objects.create(question=question, choice_text='False', is_correct=(correct == 'False'))

            messages.success(request, f'Question {order} added.')
            if request.POST.get('add_another'):
                return redirect('faculty_add_question', quiz_id=quiz.id)
            return redirect('faculty_manage_quizzes')

    return render(request, 'quiz/faculty_add_question.html', {
        'quiz': quiz, 'questions': questions
    })


@login_required
def faculty_delete_question(request, question_id):
    if not _is_faculty(request.user):
        return redirect('quiz_list')
    question = get_object_or_404(Question, id=question_id)
    quiz_id = question.quiz.id
    question.delete()
    messages.success(request, 'Question deleted.')
    return redirect('faculty_add_question', quiz_id=quiz_id)
