# Generated by Django 5.0.3 on 2024-10-22 14:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('credits', '0003_service_profit'),
    ]

    operations = [
        migrations.AddField(
            model_name='service',
            name='slug',
            field=models.SlugField(blank=True, max_length=255, unique=True),
        ),
    ]