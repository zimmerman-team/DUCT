# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-04-21 14:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('file_upload', '0004_filedtypes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='filedtypes',
            name='line_no',
            field=models.IntegerField(),
        ),
    ]