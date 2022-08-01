# Generated by Django 2.2.24 on 2022-08-01 18:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clinicalcode', '0062_auto_20220601_1824'),
    ]

    operations = [
        migrations.AlterField(
            model_name='concept',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='concept',
            name='secondary_publication_links',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='concept',
            name='validation_description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='historicalconcept',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='historicalconcept',
            name='secondary_publication_links',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='historicalconcept',
            name='validation_description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='historicalphenotype',
            name='secondary_publication_links',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='historicalphenotype',
            name='validation',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='phenotype',
            name='secondary_publication_links',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='phenotype',
            name='validation',
            field=models.TextField(blank=True, null=True),
        ),
    ]
