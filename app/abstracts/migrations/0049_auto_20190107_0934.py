# Generated by Django 2.1 on 2019-01-07 14:34

import django.contrib.postgres.indexes
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('abstracts', '0048_auto_20190106_1445'),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name='appellation',
            name='appellation_idx',
        ),
        migrations.RemoveIndex(
            model_name='institution',
            name='abstracts_i_search__bb6726_gin',
        ),
        migrations.RemoveIndex(
            model_name='work',
            name='full_text_idx',
        ),
        migrations.RemoveField(
            model_name='appellation',
            name='search_text',
        ),
        migrations.RemoveField(
            model_name='institution',
            name='search_text',
        ),
        migrations.AlterField(
            model_name='appellation',
            name='first_name',
            field=models.CharField(blank=True, db_index=True, default='', max_length=100),
        ),
        migrations.AddIndex(
            model_name='work',
            index=django.contrib.postgres.indexes.GinIndex(fields=['search_text'], name='abstracts_w_search__cfd9ce_gin'),
        ),
    ]