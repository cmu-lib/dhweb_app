# Generated by Django 2.1 on 2018-12-17 20:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('abstracts', '0026_auto_20181217_1446'),
    ]

    operations = [
        migrations.AddField(
            model_name='version',
            name='disciplines',
            field=models.ManyToManyField(blank=True, related_name='versions', to='abstracts.Discipline'),
        ),
        migrations.AddField(
            model_name='version',
            name='keywords',
            field=models.ManyToManyField(blank=True, related_name='versions', to='abstracts.Keyword'),
        ),
        migrations.AddField(
            model_name='version',
            name='languages',
            field=models.ManyToManyField(blank=True, related_name='versions', to='abstracts.Language'),
        ),
        migrations.AddField(
            model_name='version',
            name='topics',
            field=models.ManyToManyField(blank=True, related_name='versions', to='abstracts.Topic'),
        ),
    ]