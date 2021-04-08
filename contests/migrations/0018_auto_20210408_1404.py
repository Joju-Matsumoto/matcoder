# Generated by Django 3.1.7 on 2021-04-08 05:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contests', '0017_testcase_testresult'),
    ]

    operations = [
        migrations.AddField(
            model_name='submission',
            name='waiting_judge',
            field=models.BooleanField(default=True, verbose_name='ジャッジ待ち'),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='error',
            field=models.TextField(blank=True, max_length=2000, null=True, verbose_name='エラー出力'),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='output',
            field=models.TextField(blank=True, max_length=2000, null=True, verbose_name='出力結果'),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='status',
            field=models.CharField(default='WAIT', max_length=10, verbose_name='状態'),
        ),
    ]
