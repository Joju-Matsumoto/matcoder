import datetime

from django.shortcuts import render, redirect
# from django.views.generic import TemplateView
# Create your views here.
from django.utils import timezone
from django.views import View

from . import models
from . import forms
from . import utils

class IndexView(View):
    def get(self, request, *args, **kwargs):
        now = timezone.now()
        all_contests = models.Contest.objects.all()
        past_contests = all_contests.filter(end_date__lt=now)
        future_contests = all_contests.filter(start_date__gt=now)
        live_contests = all_contests.filter(start_date__lte=now).filter(end_date__gt=now)
        context = {
            "contests_list": [
                ("開催中のコンテスト", live_contests),
                ("開催予定のコンテスト", future_contests),
                ("過去のコンテスト", past_contests),
            ],
        }
        return render(request, "contests/index.html", context)

index_view = IndexView.as_view()

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
            contest_score = models.ContestScore.objects.create(
                contest=contest,
                user=request.user,
            )
            contest_score.save()
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
        contest = models.Contest.objects.get(short_name=short_name)
        problem = models.Problem.objects.get(pk=problem_id)
        form = forms.SubmissionForm(request.POST)
        if form.is_valid(): # 検証ずみ
            ############################################################
            # フォームからSubmissionを生成，正誤判定し，情報を加えてからDBに保存
            ############################################################
            submission = form.save(commit=False)    # DBに保存せずにインスタンス化
            if utils.check_answer(submission.answer, problem.answer):   # 正答
                submission.accepted = True
                submission.point = problem.point
            else:   # 誤答
                submission.accepted = False
            submission.user = request.user
            submission.problem = problem
            submission.save()   # 保存
            ################
            #  スコアへの反映
            ################
            if contest.is_live(): # コンテスト中はスコアに反映する
                ######################
                # ProblemScoreへの反映
                ######################
                try:    # 存在チェック
                    problem_score = models.ProblemScore.objects.get(user=request.user, problem=problem)
                except: # 存在しなければ新たに作成する
                    problem_score = models.ProblemScore.objects.create(
                        user=request.user,
                        problem=problem,
                    )
                if problem_score.time_sec == 0: # まだACしていない場合，スコア変動の可能性がある
                    if submission.accepted: # AC：得点が決まる
                        # 時間(s)と得点を決定
                        problem_score.time_sec = (submission.submission_date - contest.start_date).total_seconds()
                        problem_score.score = submission.point  # 得点を更新
                        ######################
                        # ContestScoreへの反映
                        ######################
                        contest_score = models.ContestScore.objects.get(contest=contest, user=request.user)
                        contest_score.penalty += problem_score.penalty      # ペナルティ加算
                        contest_score.score += problem_score.score          # スコア加算
                        # 時間(s) = 最終の初ACの時間(s) + ペナルティ数 * ペナルティ * 60
                        contest_score.time_sec = problem_score.time_sec + contest_score.penalty * contest.penalty * 60
                        contest_score.save()    # 保存
                    else:   # WA：ペナルティ加算
                        problem_score.penalty += 1
                problem_score.save()    # 保存
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
        if not request.user.is_authenticated:   # 要ログイン
            return redirect("users:index")
        contest = models.Contest.objects.get(short_name=short_name)
        submissions = models.Submission.objects.filter(problem__contest=contest).order_by("-submission_date")
        if contest.is_live():   # 開催中はユーザは自分の提出のみ見られる
            submissions = submissions.filter(user=request.user)
        context = {
            "contest": contest,
            "submissions": submissions,
        }
        return render(request, "contests/submissions.html", context)

submissions_view = SubmissionsView.as_view()

class SubmissionsMeView(View):
    def get(self, request, short_name, *args, **kwargs):
        if not request.user.is_authenticated:   # 要ログイン
            return redirect("users:index")
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
        contest = models.Contest.objects.get(short_name=short_name)
        problems = sorted(list(models.Problem.objects.filter(contest=contest)), key=lambda x: x.order)
        problem_scores = models.ProblemScore.objects.filter(problem__in=problems)
        contest_scores = sorted(list(models.ContestScore.objects.filter(contest=contest)), key=lambda x: (-x.score, x.time_sec))
        table_rows = [{
                "order": i+1,
                "user": contest_score.user,
                "score": contest_score.score,
                "time": contest_score.get_time_str,
                "penalty": contest_score.penalty,
                "problem_scores": sorted(list(problem_scores.filter(user=contest_score.user)), key=lambda x: x.problem.order),
            } for i, contest_score in enumerate(contest_scores)]

        context = {
            "contest": models.Contest.objects.get(short_name=short_name),
            "problems": problems,
            "contest_scores": contest_scores,
            "table_rows": table_rows,
        }
        return render(request, "contests/standings.html", context)

standings_view = StandingsView.as_view()