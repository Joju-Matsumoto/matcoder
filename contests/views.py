from django.shortcuts import render, redirect
# from django.views.generic import TemplateView
# Create your views here.
from django.utils import timezone
from django.views import View

from . import models
from . import forms
from . import utils

def index_view(request):
    template_name = "contests/index.html"
    now = timezone.now()
    context = {
        "past_contests": models.Contest.objects.filter(end_date__lt=now),
        "future_contests": models.Contest.objects.filter(start_date__gt=now),
        "live_contests": models.Contest.objects.filter(start_date__lte=now).filter(end_date__gt=now),
    }
    return render(request, template_name, context)

class ContestDetailView(View):
    def get(self, request, short_name, *args, **kwargs):
        contest = models.Contest.objects.get(short_name=short_name)
        context = {
            "is_live": contest.is_live(),
            "contest": contest,
        }
        return render(request, "contests/contest_detail.html", context)
    
    def post(self, request, short_name, *args, **kwargs):
        contest = models.Contest.objects.get(short_name=short_name)
        if request.user.is_authenticated:
            contest.users.add(request.user)
            contest.save()
        return redirect("contests:contest_detail", short_name)

contest_detail_view = ContestDetailView.as_view()

class ProblemsView(View):
    def get(self, request, short_name, *args, **kwargs):
        contest = models.Contest.objects.get(short_name=short_name)
        context = {
            "contest": contest,
            "problems": contest.problem_set.all(),
        }
        return render(request, "contests/problems.html", context)

problems_view = ProblemsView.as_view()

class ProblemDetailView(View):
    def get(self, request, short_name, problem_id, *args, **kwargs):
        contest = models.Contest.objects.get(short_name=short_name)
        problem = models.Problem.objects.get(pk=problem_id)
        context = {
            "contest": contest,
            "problem": problem,
            "form": forms.SubmissionForm(),
        }
        return render(request, "contests/problem_detail.html", context)
    
    def post(self, request, short_name, problem_id, *args, **kwargs):
        problem = models.Problem.objects.get(pk=problem_id)
        form = forms.SubmissionForm(request.POST)
        if form.is_valid(): # 検証ずみ
            # フォームからモデルのインスタンスを取得し，正誤判定し，情報を加えてからDBに保存
            submission = form.save(commit=False)    # DBに保存せずにインスタンス化
            if utils.check_answer(submission.answer, problem.answer):   # 正答
                submission.accepted = True
                # contest_score を更新
            else:   # 誤答
                submission.accepted = False

            submission.user = request.user
            submission.problem = problem
            submission.save()   # 保存
            return redirect("contests:submissions", short_name)
        else:   # 検証エラー
            contest = models.Contest.objects.get(short_name=short_name)
            context = {
                "contest": contest,
                "problem": problem,
                "form": form,
            }
            return render(request, "contests/problem_detail.html", context)

problem_detail_view = ProblemDetailView.as_view()

class SubmissionsView(View):
    def get(self, request, short_name, *args, **kwargs):
        contest = models.Contest.objects.get(short_name=short_name)
        submissions = models.Submission.objects.filter(problem__contest=contest).order_by("-submission_date")
        if contest.is_live():
            submissions = submissions.filter(user=request.user)
        context = {
            "contest": contest,
            "submissions": submissions,
        }
        return render(request, "contests/submissions.html", context)

submissions_view = SubmissionsView.as_view()

class SubmissionsMeView(View):
    def get(self, request, short_name, *args, **kwargs):
        contest = models.Contest.objects.get(short_name=short_name)
        submissions = models.Submission.objects.filter(problem__contest=contest).filter(user=request.user).order_by("-submission_date")
        context = {
            "contest": contest,
            "submissions": submissions,
        }
        return render(request, "contests/submissions.html", context)

submissions_me_view = SubmissionsMeView.as_view()

class SubmissionDetailView(View):
    def get(self, request, short_name, submission_id, *args, **kwargs):
        contest = models.Contest.objects.get(short_name=short_name)
        submission = models.Submission.objects.get(pk=submission_id)
        problem = submission.problem
        context = {
            "problem": problem,
            "contest": contest,
            "submission": submission,
        }
        return render(request, "contests/submission_detail.html", context)

submission_detail_view = SubmissionDetailView.as_view()

class StandingsView(View):
    def get(self, request, short_name, *args, **kwargs):
        context = {
            "contest": models.Contest.objects.get(short_name=short_name),
        }
        return render(request, "contests/standings.html", context)

standings_view = StandingsView.as_view()