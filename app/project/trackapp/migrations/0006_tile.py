# Generated by Django 5.1.6 on 2025-02-14 20:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trackapp', '0005_alter_userpoi_address_alter_userpoi_city_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tile',
            fields=[
                ('uuid', models.CharField(max_length=36, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
            ],
            options={
                'ordering': ['name'],
            },
        ),
    ]
