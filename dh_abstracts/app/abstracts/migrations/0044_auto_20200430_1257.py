# Generated by Django 3.0.5 on 2020-04-30 16:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('abstracts', '0043_remove_conference_venue_abbreviation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='conference',
            name='year',
            field=models.PositiveIntegerField(),
        ),
    ]
