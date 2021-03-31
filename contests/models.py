from django.db import models
from django.conf import settings
from django.utils import timezone

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

class Problem(models.Model):
    """問題モデル"""
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

    def __str__(self):
        return "problem:{}, user:{}".format(self.problem, self.user)
    