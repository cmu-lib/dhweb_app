# Generated by Django 3.0.5 on 2020-05-21 15:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('abstracts', '0064_auto_20200520_1717'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='keyword',
            name='author_supplied',
        ),
    ]