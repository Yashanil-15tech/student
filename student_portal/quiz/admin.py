from django.contrib import admin
from .models import Quiz, Question, Choice, QuizAttempt, Answer

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 4

class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    show_change_link = True

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'start_time', 'end_time', 'total_marks', 'is_active']
    list_filter = ['is_active', 'course', 'start_time']
    search_fields = ['title', 'course__code']
    inlines = [QuestionInline]

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['quiz', 'question_text', 'question_type', 'marks', 'order']
    list_filter = ['question_type', 'quiz']
    search_fields = ['question_text', 'quiz__title']
    inlines = [ChoiceInline]

@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ['question', 'choice_text', 'is_correct']
    list_filter = ['is_correct', 'question__quiz']
    search_fields = ['choice_text', 'question__question_text']

@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ['student', 'quiz', 'start_time', 'end_time', 'score', 'is_completed']
    list_filter = ['is_completed', 'quiz', 'start_time']
    search_fields = ['student__user__username', 'quiz__title']

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ['attempt', 'question', 'selected_choice', 'is_correct', 'marks_obtained']
    list_filter = ['is_correct', 'attempt__quiz']
    search_fields = ['attempt__student__user__username', 'question__question_text']
