# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2021-09-27 15:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clinicalcode', '0042_auto_20210920_1501'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalphenotype',
            name='implementation',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='phenotype',
            name='implementation',
            field=models.TextField(blank=True, null=True),
        ),
    ]
