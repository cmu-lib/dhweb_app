# Generated by Django 2.1 on 2018-12-31 17:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('abstracts', '0021_auto_20181231_1207'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='work',
            name='submission_type',
        ),
    ]
