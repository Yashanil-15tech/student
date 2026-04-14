from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from academics import views as academic_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', academic_views.home, name='home'),
    path('dashboard/', academic_views.dashboard, name='dashboard'),

    # Authentication
    path('login/', auth_views.LoginView.as_view(template_name='auth/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', academic_views.register, name='register'),
    path('profile-setup/', academic_views.profile_setup, name='profile_setup'),
    path('faculty-profile-setup/', academic_views.faculty_profile_setup, name='faculty_profile_setup'),

    # Password reset
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='auth/password_reset.html'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='auth/password_reset_done.html'), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='auth/password_reset_confirm.html'), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='auth/password_reset_complete.html'), name='password_reset_complete'),

    path('academics/', include('academics.urls')),
    path('quiz/', include('quiz.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
