# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2021-08-06 13:48
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('clinicalcode', '0033_auto_20210806_1431'),
    ]

    operations = [
        migrations.AlterField(
            model_name='datasource',
            name='brand',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='data_source_brand', to='clinicalcode.Brand'),
        ),
        migrations.AlterField(
            model_name='datasource',
            name='description',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='datasource',
            name='uid',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AlterField(
            model_name='datasource',
            name='url',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='historicaldatasource',
            name='description',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='historicaldatasource',
            name='uid',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AlterField(
            model_name='historicaldatasource',
            name='url',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]
