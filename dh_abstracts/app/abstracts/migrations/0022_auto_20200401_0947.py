# Generated by Django 3.0.4 on 2020-04-01 13:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('abstracts', '0021_work_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='authorship',
            name='last_updated',
            field=models.DateTimeField(auto_now=True, db_index=True),
        ),
        migrations.AddField(
            model_name='work',
            name='last_updated',
            field=models.DateTimeField(auto_now=True, db_index=True),
        ),
    ]