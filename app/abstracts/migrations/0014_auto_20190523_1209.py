# Generated by Django 2.2 on 2019-05-23 16:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('abstracts', '0013_auto_20190522_1708'),
    ]

    operations = [
        migrations.AlterField(
            model_name='work',
            name='full_text_type',
            field=models.CharField(blank=True, choices=[('', '-----------'), ('xml', 'XML'), ('txt', 'plain text')], default='', max_length=3),
        ),
    ]