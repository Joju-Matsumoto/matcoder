from django.urls import path

from . import views

app_name = "contests"
urlpatterns = [
    path("", views.index_view, name="index"),
    path("code_test/", views.code_test_view, name="code_test"),
    path("my_page/", views.my_page_view, name="my_page"),
    path("<str:short_name>/", views.contest_detail_view, name="contest_detail"),
    path("<str:short_name>/problems/", views.problems_view, name="problems"),
    path("<str:short_name>/problems/<int:problem_id>/", views.problem_detail_view, name="problem_detail"),
    path("<str:short_name>/submissions/", views.submissions_view, name="submissions"),
    path("<str:short_name>/submissions/me/", views.submissions_me_view, name="submissions_me"),
    path("<str:short_name>/submissions/<int:submission_id>/", views.submission_detail_view, name="submission_detail"),
    path("<str:short_name>/standings/", views.standings_view, name="standings"),
    # 編集ページ
    path("<str:short_name>/edit/", views.contest_detail_edit_view, name="contest_detail_edit"),
    path("<str:short_name>/problems/edit/", views.problems_edit_view, name="problems_edit"),
    path("<str:short_name>/problems/<int:problem_id>/edit/", views.problem_detail_edit_view, name="problem_detail_edit"),
    path("<str:short_name>/problems/<int:problem_id>/test_case/", views.test_case_edit_view, name="test_case_add"),     # 追加の場合はtest_case_idを指定しない
    path("<str:short_name>/problems/<int:problem_id>/test_case/<int:test_case_id>/", views.test_case_edit_view, name="test_case_edit"), # 編集の場合はtest_case_idを引数に渡す
    path("<str:short_name>/problems/<int:problem_id>/test_case/<int:test_case_id>/delete/", views.test_case_delete_view, name="test_case_delete"), # 削除
]
