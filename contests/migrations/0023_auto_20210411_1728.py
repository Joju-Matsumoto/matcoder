# Generated by Django 3.1.7 on 2021-04-11 08:28

import colorfield.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contests', '0022_userprofile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='color',
            field=colorfield.fields.ColorField(default='#000000', max_length=18, verbose_name='カラー'),
        ),
    ]
