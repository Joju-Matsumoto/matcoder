# Generated by Django 3.1.7 on 2021-03-31 07:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contests', '0007_auto_20210331_1600'),
    ]

    operations = [
        migrations.RenameField(
            model_name='score',
            old_name='first_accept_date',
            new_name='accepted_date',
        ),
    ]
