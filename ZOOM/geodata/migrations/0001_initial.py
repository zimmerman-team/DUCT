# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-01-19 09:31
from __future__ import unicode_literals

import django.contrib.gis.db.models.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Adm1Region',
            fields=[
                ('adm1_code', models.CharField(max_length=10, primary_key=True, serialize=False)),
                ('OBJECTID_1', models.IntegerField(blank=True, null=True)),
                ('diss_me', models.IntegerField(blank=True, null=True)),
                ('adm1_cod_1', models.CharField(blank=True, max_length=20, null=True)),
                ('iso_3166_2', models.CharField(blank=True, max_length=2, null=True)),
                ('wikipedia', models.CharField(blank=True, max_length=150, null=True)),
                ('adm0_sr', models.IntegerField(blank=True, null=True)),
                ('name', models.CharField(blank=True, max_length=100, null=True)),
                ('name_alt', models.CharField(blank=True, max_length=200, null=True)),
                ('name_local', models.CharField(blank=True, max_length=100, null=True)),
                ('type', models.CharField(blank=True, max_length=100, null=True)),
                ('type_en', models.CharField(blank=True, max_length=100, null=True)),
                ('code_local', models.CharField(blank=True, max_length=100, null=True)),
                ('code_hasc', models.CharField(blank=True, max_length=100, null=True)),
                ('note', models.TextField(blank=True, null=True)),
                ('hasc_maybe', models.CharField(blank=True, max_length=100, null=True)),
                ('region', models.CharField(blank=True, max_length=100, null=True)),
                ('region_cod', models.CharField(blank=True, max_length=100, null=True)),
                ('provnum_ne', models.IntegerField(blank=True, null=True)),
                ('gadm_level', models.IntegerField(blank=True, null=True)),
                ('check_me', models.IntegerField(blank=True, null=True)),
                ('scalerank', models.IntegerField(blank=True, null=True)),
                ('datarank', models.IntegerField(blank=True, null=True)),
                ('abbrev', models.CharField(blank=True, max_length=100, null=True)),
                ('postal', models.CharField(blank=True, max_length=100, null=True)),
                ('area_sqkm', models.CharField(blank=True, max_length=100, null=True)),
                ('sameascity', models.IntegerField(blank=True, null=True)),
                ('labelrank', models.IntegerField(blank=True, null=True)),
                ('featurecla', models.CharField(blank=True, max_length=100, null=True)),
                ('name_len', models.IntegerField(blank=True, null=True)),
                ('mapcolor9', models.IntegerField(blank=True, null=True)),
                ('mapcolor13', models.IntegerField(blank=True, null=True)),
                ('fips', models.CharField(blank=True, max_length=100, null=True)),
                ('fips_alt', models.CharField(blank=True, max_length=100, null=True)),
                ('woe_id', models.IntegerField(blank=True, null=True)),
                ('woe_label', models.CharField(blank=True, max_length=100, null=True)),
                ('woe_name', models.CharField(blank=True, max_length=100, null=True)),
                ('center_location', django.contrib.gis.db.models.fields.PointField(blank=True, null=True, srid=4326)),
                ('sov_a3', models.CharField(blank=True, max_length=3, null=True)),
                ('adm0_a3', models.CharField(blank=True, max_length=3, null=True)),
                ('adm0_label', models.IntegerField(blank=True, null=True)),
                ('admin', models.CharField(blank=True, max_length=100, null=True)),
                ('geonunit', models.CharField(blank=True, max_length=100, null=True)),
                ('gu_a3', models.CharField(blank=True, max_length=3, null=True)),
                ('gn_id', models.IntegerField(blank=True, null=True)),
                ('gn_name', models.CharField(blank=True, max_length=100, null=True)),
                ('gns_id', models.IntegerField(blank=True, null=True)),
                ('gns_name', models.CharField(blank=True, max_length=100, null=True)),
                ('gn_level', models.IntegerField(blank=True, null=True)),
                ('gn_region', models.CharField(blank=True, max_length=100, null=True)),
                ('gn_a1_code', models.CharField(blank=True, max_length=100, null=True)),
                ('region_sub', models.CharField(blank=True, max_length=100, null=True)),
                ('sub_code', models.CharField(blank=True, max_length=100, null=True)),
                ('gns_level', models.IntegerField(blank=True, null=True)),
                ('gns_lang', models.CharField(blank=True, max_length=100, null=True)),
                ('gns_adm1', models.CharField(blank=True, max_length=100, null=True)),
                ('gns_region', models.CharField(blank=True, max_length=100, null=True)),
                ('polygon', models.TextField(blank=True, null=True)),
                ('geometry_type', models.CharField(blank=True, max_length=50, null=True)),
            ],
            options={
                'verbose_name_plural': 'admin1 regions',
            },
        ),
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('geoname_id', models.IntegerField(blank=True, null=True)),
                ('name', models.CharField(max_length=200)),
                ('location', django.contrib.gis.db.models.fields.PointField(blank=True, null=True, srid=4326)),
                ('ascii_name', models.CharField(blank=True, max_length=200, null=True)),
                ('alt_name', models.CharField(blank=True, max_length=200, null=True)),
                ('namepar', models.CharField(blank=True, max_length=200, null=True)),
            ],
            options={
                'verbose_name_plural': 'cities',
            },
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('code', models.CharField(max_length=2, primary_key=True, serialize=False)),
                ('numerical_code_un', models.IntegerField(blank=True, null=True)),
                ('name', models.CharField(db_index=True, max_length=100)),
                ('alt_name', models.CharField(blank=True, max_length=100, null=True)),
                ('language', models.CharField(max_length=2, null=True)),
                ('dac_country_code', models.IntegerField(blank=True, null=True)),
                ('iso3', models.CharField(blank=True, max_length=3, null=True)),
                ('alpha3', models.CharField(blank=True, max_length=3, null=True)),
                ('fips10', models.CharField(blank=True, max_length=2, null=True)),
                ('center_longlat', django.contrib.gis.db.models.fields.PointField(blank=True, null=True, srid=4326)),
                ('polygon', models.TextField(blank=True, null=True)),
                ('data_source', models.CharField(blank=True, max_length=20, null=True)),
                ('capital_city', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='capital_of', to='geodata.City')),
            ],
            options={
                'verbose_name_plural': 'countries',
            },
        ),
        migrations.CreateModel(
            name='Region',
            fields=[
                ('code', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=80)),
                ('center_longlat', django.contrib.gis.db.models.fields.PointField(blank=True, null=True, srid=4326)),
                ('parental_region', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='geodata.Region')),
            ],
        ),
        migrations.CreateModel(
            name='RegionVocabulary',
            fields=[
                ('code', models.CharField(max_length=40, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(default=b'')),
            ],
        ),
        migrations.AddField(
            model_name='region',
            name='region_vocabulary',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='geodata.RegionVocabulary'),
        ),
        migrations.AddField(
            model_name='country',
            name='region',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='geodata.Region'),
        ),
        migrations.AddField(
            model_name='country',
            name='un_region',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='un_countries', to='geodata.Region'),
        ),
        migrations.AddField(
            model_name='country',
            name='unesco_region',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='unesco_countries', to='geodata.Region'),
        ),
        migrations.AddField(
            model_name='city',
            name='country',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='geodata.Country'),
        ),
        migrations.AddField(
            model_name='adm1region',
            name='country',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='geodata.Country'),
        ),
    ]
