from django.urls import path
from . import views

urlpatterns = [
    path('', views.quiz_list, name='quiz_list'),
    path('<int:quiz_id>/', views.quiz_detail, name='quiz_detail'),
    path('<int:quiz_id>/start/', views.start_quiz, name='start_quiz'),
    path('attempt/<int:attempt_id>/', views.take_quiz, name='take_quiz'),
    path('attempt/<int:attempt_id>/submit/', views.submit_quiz, name='submit_quiz'),
    path('attempt/<int:attempt_id>/result/', views.quiz_result, name='quiz_result'),
    path('my-attempts/', views.my_attempts, name='my_attempts'),
    path('faculty/create/', views.faculty_create_quiz, name='faculty_create_quiz'),
    path('faculty/<int:quiz_id>/edit/', views.faculty_edit_quiz, name='faculty_edit_quiz'),
    path('faculty/<int:quiz_id>/delete/', views.faculty_delete_quiz, name='faculty_delete_quiz'),
    path('faculty/<int:quiz_id>/add-question/', views.faculty_add_question, name='faculty_add_question'),
    path('faculty/question/<int:question_id>/delete/', views.faculty_delete_question, name='faculty_delete_question'),
    path('faculty/manage/', views.faculty_manage_quizzes, name='faculty_manage_quizzes'),
]
