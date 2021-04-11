import datetime
from threading import Thread

from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import FormView
from django.contrib import messages

# 型アノテーションのためだけのimport...
from users.models import User

from . import models
from . import forms
from . import utils
from . import docker
from . import check_submission


class MyPageView(View):
    def get(self, request):
        context = {}
        if request.user.is_authenticated:
            context["contest_scores"] = models.ContestScore.objects.filter(user=request.user).order_by("-contest__start_date")
            # UserProfileの取得 or 新規作成
            try:
                user_profile = models.UserProfile.objects.get(user=request.user)
            except:
                user_profile = models.UserProfile.objects.create(user=request.user)
            context["user_profile"] = user_profile
            # UserProfileの変更フォーム
            form = forms.UserProfileForm(instance=user_profile)
            context["form"] = form
        return render(request, "contests/my_page.html", context)
    
    def post(self, request):
        if request.user.is_authenticated:
            user_profile = models.UserProfile.objects.get(user=request.user)
            form = forms.UserProfileForm(request.POST, instance=user_profile)
            if form.is_valid():
                form.save()
        return redirect("contests:my_page")

my_page_view = MyPageView.as_view()


class IndexView(View):
    def get(self, request, *args, **kwargs):
        now = timezone.now()
        all_contests = models.Contest.objects.all()
        past_contests = all_contests.filter(end_date__lt=now).order_by("-start_date")
        future_contests = all_contests.filter(start_date__gt=now).order_by("start_date")
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


def enter_contest(contest: models.Contest, user: User):
    """コンテスト参加時の処理をすべて行う．\
    元から存在する場合は初期化する．(得点再計算を考慮)
    """
    
    # コンテストに参加
    if user not in contest.users.all():
        contest.users.add(user)
        contest.save()
    
    # スコアの初期化
    # ContestScoreの初期化
    try:    # 存在する場合
        contest_score = models.ContestScore.objects.get(contest=contest, user=user)
    except: # 存在しない場合は作成
        contest_score = models.ContestScore.objects.create(
            contest=contest,
            user=user,
        )
    contest_score.time_sec = 0
    contest_score.penalty = 0
    contest_score.score = 0
    contest_score.save()
    for problem in contest.problem_set.all():
        # ProblemScoreの初期化
        try:    # 存在する場合
            problem_score = models.ProblemScore.objects.get(user=user, problem=problem)
        except: # 存在しない場合は作成
            problem_score = models.ProblemScore.objects.create(
                user=user,
                problem=problem,
            )
        problem_score.time_sec = 0
        problem_score.penalty = 0
        problem_score.score = 0
        problem_score.save()

class ContestDetailView(View):
    def get(self, request, short_name, *args, **kwargs):
        contest = models.Contest.objects.get(short_name=short_name)
        author = models.Author.objects.get(contest=contest)
        context = {
            "is_live": contest.is_live(),
            "contest": contest,
            "author": author,
            "problems": contest.problem_set.order_by("order"),
            # "start_date_str": contest.get_start_time_str(),
            # "end_date_str": contest.get_end_time_str(),
        }
        return render(request, "contests/contest_detail.html", context)
    
    def post(self, request, short_name, *args, **kwargs):
        contest = models.Contest.objects.get(short_name=short_name)
        if request.user.is_authenticated:   # ログイン済ユーザー
            # コンテスト参加処理
            enter_contest(contest, request.user)
            return redirect("contests:contest_detail", short_name)
        else:
            return redirect("users:index")

contest_detail_view = ContestDetailView.as_view()


class ProblemsView(View):
    def get(self, request, short_name, *args, **kwargs):
        contest = models.Contest.objects.get(short_name=short_name)
        context = {
            "contest": contest,
            "problems": contest.problem_set.order_by("order"),
        }
        return render(request, "contests/problems.html", context)

problems_view = ProblemsView.as_view()


def update_submission(submission: models.Submission, problem: models.Problem, user: User):
    """Submissionの正誤判定と保存
    """
    # user, problemの関連づけ．check_submission内でproblemを取得するため．
    submission.user = user
    submission.problem = problem
    submission.accepted = True  # ACであると仮定しておく．
    submission.total_test_case = problem.total_test_case()    # テストケースの数
    # いったん保存する．test_resultでforeignkeyとして使用するため．
    submission.save()
    # acceptedの更新は冗長な処理になってしまっている
    if check_submission.check_answer(submission):   # 正答
        submission.status = "AC"
        submission.accepted = True
        submission.point = problem.point
    else:   # 誤答
        submission.accepted = False
    # 保存
    submission.save()

