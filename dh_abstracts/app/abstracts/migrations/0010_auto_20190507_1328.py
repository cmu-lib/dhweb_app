# Generated by Django 2.2 on 2019-05-07 17:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('abstracts', '0009_auto_20190506_1016'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='seriesmembership',
            unique_together=set(),
        ),
        migrations.RemoveField(
            model_name='seriesmembership',
            name='number',
        ),
    ]
