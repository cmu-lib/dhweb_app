# Generated by Django 3.0.5 on 2020-04-30 20:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('abstracts', '0050_auto_20200430_1655'),
    ]

    operations = [
        migrations.AlterField(
            model_name='conference',
            name='url',
            field=models.URLField(blank=True, help_text='Public URL for the conference and/or conference program', max_length=500, verbose_name='URL'),
        ),
    ]
