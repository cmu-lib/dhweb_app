# Generated by Django 3.0.5 on 2020-04-29 14:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('abstracts', '0035_license_default'),
    ]

    operations = [
        migrations.AlterField(
            model_name='license',
            name='display_abbreviation',
            field=models.CharField(max_length=100, unique=True),
        ),
    ]
