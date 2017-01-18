# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone
import uuid
import validate.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True)),
                ('source_url', models.URLField(max_length=2000, null=True)),
                ('file', models.FileField(upload_to=validate.models.upload_to)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('modified', models.DateTimeField(auto_now=True, null=True)),
                ('rendered', models.BooleanField(default=False)),
                ('form_name', models.CharField(max_length=20, null=True, choices=[(b'upload_form', b'File upload'), (b'url_form', b'Downloaded from URL'), (b'text_form', b'Pasted into textarea')])),
            ],
        ),
        migrations.CreateModel(
            name='HXLmapping',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('column_name', models.CharField(max_length=50)),
                ('HXL_tag', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='HXLtags',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('HXL_tag', models.CharField(max_length=50)),
                ('value_type', models.CharField(max_length=40)),
            ],
        ),
        migrations.CreateModel(
            name='Store',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('file_source', models.CharField(max_length=50)),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now)),
                ('indicator_type', models.CharField(max_length=50)),
                ('indicator', models.CharField(max_length=40)),
                ('unit', models.CharField(max_length=50)),
                ('subgroup', models.CharField(max_length=50)),
                ('country', models.CharField(max_length=50)),
                ('country_id', models.CharField(max_length=5)),
                ('date', models.DateField(verbose_name=b'Date')),
                ('source', models.CharField(max_length=5)),
                ('value', models.DecimalField(max_digits=20, decimal_places=5)),
                ('footnote', models.CharField(max_length=200)),
            ],
        ),
    ]
