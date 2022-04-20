from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponse
from . import forms
import website.models as md
from django.conf import settings  # 将settings的内容引进


def index(request):
    if 'username' not in request.session:
        return redirect('/login')
    if (request.method == 'POST'):
        track_form = forms.TrackForm(request.Post)
        if track_form.is_valid():
            package = md.Package.objects.filter(
                tracking_id=track_form.cleaned_data['trackingid'])
            # return render(request, 'track.html', locals())
            return redirect('track', id=package.tracking_id)
    else:
        track_form = forms.TrackForm()
    return render(request, 'index.html', locals())


def track(request, id):
    if 'username' not in request.session:
        return redirect('/login')
    package = get_object_or_404(md.Package, tracking_id=id)
    return render(request, 'track.html', locals())


def register(request):
    if request.method == 'POST':
        register_form = forms.RegisterForm(request.POST)
        if register_form.is_valid():
            user_name = register_form.cleaned_data['username']
            password = register_form.cleaned_data['password']
            password2 = register_form.cleaned_data['password2']
            email = register_form.cleaned_data['email']

            try:
                existed = md.User.objects.get(username=user_name)
            except:
                existed = None
            if existed is not None:
                error_message = 'email existed!'
                return render(request, 'register.html', locals())
            if password != password2:
                error_message = 'passwords are not same!'
                return render(request, 'register.html', locals())
            current_user = md.User()
            current_user.username = user_name
            current_user.email = email
            current_user.password = password
            current_user.save()
            return redirect('/login')
    else:
        register_form = forms.RegisterForm()
    return render(request, 'register.html', locals())


def login(request):
    if request.method == 'POST':
        login_form = forms.LoginForm(request.POST)
        if login_form.is_valid():
            user_name = login_form.cleaned_data['username']
            password = login_form.cleaned_data['password']
            user = md.User.objects.filter(username=user_name).first()
            if not user:
                error_message = 'user does not exist'
                return render(request, 'login.html', locals())
            else:
                if user.password == password:
                    request.session['username'] = user.username
                    request.session.set_expiry(99999999999)
                    return redirect('/index')
                else:
                    error_message = 'wrong email or password'
                    return render(request, 'login.html', locals())
    else:
        login_form = forms.LoginForm()
    return render(request, 'login.html', locals())


def logout(request):
    try:
        del request.session['username']
    except KeyError:
        pass
    return redirect('/login')


def account(request):
    if 'username' not in request.session:
        return redirect('/login')
    user = md.User.objects.get(username=request.session['username'])
    user_packages = md.Package.objects.filter(
        user=request.session['username']).count()
    tracking_list = []
    for package in user_packages:
        tracking_list.append(package.tracking_id)
    pac_items = md.Item.objects.filter(tracking_id__in=tracking_list)
    return render(request, 'account.html', {'user': user, 'user_packages': user_packages, 'pac_items': pac_items})


# def package_detail(request):
#     return
