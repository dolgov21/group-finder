from django.shortcuts import render, HttpResponse

from .vendor import control

def run_scraper(request):
    control.run()
    return HttpResponse("hi")