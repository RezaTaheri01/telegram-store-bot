# Generated by Django 5.1.4 on 2024-12-15 21:24

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='UserData',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('mobile_number', models.CharField(max_length=20, null=True)),
                ('username', models.CharField(max_length=100, unique=True)),
                ('balance', models.IntegerField(default=0)),
            ],
        ),
    ]
