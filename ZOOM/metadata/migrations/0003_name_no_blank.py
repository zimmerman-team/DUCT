# Generated by Django 2.1.2 on 2018-11-08 22:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('metadata', '0002_file_file_heading_list'),
    ]

    operations = [
        migrations.AlterField(
            model_name='filesource',
            name='name',
            field=models.CharField(max_length=100, unique=True),
        ),
    ]
