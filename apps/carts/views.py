from django.shortcuts import render
from django.http import HttpResponse


def createsession(request):
    request.session['name'] = 'xiaowang'
    return HttpResponse("session设置")