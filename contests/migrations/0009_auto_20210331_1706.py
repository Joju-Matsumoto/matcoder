# Generated by Django 3.1.7 on 2021-03-31 08:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contests', '0008_auto_20210331_1618'),
    ]

    operations = [
        migrations.AddField(
            model_name='problem',
            name='point',
            field=models.IntegerField(default=0, verbose_name='スコア'),
        ),
        migrations.AddField(
            model_name='submission',
            name='point',
            field=models.IntegerField(default=0, verbose_name='得点'),
        ),
    ]
