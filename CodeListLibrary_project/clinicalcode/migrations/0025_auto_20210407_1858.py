# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2021-04-07 17:58


from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clinicalcode', '0024_auto_20210329_2046'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='historicalphenotypecomponent',
            name='created_by',
        ),
        migrations.RemoveField(
            model_name='historicalphenotypecomponent',
            name='history_user',
        ),
        migrations.RemoveField(
            model_name='historicalphenotypecomponent',
            name='modified_by',
        ),
        migrations.RemoveField(
            model_name='historicalphenotypecomponent',
            name='phenotype',
        ),
        migrations.RemoveField(
            model_name='phenotypecomponent',
            name='created_by',
        ),
        migrations.RemoveField(
            model_name='phenotypecomponent',
            name='modified_by',
        ),
        migrations.RemoveField(
            model_name='phenotypecomponent',
            name='phenotype',
        ),
        migrations.DeleteModel(
            name='HistoricalPhenotypeComponent',
        ),
        migrations.DeleteModel(
            name='PhenotypeComponent',
        ),
    ]
