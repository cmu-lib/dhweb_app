# Generated by Django 3.0.4 on 2020-04-01 19:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('abstracts', '0024_authorship_user_last_updated'),
    ]

    operations = [
        migrations.AddField(
            model_name='author',
            name='appellations_index',
            field=models.CharField(blank=True, db_index=True, max_length=4000),
        ),
    ]
