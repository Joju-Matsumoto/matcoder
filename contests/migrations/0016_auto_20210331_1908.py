# Generated by Django 3.1.7 on 2021-03-31 10:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contests', '0015_auto_20210331_1859'),
    ]

    operations = [
        migrations.RenameField(
            model_name='contestscore',
            old_name='time',
            new_name='time_sec',
        ),
    ]
