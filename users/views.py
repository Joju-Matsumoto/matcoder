from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView

from . import models, forms

# Create your views here.
def index_view(request):
    context = {
        "users": models.User.objects.all()
    }
    return render(request, "users/index.html", context)

def signup_view(request):
    if request.method == "POST":
        form = forms.SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password1")
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect("users:index")
    else:
        form = forms.SignUpForm()
    return render(request, "users/signup.html", {"form": form,})

class Login(LoginView):
    form_class = forms.LoginForm
    template_name = "users/login.html"

login_view = Login.as_view()

class Logout(LoginRequiredMixin, LogoutView):
    template_name = "users/logout.html"

logout_view = Logout.as_view()