from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.timezone import localtime

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
        dt = localtime(self.start_date)
        return "{}({}){}".format(
            dt.strftime("%Y-%m-%d"),
            utils.day_of_week_to_japanese[dt.strftime("%a")],
            dt.strftime("%H:%M")
        )
    
    def get_time_str(self) -> str:
        dt = self.end_date - self.start_date
        hour = int(dt.total_seconds()) // 3600
        minute = int((dt.total_seconds()) % 3600) // 60
        return f"{hour:02d}:{minute:02d}"

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
    accepted = models.BooleanField(
        verbose_name="結果",
        default=False,
    )
    point = models.IntegerField(
        verbose_name="得点",
        default=0,
    )

    def __str__(self):
        return "problem:{}, user:{}".format(self.problem.title, self.user.username)
    
    def get_date_str(self):
        return self.submission_date.strftime("%Y-%m-%d %H:%M:%S")

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
        return f"{minutes:2d}:{second:2d}"

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
        return f"{minutes:2d}:{second:2d}"
    
    