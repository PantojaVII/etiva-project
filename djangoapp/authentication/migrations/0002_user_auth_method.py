# Generated by Django 5.0.3 on 2024-08-14 14:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='auth_method',
            field=models.CharField(choices=[('seek', 'Seek'), ('google', 'Google'), ('facebook', 'Facebook'), ('microsoft', 'Microsoft'), ('email', 'Email')], default='seek', max_length=20),
        ),
    ]