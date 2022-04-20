from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponse
# Create your views here.


def index(request):
    if 'email' not in request.session:
        return redirect('/login')
    return HttpResponse("请求路径:{}" .format(request.path))


def track(request):
    return HttpResponse("请求路径:{}" .format(request.path))


def register(request):
    return


def login(request):
    return


def account(request):
    return


def package_detail(request):
    return
