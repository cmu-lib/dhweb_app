# Generated by Django 2.1 on 2018-12-31 14:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('abstracts', '0019_auto_20181230_2330'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='seriesmembership',
            options={'ordering': ['-conference__year']},
        ),
    ]
