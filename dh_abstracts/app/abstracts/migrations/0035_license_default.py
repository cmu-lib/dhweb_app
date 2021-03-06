# Generated by Django 3.0.5 on 2020-04-29 14:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('abstracts', '0034_auto_20200428_1610'),
    ]

    operations = [
        migrations.AddField(
            model_name='license',
            name='default',
            field=models.BooleanField(default=False, help_text='Make this license the default license applied to any work whose conference has been set to show all full texts.'),
        ),
    ]
