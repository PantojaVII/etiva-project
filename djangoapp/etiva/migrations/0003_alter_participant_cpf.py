# Generated by Django 5.0.3 on 2024-11-05 04:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('etiva', '0002_auto_20241105_0110'),
    ]

    operations = [
        migrations.AlterField(
            model_name='participant',
            name='cpf',
            field=models.CharField(max_length=14, unique=True),
        ),
    ]
