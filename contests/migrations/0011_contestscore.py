# Generated by Django 3.1.7 on 2021-03-31 08:36

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contests', '0010_auto_20210331_1720'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContestScore',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.IntegerField(default=0, verbose_name='得点')),
                ('time', models.DateTimeField(default=datetime.datetime(2021, 3, 31, 8, 36, 11, 991685, tzinfo=utc), verbose_name='時間')),
                ('contest', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contests.contest', verbose_name='コンテスト')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='ユーザ')),
            ],
        ),
    ]