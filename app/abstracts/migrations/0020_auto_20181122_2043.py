# Generated by Django 2.1 on 2018-11-23 01:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('abstracts', '0019_auto_20181122_0744'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='conference',
            name='organizers',
        ),
        migrations.AddField(
            model_name='organizer',
            name='conferences_organized',
            field=models.ManyToManyField(related_name='organizers', to='abstracts.Conference'),
        ),
    ]