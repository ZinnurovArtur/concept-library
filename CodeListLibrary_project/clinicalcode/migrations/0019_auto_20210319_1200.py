# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2021-03-19 12:00


import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clinicalcode', '0018_bnf_codes_med_codes_prod_codes_snomed_codes_ukbiobank_codes'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalphenotype',
            name='clinical_terminologies',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(), blank=True, null=True, size=None),
        ),
        migrations.AddField(
            model_name='historicalphenotype',
            name='publications',
            field=models.CharField(blank=True, max_length=3000, null=True),
        ),
        migrations.AddField(
            model_name='phenotype',
            name='clinical_terminologies',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(), blank=True, null=True, size=None),
        ),
        migrations.AddField(
            model_name='phenotype',
            name='publications',
            field=models.CharField(blank=True, max_length=3000, null=True),
        ),
    ]
