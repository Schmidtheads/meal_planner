# Generated by Django 3.1.5 on 2022-09-04 14:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Author',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=25)),
                ('last_name', models.CharField(max_length=25)),
            ],
        ),
        migrations.CreateModel(
            name='Cookbook',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=50)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('publish_date', models.PositiveSmallIntegerField()),
                ('url', models.CharField(blank=True, max_length=200)),
                ('edition', models.CharField(blank=True, max_length=20)),
                ('image', models.ImageField(blank=True, upload_to='images/')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cookbook.author')),
            ],
        ),
    ]
