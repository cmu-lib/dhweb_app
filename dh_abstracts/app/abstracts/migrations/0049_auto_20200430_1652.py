# Generated by Django 3.0.5 on 2020-04-30 20:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('abstracts', '0048_auto_20200430_1649'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='conference',
            unique_together=set(),
        ),
    ]
