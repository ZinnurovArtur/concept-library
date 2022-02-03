# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2021-04-09 13:54


import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clinicalcode', '0025_auto_20210407_1858'),
    ]

    operations = [
        migrations.AddField(
            model_name='concept',
            name='code_attribute_header',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=100), blank=True, null=True, size=None),
        ),
        migrations.AddField(
            model_name='historicalconcept',
            name='code_attribute_header',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=100), blank=True, null=True, size=None),
        ),
    ]