def update_contest_score(problem_score: models.ProblemScore, contest: models.Contest, user: User):
    """ContestScoreの更新
    """
    # ContestScoreの更新
    try:
        contest_score = models.ContestScore.objects.get(contest=contest, user=user)
    except: # 念のため
        contest_score = models.ContestScore.objects.create(
            contest=contest,
            user=user,
        )
    contest_score.penalty += problem_score.penalty      # ペナルティ加算
    contest_score.score += problem_score.score          # スコア加算
    # 時間(s) = 最終の初ACの時間(s) + ペナルティ数 * ペナルティ * 60
    contest_score.time_sec = problem_score.time_sec + contest_score.penalty * contest.penalty * 60
    contest_score.save()    # 保存

def update_problem_score(submission: models.Submission, contest: models.Contest, problem: models.Problem, user: User):
    """スコア(ContestScore, ProblemScore)の更新
    """

    # ProblemScoreの更新
    try:
        problem_score = models.ProblemScore.objects.get(user=user, problem=problem)
    except: # 念のため
        problem_score = models.ProblemScore.objects.create(
            user=user,
            problem=problem,
        )
    
    # まだACしていない場合，スコア変動の可能性がある
    if problem_score.time_sec == 0:
        if submission.accepted: # AC：時間(s)と得点を更新
            problem_score.time_sec = (submission.submission_date - contest.start_date).total_seconds() # 時間更新
            problem_score.score = submission.point  # 得点を更新
            
            # ContestScoreを更新
            update_contest_score(problem_score, contest, user)
        else:   # WA：ペナルティ加算
            problem_score.penalty += 1
    
    problem_score.save()    # 保存

def submit(submission: models.Submission, contest: models.Contest, problem: models.Problem, user: User, force_to_rescore: bool=False):
    """submissionを受け取って，正誤判定を行い，関連するデータベースを更新する
    """
    # Submissionの更新
    update_submission(submission, problem, user)

    # スコアの更新
    if contest.is_live() or force_to_rescore:   # 開催中 or 強制再計算の場合のみ得点計算
        # ProblemScoreの更新．必要に応じて，ContestScoreの更新も行われる
        update_problem_score(submission, contest, problem, user)

