# Generated by Django 2.1 on 2018-12-30 16:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('abstracts', '0012_organizer_notes'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='affiliation',
            options={'ordering': ['institution', 'department']},
        ),
    ]