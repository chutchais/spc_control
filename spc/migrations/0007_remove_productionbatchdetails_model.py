# -*- coding: utf-8 -*-
# Generated by Django 1.9a1 on 2016-04-25 04:42
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('spc', '0006_auto_20160425_1047'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='productionbatchdetails',
            name='model',
        ),
    ]
