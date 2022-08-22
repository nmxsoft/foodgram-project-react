from django.shortcuts import render

from .models import User


def view_users(request):
    return render(request, 'user.html', {'users': User.objects.all()})
