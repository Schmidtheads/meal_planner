# Generated by Django 2.2.16 on 2020-11-07 03:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cookbook', '0002_auto_20201106_2243'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cookbook',
            name='edition',
            field=models.CharField(blank=True, max_length=20),
        ),
    ]