# Generated by Django 2.1 on 2018-12-29 21:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('abstracts', '0011_conference_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='organizer',
            name='notes',
            field=models.TextField(blank=True),
        ),
    ]