# Generated by Django 3.1.7 on 2021-03-31 09:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contests', '0013_problem_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='contestscore',
            name='penalty',
            field=models.IntegerField(default=0, verbose_name='ペナルティ'),
        ),
    ]
