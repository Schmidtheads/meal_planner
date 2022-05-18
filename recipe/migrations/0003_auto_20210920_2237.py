# Generated by Django 3.1.5 on 2021-09-21 02:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipe', '0002_auto_20210520_2148'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recipe',
            name='recipe_types',
        ),
        migrations.AddField(
            model_name='recipetype',
            name='recipes',
            field=models.ManyToManyField(to='recipe.Recipe'),
        ),
    ]