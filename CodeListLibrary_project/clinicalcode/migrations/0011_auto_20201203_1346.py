# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2020-12-03 13:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clinicalcode', '0010_auto_20201203_1322'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalphenotype',
            name='validation_performed',
            field=models.NullBooleanField(),
        ),
        migrations.AddField(
            model_name='phenotype',
            name='validation_performed',
            field=models.NullBooleanField(),
        ),
    ]
