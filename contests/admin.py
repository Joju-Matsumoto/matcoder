from django.contrib import admin

from . import models

# Register your models here.
class ContestAdmin(admin.ModelAdmin):
    model = models.Contest

class ProblemAdmin(admin.ModelAdmin):
    model = models.Problem

class SubmissionAdmin(admin.ModelAdmin):
    model = models.Submission

class ProblemScoreAdmin(admin.ModelAdmin):
    model = models.ProblemScore

class ContestScoreAdmin(admin.ModelAdmin):
    model = models.ContestScore

class TestCaseAdmin(admin.ModelAdmin):
    model = models.TestCase

class TestResultAdmin(admin.ModelAdmin):
    model = models.TestResult

admin.site.register(models.Contest, ContestAdmin)
admin.site.register(models.Problem, ProblemAdmin)
admin.site.register(models.Submission, SubmissionAdmin)
admin.site.register(models.ProblemScore, ProblemScoreAdmin)
admin.site.register(models.ContestScore, ContestScoreAdmin)
admin.site.register(models.TestCase, TestCaseAdmin)
admin.site.register(models.TestResult, TestResultAdmin)