# -*- coding: utf-8 -*-
# Generated by Django 1.9a1 on 2016-04-25 03:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spc', '0002_auto_20160425_1032'),
    ]

    operations = [
        migrations.AlterField(
            model_name='performingdetail',
            name='datetime',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='performingtracking',
            name='datetime',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
