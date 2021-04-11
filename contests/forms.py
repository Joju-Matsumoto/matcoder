from django import forms

from colorfield.widgets import ColorWidget

from . import models


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = models.UserProfile

        fields = ["color", "organization"]

        labels = {
            "color": "ユーザーカラー",
            "oorganization": "所属",
        }

        widgets = {
            "color": ColorWidget,
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["color"].widget.attrs["cols"] = "7"
        self.fields["organization"].widget.attrs["style"] = "width: 100%;"


class ContestEditForm(forms.ModelForm):
    """コンテスト編集用のフォーム"""
    class Meta:
        model = models.Contest
        fields = ["abstract", "penalty", "released"]

        labels = {
            "abstract": "概要",
            "penalty": "ペナルティ(分)",
            "released": "公開する",
        }
    
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)


class ProblemsAddForm(forms.ModelForm):
    class Meta:
        model = models.Problem
        fields = ("order", "title")


class ProblemEditForm(forms.ModelForm):
    """問題編集用のフォーム"""
    class Meta:
        model = models.Problem
        fields = ("order", "title", "question", "answer", "point")

        labels = {
            "order": "問題順序",
            "title": "タイトル",
            "question": "問題文",
            "answer": "答えのサンプル",
            "point": "配点",
        }


class TestCaseEditForm(forms.ModelForm):
    """テストケース 追加・編集 用フォーム"""
    class Meta:
        model = models.TestCase
        fields = ("title", "test_input", "test_output", "is_sample")

        labels = {
            "title": "タイトル",
            "test_input": "入力",
            "test_output": "出力",
            "is_sample": "これはサンプル",
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for key, field in self.fields.items():
            if key == "is_sample":
                continue
            field.widget.attrs["class"] = "form-control"
        self.fields["test_input"].widget.attrs["rows"] = 4
        self.fields["test_output"].widget.attrs["rows"] = 4


class SubmissionForm(forms.ModelForm):
    """解答提出用のフォーム"""
    class Meta:
        model = models.Submission
        fields = ("answer",)

        labels = {
            "answer": "解答",
        }
        help_texts = {
            "answer": "解答を入力",
        }


class CodeSubmissionForm(forms.Form):
    code = forms.CharField(
        widget=forms.Textarea,
        help_text="解答欄",
    )
    test_input = forms.CharField(
        widget=forms.Textarea,
        help_text="サンプル入力",
        required=False,
    )
    test_output = forms.CharField(
        widget=forms.Textarea,
        help_text="サンプル出力",
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["code"].widget.attrs["class"] = "form-control"
        self.fields["test_input"].widget.attrs["class"] = "form-control"
        self.fields["test_input"].widget.attrs["rows"] = "2"
        self.fields["test_output"].widget.attrs["class"] = "form-control"
        self.fields["test_output"].widget.attrs["rows"] = "2"