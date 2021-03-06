# Generated by Django 3.0.5 on 2020-04-03 17:56

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('abstracts', '0025_author_appellations_index'),
    ]

    operations = [
        migrations.AddField(
            model_name='author',
            name='last_updated',
            field=models.DateTimeField(auto_now=True, db_index=True),
        ),
        migrations.AddField(
            model_name='author',
            name='user_last_updated',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='authors_last_updated', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='institution',
            name='last_updated',
            field=models.DateTimeField(auto_now=True, db_index=True),
        ),
        migrations.AddField(
            model_name='institution',
            name='user_last_updated',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='institutions_last_updated', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='organizer',
            name='last_updated',
            field=models.DateTimeField(auto_now=True, db_index=True),
        ),
        migrations.AddField(
            model_name='organizer',
            name='user_last_updated',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='organizers_last_updated', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='work',
            name='user_last_updated',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='works_last_updated', to=settings.AUTH_USER_MODEL),
        ),
    ]
