# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2021-03-23 14:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clinicalcode', '0019_auto_20210319_1200'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='historicalphenotype',
            name='valid_event_data_range_end',
        ),
        migrations.RemoveField(
            model_name='historicalphenotype',
            name='valid_event_data_range_start',
        ),
        migrations.RemoveField(
            model_name='phenotype',
            name='valid_event_data_range_end',
        ),
        migrations.RemoveField(
            model_name='phenotype',
            name='valid_event_data_range_start',
        ),
        migrations.AddField(
            model_name='historicalphenotype',
            name='valid_event_data_range',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AddField(
            model_name='phenotype',
            name='valid_event_data_range',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AlterField(
            model_name='historicalphenotype',
            name='hdr_created_date',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='historicalphenotype',
            name='hdr_modified_date',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='phenotype',
            name='hdr_created_date',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='phenotype',
            name='hdr_modified_date',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
