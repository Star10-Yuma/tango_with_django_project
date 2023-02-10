from django.shortcuts import render

from django.http import HttpResponse

def index(request):
    link = "<a href='/rango/about/'>About</a>"
    return HttpResponse("Rango says hey there partner!" + link)

def about(request):
    link = "<a href='/rango/'>Index</a>"
    return HttpResponse("Rango says here is the about page." + link)