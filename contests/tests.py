import datetime

import django
from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from . import models

def create_contest(short_name: str, title="test", abstract="test abstract", \
    start_date=timezone.now(), end_date=timezone.now()+datetime.timedelta(hours=1)):
    """Contest作成のutil．short_name は必ず必要
    デフォルトでは現在時刻から開始して，1時間で終了するコンテストが作成される
    """
    contest = models.Contest.objects.create(
        title=title,
        abstract=abstract,
        short_name=short_name,
        start_date=start_date,
        end_date=end_date,
    )
    return contest

def get_delta_time(days=0, hours=0, minutes=0, seconds=0):
    """現在の時刻からdeltatime進んだ時刻を返す"""
    return localtime(timezone.now()) + datetime.timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)

# Create your tests here.
class ContestTest(TestCase):
    def test_contest_is_past_contest(self):
        """過去のコンテストである"""
        start_date = get_delta_time(seconds=-2)
        end_date = get_delta_time(seconds=-1)
        contest = create_contest(
            short_name="past_contest",
            start_date=start_date,
            end_date=end_date,
        )
        self.assertEqual(contest.is_past_contest(), True)
        self.assertEqual(contest.is_live(), False)
        self.assertEqual(contest.is_future_contest(), False)
    
    def test_contest_is_not_past_but_live_contest(self):
        """現在開催中のコンテストである"""
        start_date = get_delta_time(seconds=-1)
        end_date = get_delta_time(seconds=1)
        contest = create_contest(
            short_name="past_contest",
            start_date=start_date,
            end_date=end_date,
        )
        self.assertEqual(contest.is_past_contest(), False)
        self.assertEqual(contest.is_live(), True)
        self.assertEqual(contest.is_future_contest(), False)
    
    def test_contest_is_not_past_but_future_contest(self):
        """開催予定のコンテストである"""
        start_date = get_delta_time(seconds=1)
        end_date = get_delta_time(seconds=2)
        contest = create_contest(
            short_name="past_contest",
            start_date=start_date,
            end_date=end_date,
        )
        self.assertEqual(contest.is_past_contest(), False)
        self.assertEqual(contest.is_live(), False)
        self.assertEqual(contest.is_future_contest(), True)

class ContestIndexViewTest(TestCase):
    def test_chcek_context_contents_and_its_types(self):
        """contextのkeyが正しいかどうか，valueのtypeが正しいかどうか．
        """
        response = self.client.get(reverse("contests:index"))
        context = response.context
        self.assertNotEqual(context.get("past_contests"), None)
        self.assertNotEqual(context.get("live_contests"), None)
        self.assertNotEqual(context.get("future_contests"), None)
        self.assertEqual(type(context["past_contests"]), django.db.models.query.QuerySet)
        self.assertEqual(type(context["live_contests"]), django.db.models.query.QuerySet)
        self.assertEqual(type(context["future_contests"]), django.db.models.query.QuerySet)
        

    def test_contest_list(self):
        """contextの振り分け処理が正しく行われているかどうか
        (過去の->"past_contests", 開催中の->"live_contests", 開催予定の->"future_contests")
        """
        past_contest = create_contest(
            title="past1",
            short_name="past",
            start_date=get_delta_time(seconds=-5),
            end_date=get_delta_time(seconds=-1),
        )
        live_contest = create_contest(
            title="live1",
            short_name="live",
            start_date=get_delta_time(seconds=-1),
            end_date=get_delta_time(seconds=1),
        )
        future_contest = create_contest(
            title="future1",
            short_name="future",
            start_date=get_delta_time(seconds=1),
            end_date=get_delta_time(seconds=2),
        )
        past_contest = create_contest(
            title="past2",
            short_name="past2",
            start_date=get_delta_time(days=-5),
            end_date=get_delta_time(days=-1),
        )
        live_contest = create_contest(
            title="live2",
            short_name="live2",
            start_date=get_delta_time(hours=-1),
            end_date=get_delta_time(hours=1),
        )
        future_contest = create_contest(
            title="future2",
            short_name="future2",
            start_date=get_delta_time(minutes=1),
            end_date=get_delta_time(minutes=2),
        )
        response = self.client.get(reverse("contests:index"))
        self.assertQuerysetEqual(
            response.context["past_contests"],
            ["<Contest: past1>", "<Contest: past2>"],
            ordered=False,
        )
        self.assertQuerysetEqual(
            response.context["live_contests"],
            ["<Contest: live1>", "<Contest: live2>"],
            ordered=False,
        )
        self.assertQuerysetEqual(
            response.context["future_contests"],
            ["<Contest: future1>", "<Contest: future2>"],
            ordered=False,
        )