# Generated by Django 2.1 on 2018-12-24 21:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('abstracts', '0008_auto_20181224_1552'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='appellation',
            unique_together=set(),
        ),
        migrations.RemoveField(
            model_name='appellation',
            name='author',
        ),
    ]