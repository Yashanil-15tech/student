from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from academics.models import Course, Student

class Quiz(models.Model):
    title = models.CharField(max_length=200)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    description = models.TextField()
    duration_minutes = models.IntegerField(validators=[MinValueValidator(1)])
    total_marks = models.IntegerField(validators=[MinValueValidator(1)])
    passing_marks = models.IntegerField(validators=[MinValueValidator(0)])
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    shuffle_questions = models.BooleanField(default=True)
    show_results = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} - {self.course.code}"
    
    class Meta:
        verbose_name_plural = "Quizzes"

class Question(models.Model):
    QUESTION_TYPES = [
        ('MCQ', 'Multiple Choice'),
        ('TF', 'True/False'),
        ('SA', 'Short Answer'),
    ]
    
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    question_type = models.CharField(max_length=3, choices=QUESTION_TYPES, default='MCQ')
    marks = models.IntegerField(validators=[MinValueValidator(1)])
    order = models.IntegerField(default=0)
    
    def __str__(self):
        return f"Q{self.order}: {self.question_text[:50]}"
    
    class Meta:
        ordering = ['order']

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    choice_text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)
    
    def __str__(self):
        return self.choice_text

class QuizAttempt(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['quiz', 'student']
    
    def __str__(self):
        return f"{self.student.user.username} - {self.quiz.title} - {self.score}"

class Answer(models.Model):
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_choice = models.ForeignKey(Choice, on_delete=models.CASCADE, null=True, blank=True)
    text_answer = models.TextField(blank=True)
    is_correct = models.BooleanField(default=False)
    marks_obtained = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    def __str__(self):
        return f"{self.attempt.student.user.username} - Q{self.question.order}"
