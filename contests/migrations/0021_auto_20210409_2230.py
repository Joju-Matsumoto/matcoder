# Generated by Django 3.1.7 on 2021-04-09 13:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contests', '0020_author'),
    ]

    operations = [
        migrations.AlterField(
            model_name='problem',
            name='order',
            field=models.CharField(default='A', max_length=5, unique=True, verbose_name='問題番号(アルファベット)'),
        ),
    ]