class ProblemDetailView(View):
    def get(self, request, short_name, problem_id, *args, **kwargs):
        contest = models.Contest.objects.get(short_name=short_name)
        problem = models.Problem.objects.get(pk=problem_id)
        test_cases = models.TestCase.objects.filter(problem=problem, is_sample=True)
        context = {
            "contest": contest,
            "problem": problem,
            "form": forms.SubmissionForm(),
            "test_cases": test_cases,
        }
        return render(request, "contests/problem_detail.html", context)
    
    def post(self, request, short_name, problem_id, *args, **kwargs):
        contest = models.Contest.objects.get(short_name=short_name)
        problem = models.Problem.objects.get(pk=problem_id)
        form = forms.SubmissionForm(request.POST)
        if form.is_valid(): # 検証ずみ
            submission = form.save(commit=False)    # DBに保存せずにインスタンス化
            # 提出処理
            # submit(submission, contest, problem, request.user, force_to_rescore=False)
            # スレッドに任せる
            thread = Thread(target=submit, args=(submission, contest, problem, request.user, False,))
            thread.start()
            # リダイレクト
            return redirect("contests:submissions", short_name)
        else:   # 検証エラー
            test_cases = models.TestCase.objects.filter(problem=problem, is_sample=True)
            context = {
                "contest": contest,
                "problem": problem,
                "form": form,
                "test_cases": test_cases,
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
            "test_results": models.TestResult.objects.filter(submission=submission),
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


class CodeTestView(View):
    def get(self, request):
        form = forms.CodeSubmissionForm(request.session.get("form_data"))
        result_status = request.session.get("result_status")
        result_output = request.session.get("result_output")
        result_error = request.session.get("result_error")
        context = {
            "form": form,
            "result_status": result_status,
            "result_output": result_output,
            "result_error": result_error,
        }
        return render(request, "contests/code_test.html", context)
    
    def post(self, request):
        form = forms.CodeSubmissionForm(request.POST)
        if not request.user.is_authenticated:
            messages.warning(request, "ログインしてください！")
            return redirect("contests:code_test")
        if form.is_valid():
            request.session["form_data"] = request.POST
            code = form.cleaned_data["code"]
            test_input = form.cleaned_data["test_input"]
            test_output = form.cleaned_data["test_output"]
            status, output, error = docker.exec_code_python(code, request.user.username, test_input, test_output)
            request.session["result_status"] = status
            request.session["result_output"] = output
            request.session["result_error"] = error
            return redirect("contests:code_test")
        else:
            context = {
                "form": form,
            }
            return render(request, "contests/code_test.html", context)

code_test_view = CodeTestView.as_view()


class ContestDetailEditView(View):
    def get(self, request, short_name, *args, **kwargs):
        contest = models.Contest.objects.get(short_name=short_name)
        context = {
            "contest": contest,
            "form": forms.ContestEditForm(instance=contest),
        }
        return render(request, "contests/contest_detail_edit.html", context)
    
    def post(self, request, short_name, *args, **kwargs):
        contest = models.Contest.objects.get(short_name=short_name)
        form = forms.ContestEditForm(request.POST, instance=contest)
        if form.is_valid():
            form.save()
            return redirect("contests:contest_detail_edit", short_name)
        else:
            context = {
                "contest": contest,
                "form": form,
            }
            return render(request, "contests/contest_detail_edit.html", context)

contest_detail_edit_view = ContestDetailEditView.as_view()


class ProblemsEditView(View):
    def get(self, request, short_name, *args, **kwargs):
        contest = models.Contest.objects.get(short_name=short_name)
        problems = contest.problem_set.order_by("order")
        form = forms.ProblemsAddForm()
        context = {
            "contest": contest,
            "problems": problems,
            "form": form,
        }
        return render(request, "contests/problems_edit.html", context)
    
    def post(self, request, short_name, *args, **kwargs):
        contest = models.Contest.objects.get(short_name=short_name)
        form = forms.ProblemsAddForm(request.POST)
        if form.is_valid():
            problem = form.save(commit=False)
            problem.question = "ここに問題文を入力"
            problem.answer = "ここにサンプルの答えを入力"
            problem.contest = contest
            problem.point = 100
            problem.save()
            print("made:", problem)
            return redirect("contests:problem_detail_edit", contest.short_name, problem.pk)
        else:
            problems = contest.problem_set.order_by("order")
            context = {
                "contest": contest,
                "problems": problems,
                "form": form,
            }
            return render(request, "contests/problems_edit.html", context)
            

problems_edit_view = ProblemsEditView.as_view()


class ProblemDetailEditView(View):
    def get(self, request, short_name, problem_id, *args, **kwargs):
        contest = models.Contest.objects.get(short_name=short_name)
        problem = models.Problem.objects.get(pk=problem_id)
        form = forms.ProblemEditForm(instance=problem)
        test_cases = models.TestCase.objects.filter(problem=problem)
        context = {
            "contest": contest,
            "problem": problem,
            "form": form,
            "test_cases": test_cases,
        }
        return render(request, "contests/problem_detail_edit.html", context)
    
    def post(self, request, short_name, problem_id, *args, **kwargs):
        contest = models.Contest.objects.get(short_name=short_name)
        problem = models.Problem.objects.get(pk=problem_id)
        form = forms.ProblemEditForm(request.POST, instance=problem)
        if form.is_valid():
            problem = form.save()
            return redirect("contests:problem_detail_edit", contest.short_name, problem.pk)
        else:
            test_cases = models.TestCase.objects.filter(problem=problem)
            context = {
                "contest": contest,
                "problem": problem,
                "form": form,
                "test_cases": test_cases,
            }
            return render(request, "contests/problem_detail_edit.html", context)

problem_detail_edit_view = ProblemDetailEditView.as_view()


class TestCaseEditView(View):
    def get(self, request, short_name, problem_id, test_case_id=None, *args, **kwargs):
        contest = models.Contest.objects.get(short_name=short_name)
        problem = models.Problem.objects.get(pk=problem_id)
        test_case = None
        is_add_page = True
        if test_case_id is not None:
            test_case = models.TestCase.objects.filter(problem=problem).get(pk=test_case_id)
            is_add_page = False
        form = forms.TestCaseEditForm(instance=test_case)
        context = {
            "contest": contest,
            "problem": problem,
            "form": form,
            "is_add_page": is_add_page,
        }
        return render(request, "contests/test_case_edit.html", context)
    
    def post(self, request, short_name, problem_id, test_case_id=None, *args, **kwargs):
        contest = models.Contest.objects.get(short_name=short_name)
        problem = models.Problem.objects.get(pk=problem_id)
        test_case = None
        is_add_page = True
        if test_case_id is not None:
            test_case = models.TestCase.objects.filter(problem=problem).get(pk=test_case_id)
            is_add_page = False
        form = forms.TestCaseEditForm(request.POST, instance=test_case)
        if form.is_valid():
            test_case = form.save(commit=False)
            test_case.problem = problem
            test_case.save()
            # return redirect("contests:test_case_edit", contest.short_name, problem.pk, test_case.id)
            return redirect("contests:problem_detail_edit", contest.short_name, problem.pk)
        else:
            context = {
                "contest": contest,
                "problem": problem,
                "form": form,
                "is_add_page": is_add_page,
            }
            return render(request, "contests/test_case_edit.html", context)

test_case_edit_view = TestCaseEditView.as_view()


class TestCaseDeleteView(View):
    def post(self, request, short_name, problem_id, test_case_id, *args, **kwargs):
        # contest = models.Contest.objects.get(short_name=short_name)
        # problem = models.Problem.objects.get(pk=problem_id)
        test_case = models.TestCase.objects.get(pk=test_case_id)
        test_case.delete()
        return redirect("contests:problem_detail_edit", short_name, problem_id)

test_case_delete_view = TestCaseDeleteView.as_view()