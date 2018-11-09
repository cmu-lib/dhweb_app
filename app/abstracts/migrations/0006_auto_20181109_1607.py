# Generated by Django 2.1 on 2018-11-09 21:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('abstracts', '0005_auto_20181109_1344'),
    ]

    operations = [
        migrations.AddField(
            model_name='author',
            name='appellations',
            field=models.ManyToManyField(related_name='author', through='abstracts.AppellationAssertion', to='abstracts.Appellation'),
        ),
        migrations.AddField(
            model_name='author',
            name='departments',
            field=models.ManyToManyField(related_name='members', through='abstracts.DepartmentAssertion', to='abstracts.Department'),
        ),
        migrations.AddField(
            model_name='author',
            name='genders',
            field=models.ManyToManyField(related_name='members', through='abstracts.GenderAssertion', to='abstracts.Gender'),
        ),
        migrations.AddField(
            model_name='author',
            name='institutions',
            field=models.ManyToManyField(related_name='members', through='abstracts.InstitutionAssertion', to='abstracts.Institution'),
        ),
    ]
