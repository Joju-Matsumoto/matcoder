from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.timezone import localtime

from colorfield.fields import ColorField

from . import utils


class Contest(models.Model):
    """コンテストモデル"""
    title = models.CharField(
        verbose_name="タイトル",
        max_length=255,
    )
    abstract = models.TextField(
        verbose_name="概要",
        max_length=2000,
    )
    short_name = models.CharField(
        verbose_name="省略形",
        max_length=20,
        unique=True,
        default="null",
    )
    start_date = models.DateTimeField(
        verbose_name="開始日時",
    )
    end_date = models.DateTimeField(
        verbose_name="終了日時",
    )
    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        verbose_name="参加者",
        blank=True,
    )
    penalty = models.IntegerField(
        verbose_name="ペナルティ(分)",
        default=5,
    )

    def __str__(self):
        return self.title
    
    def is_live(self) -> bool:
        now = timezone.now()
        return self.start_date <= now <= self.end_date
    
    def is_past_contest(self) -> bool:
        now = timezone.now()
        return self.end_date < now
    
    def is_future_contest(self) -> bool:
        now = timezone.now()
        return now < self.start_date
    
    def get_start_time_str(self) -> str:
        """ コンテスト開始時刻を「21-04-04 (月) 21:00」の形式の文字列で返す
        """
        return utils.datetime_str(self.start_date)
    
    def get_end_time_str(self) -> str:
        """ コンテスト終了時刻を「21-04-04 (月) 22:30」の形式の文字列で返す
        """
        return utils.datetime_str(self.end_date)
    
    def get_time_str(self) -> str:
        """ 00:00の形式でコンテスト時間を返す
        """
        dt = self.end_date - self.start_date
        hour = int(dt.total_seconds()) // 3600
        minute = int((dt.total_seconds()) % 3600) // 60
        return f"{hour:02d}:{minute:02d}"
    
    def get_time_hour(self) -> int:
        """ 分単位でコンテスト時間を返す
        """
        dt = self.end_date - self.start_date
        minute = int(dt.total_seconds()) // 60
        return minute


class Author(models.Model):
    """コンテスト作者モデル"""
    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        verbose_name="作者",
        blank=True,
    )
    contest = models.ForeignKey(
        Contest,
        on_delete=models.CASCADE,
        verbose_name="コンテスト",
    )

    def __str__(self):
        return "Contest:{} author:{}".format(self.contest, ",".join(map(str, self.users.all())))
    
    def get_author_names_str(self) -> str:
        """色付きユーザーネームの文字列を返す"""
        return ",".join(map(lambda x: x.get_colored_username(), self.users.all()))


class Problem(models.Model):
    """問題モデル"""
    order = models.CharField(
        verbose_name="問題番号(アルファベット)",
        max_length=5,
        default="A",
    )
    title = models.CharField(
        verbose_name="タイトル",
        max_length=100,
    )
    question = models.TextField(
        verbose_name="問題",
        max_length=2000,
    )
    answer = models.TextField(
        verbose_name="正解",
        max_length=2000,
    )
    contest = models.ForeignKey(
        Contest,
        verbose_name="コンテスト",
        on_delete=models.CASCADE,
    )
    point = models.IntegerField(
        verbose_name="スコア",
        default=0,
    )

    def __str__(self):
        return self.title
    
    def total_test_case(self) -> int:
        return len(TestCase.objects.filter(problem=self))


class Submission(models.Model):
    answer = models.TextField(
        verbose_name="回答",
        blank=False,
        null=False,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="提出者",
        on_delete=models.CASCADE,
    )
    problem = models.ForeignKey(
        Problem,
        verbose_name="問題",
        on_delete=models.CASCADE,
    )
    submission_date = models.DateTimeField(
        verbose_name="提出日時",
        default=timezone.now,
    )
    status = models.CharField(
        verbose_name="状態",
        max_length=10,
        default="WAIT",
    )
    accepted = models.BooleanField(
        verbose_name="結果",
        default=False,
    )
    point = models.IntegerField(
        verbose_name="得点",
        default=0,
    )
    total_test_case = models.IntegerField(
        verbose_name="テストケースの数",
        default=0,
    )
    judged_test_case = models.IntegerField(
        verbose_name="ジャッジ済テストケースの数",
        default=0,
    )

    def __str__(self):
        return "problem:{}, user:{}".format(self.problem.title, self.user.username)
    
    def get_date_str(self):
        dt = localtime(self.submission_date)
        return dt.strftime("%Y-%m-%d %H:%M:%S")


class ProblemScore(models.Model):
    problem = models.ForeignKey(
        Problem,
        verbose_name="問題",
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="参加者",
        on_delete=models.CASCADE,
    )
    penalty = models.IntegerField(
        verbose_name="ペナルティ",
        default=0,
    )
    score = models.IntegerField(
        verbose_name="得点",
        default=0,
    )
    time_sec = models.IntegerField(
        verbose_name="時間(s)",
        default=0,
    )

    def __str__(self):
        return "problem:{}, user:{}".format(self.problem.title, self.user.username)
    
    def get_time_str(self) -> str:
        minutes = self.time_sec // 60
        second = self.time_sec % 60
        return f"{minutes:02d}:{second:02d}"


class ContestScore(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="ユーザ",
        on_delete=models.CASCADE,
    )
    contest = models.ForeignKey(
        Contest,
        verbose_name="コンテスト",
        on_delete=models.CASCADE,
    )
    score = models.IntegerField(
        verbose_name="得点",
        default=0,
    )
    penalty = models.IntegerField(
        verbose_name="ペナルティ",
        default=0,
    )
    time_sec = models.IntegerField(
        verbose_name="時間(s)",
        default=0,
    )

    def __str__(self):
        return "contest:{}, user:{}".format(self.contest.title, self.user.username)
    
    def get_time_str(self) -> str:
        minutes = self.time_sec // 60
        second = self.time_sec % 60
        return f"{minutes:02d}:{second:02d}"
    

class TestCase(models.Model):
    problem = models.ForeignKey(
        Problem,
        verbose_name="問題",
        on_delete=models.CASCADE,
    )
    title = models.CharField(
        verbose_name="タイトル",
        max_length=20,
    )
    note = models.TextField(
        verbose_name="備考",
        max_length=200,
    )
    test_input = models.TextField(
        verbose_name="入力",
        max_length=2000,
    )
    test_output = models.TextField(
        verbose_name="出力",
        max_length=2000,
    )
    is_sample = models.BooleanField(
        verbose_name="サンプル",
        default=False,
    )

    def __str__(self):
        return "{}_{}".format(self.problem.title, self.title)


class TestResult(models.Model):
    submission = models.ForeignKey(
        Submission,
        verbose_name="提出",
        on_delete=models.CASCADE,
    )
    test_case = models.ForeignKey(
        TestCase,
        verbose_name="テストケース",
        on_delete=models.CASCADE,
    )
    status = models.CharField(
        verbose_name="状態",
        max_length=10,
        default="WAIT",
    )
    output = models.TextField(
        verbose_name="出力結果",
        max_length=2000,
        blank=True,
        null=True,
    )
    error = models.TextField(
        verbose_name="エラー出力",
        max_length=2000,
        blank=True,
        null=True,
    )

    def __str__(self):
        return "{}_{}".format(self.submission, self.status)


class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="ユーザー",
    )
    color = ColorField(
        default="#000000",
        verbose_name="カラー",
    )
    organization = models.CharField(
        verbose_name="所属",
        max_length=200,
        blank=True,
        null=True,
    )

    def __str__(self):
        return "<UserProfile: {}>".format(self.user.username)
    