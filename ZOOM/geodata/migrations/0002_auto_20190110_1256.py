# Generated by Django 2.1.3 on 2019-01-10 12:56

import django.contrib.gis.db.models.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('geodata', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='country',
            name='polygons',
            field=django.contrib.gis.db.models.fields.GeometryCollectionField(blank=True, null=True, srid=4326),
        ),
    ]