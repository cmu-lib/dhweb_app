# Generated by Django 2.1 on 2018-12-29 19:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('abstracts', '0009_auto_20181224_1611'),
    ]

    operations = [
        migrations.CreateModel(
            name='Affiliation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('department', models.CharField(blank=True, default='', max_length=500)),
            ],
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=500, unique=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='department',
            name='institution',
        ),
        migrations.AlterModelOptions(
            name='authorship',
            options={'ordering': ['authorship_order']},
        ),
        migrations.AlterModelOptions(
            name='seriesmembership',
            options={'ordering': ['number']},
        ),
        migrations.RemoveField(
            model_name='authorship',
            name='departments',
        ),
        migrations.RemoveField(
            model_name='authorship',
            name='institutions',
        ),
        migrations.AlterField(
            model_name='institution',
            name='country',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='institutions', to='abstracts.Country'),
        ),
        migrations.DeleteModel(
            name='Department',
        ),
        migrations.AddField(
            model_name='affiliation',
            name='institution',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='affiliations', to='abstracts.Institution'),
        ),
        migrations.AddField(
            model_name='authorship',
            name='affiliations',
            field=models.ManyToManyField(blank=True, related_name='asserted_by', to='abstracts.Affiliation'),
        ),
        migrations.AlterUniqueTogether(
            name='affiliation',
            unique_together={('department', 'institution')},
        ),
    ]