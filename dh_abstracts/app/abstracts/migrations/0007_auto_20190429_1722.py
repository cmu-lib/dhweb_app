# Generated by Django 2.1 on 2019-04-29 21:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('abstracts', '0006_auto_20190429_1717'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='institution',
            options={'ordering': ['name']},
        ),
    ]