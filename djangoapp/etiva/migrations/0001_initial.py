# Generated by Django 5.0.3 on 2024-11-05 04:09

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ActivityType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type_name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('activity_name', models.CharField(max_length=255)),
                ('activity_date', models.DateField()),
                ('activity_time', models.TimeField()),
                ('responsible_person', models.CharField(max_length=255)),
                ('location', models.CharField(max_length=255)),
                ('activity_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='etiva.activitytype')),
            ],
        ),
        migrations.CreateModel(
            name='Participant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('cpf', models.CharField(max_length=11, unique=True)),
                ('phone_number', models.CharField(max_length=15)),
                ('slug', models.SlugField(blank=True, unique=True)),
                ('activities', models.ManyToManyField(blank=True, related_name='participants', to='etiva.activity')),
            ],
        ),
    ]