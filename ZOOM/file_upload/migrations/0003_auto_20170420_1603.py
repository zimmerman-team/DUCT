# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-04-20 16:03
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('file_upload', '0002_auto_20170420_1602'),
    ]

    operations = [
        migrations.AlterField(
            model_name='file',
            name='data_source',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='file_upload.FileSource'),
        ),
    ]