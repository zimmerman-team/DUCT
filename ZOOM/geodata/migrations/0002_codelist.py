# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-01-23 13:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('geodata', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Codelist',
            fields=[
                ('name', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('description', models.TextField(blank=True, max_length=1000, null=True)),
                ('count', models.CharField(blank=True, max_length=10, null=True)),
                ('fields', models.CharField(blank=True, max_length=255, null=True)),
                ('date_updated', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
