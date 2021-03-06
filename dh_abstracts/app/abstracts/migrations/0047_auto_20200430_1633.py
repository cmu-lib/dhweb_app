# Generated by Django 3.0.5 on 2020-04-30 20:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('abstracts', '0046_auto_20200430_1307'),
    ]

    operations = [
        migrations.AddField(
            model_name='conference',
            name='attendance',
            field=models.CharField(blank=True, default='', help_text='Summary information about conference attendance, with source links', max_length=2000),
        ),
        migrations.AddField(
            model_name='conference',
            name='contributors',
            field=models.CharField(blank=True, default='', help_text='Individuals or organizations who contributed data about this conference', max_length=2000),
        ),
        migrations.AddField(
            model_name='conference',
            name='primary_contact',
            field=models.CharField(blank=True, default='', max_length=2000),
        ),
        migrations.AddField(
            model_name='conference',
            name='references',
            field=models.CharField(blank=True, default='', help_text='Citations to conference proceedings', max_length=2000),
        ),
    ]
