# Generated by Django 5.0.3 on 2024-08-16 15:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0003_profile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='picture',
            field=models.CharField(blank=True, null=True),
        ),
    ]
