# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-04-07 10:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('indicator', '0006_auto_20170312_1440'),
    ]

    operations = [
        migrations.AddField(
            model_name='indicatordatapoint',
            name='unit_of_measure',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
