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