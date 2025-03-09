
from django.urls import path
from . import views

urlpatterns = [
    path("", views.home_view, name="home"),
    path("register", views.register_view, name="register"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),

    path("courses", views.courses_list_view, name="courses_list"),
    path("weekly-schedule", views.weekly_schedule_view, name="weekly_schedule"),

    path("admin-courses", views.admin_courses_view, name="admin_courses"),
    path('admin-users', views.admin_users_view, name='admin_users'),
]
