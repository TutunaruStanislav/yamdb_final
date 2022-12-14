# Generated by Django 2.2.16 on 2022-04-28 16:01

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('reviews', '0003_user_bio'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(
                choices=[('USER', 'user'), ('MODERATOR', 'moderator'),
                         ('ADMIN', 'admin')], default='USER', max_length=1),
        ),
    ]
