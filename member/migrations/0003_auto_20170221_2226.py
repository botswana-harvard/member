# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-02-21 20:26
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('member', '0002_auto_20170211_1639'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='enrollmentchecklistanonymous',
            name='citizen',
        ),
        migrations.RemoveField(
            model_name='enrollmentchecklistanonymous',
            name='study_participation',
        ),
        migrations.RemoveField(
            model_name='historicalenrollmentchecklistanonymous',
            name='citizen',
        ),
        migrations.RemoveField(
            model_name='historicalenrollmentchecklistanonymous',
            name='study_participation',
        ),
    ]