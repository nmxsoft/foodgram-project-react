from django.urls import path

from . import views

app_name = 'users'

urlpatterns = [
    path('users/', views.view_users, name='view_user')
]
