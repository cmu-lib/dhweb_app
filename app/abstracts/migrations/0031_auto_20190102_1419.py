# Generated by Django 2.1 on 2019-01-02 19:19

import django.contrib.postgres.indexes
import django.contrib.postgres.search
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('abstracts', '0030_auto_20190102_1400'),
    ]

    operations = [
        migrations.AddField(
            model_name='author',
            name='search_text',
            field=django.contrib.postgres.search.SearchVectorField(editable=False, null=True),
        ),
        migrations.AddIndex(
            model_name='author',
            index=django.contrib.postgres.indexes.GinIndex(fields=['search_text'], name='author_text_idx'),
        ),
    ]
