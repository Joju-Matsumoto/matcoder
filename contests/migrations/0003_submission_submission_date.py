# Generated by Django 3.1.7 on 2021-03-27 16:12

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('contests', '0002_auto_20210328_0056'),
    ]

    operations = [
        migrations.AddField(
            model_name='submission',
            name='submission_date',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='ζεΊζ₯ζ'),
        ),
    ]
