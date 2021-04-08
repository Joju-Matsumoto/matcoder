from django.urls import path

from . import views

app_name = "contests"
urlpatterns = [
    path("", views.index_view, name="index"),
    path("code_test/", views.code_test_view, name="code_test"),
    path("<str:short_name>/", views.contest_detail_view, name="contest_detail"),
    path("<str:short_name>/problems/", views.problems_view, name="problems"),
    path("<str:short_name>/problems/<int:problem_id>/", views.problem_detail_view, name="problem_detail"),
    path("<str:short_name>/submissions/", views.submissions_view, name="submissions"),
    path("<str:short_name>/submissions/me/", views.submissions_me_view, name="submissions_me"),
    path("<str:short_name>/submissions/<int:submission_id>/", views.submission_detail_view, name="submission_detail"),
    path("<str:short_name>/standings/", views.standings_view, name="standings"),
]
