from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.views import View

from . import models, forms

# contests側にmy_pageをおいたので必要なくなった．
# # 邪道...
# from contests.models import ContestScore, UserProfile


class IndexView(View):
    def get(self, request):
        # リダイレクト，ずるい...?
        return redirect("contests:my_page")
        # context = {}
        # if request.user.is_authenticated:
        #     context["contest_scores"] = ContestScore.objects.filter(user=request.user).order_by("-contest__start_date")
        #     # contests用のユーザープロフィールの 取得 or 新規作成
        #     try:
        #         user_profile = UserProfile.objects.get(user=request.user)
        #     except:
        #         user_profile = UserProfile.objects.create(user=request.user)
        #     context["user_profile"] = user_profile
        # return render(request, "users/index.html", context)

index_view = IndexView.as_view()

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