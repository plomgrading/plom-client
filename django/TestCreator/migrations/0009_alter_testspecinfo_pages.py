# Generated by Django 4.0.5 on 2022-07-04 20:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('TestCreator', '0008_testspecinfo_pages'),
    ]

    operations = [
        migrations.AlterField(
            model_name='testspecinfo',
            name='pages',
            field=models.JSONField(default=dict),
        ),
    ]
