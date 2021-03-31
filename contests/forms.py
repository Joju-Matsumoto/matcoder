from django import forms

from . import models

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