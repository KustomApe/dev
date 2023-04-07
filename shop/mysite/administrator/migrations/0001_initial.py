# Generated by Django 2.2.4 on 2020-01-15 01:42

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Admin',
            fields=[
                ('admin_id', models.CharField(max_length=128, primary_key=True, serialize=False, unique=True)),
                ('password', models.CharField(max_length=256)),
            ],
            options={
                'verbose_name': '管理者',
                'verbose_name_plural': '管理者',
                'ordering': ['-admin_id'],
            },
        ),
    ]