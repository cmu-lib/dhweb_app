# Generated by Django 2.1 on 2019-01-02 20:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('abstracts', '0032_auto_20190102_1503'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='appellation',
            unique_together={('first_name', 'last_name')},
        ),
    ]