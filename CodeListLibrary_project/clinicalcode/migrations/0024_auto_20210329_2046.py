# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2021-03-29 19:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clinicalcode',
         '0023_historicalphenotypecomponent_phenotypecomponent'),
    ]

    operations = [
        migrations.RenameField(
            model_name='historicalphenotype',
            old_name='phenotype_id',
            new_name='phenotype_uuid',
        ),
        migrations.RenameField(
            model_name='phenotype',
            old_name='phenotype_id',
            new_name='phenotype_uuid',
        ),
    ]
