from django.contrib import admin

from . import models

# Register your models here.
class ContestAdmin(admin.ModelAdmin):
    model = models.Contest

class ProblemAdmin(admin.ModelAdmin):
    model = models.Problem

class SubmissionAdmin(admin.ModelAdmin):
    model = models.Submission

admin.site.register(models.Contest, ContestAdmin)
admin.site.register(models.Problem, ProblemAdmin)
admin.site.register(models.Submission, SubmissionAdmin)