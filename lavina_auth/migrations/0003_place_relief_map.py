# Generated by Django 4.0.2 on 2022-04-11 15:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lavina_auth', '0002_place_owner'),
    ]

    operations = [
        migrations.AddField(
            model_name='place',
            name='relief_map',
            field=models.JSONField(blank=True, null=True),
        ),
    ]