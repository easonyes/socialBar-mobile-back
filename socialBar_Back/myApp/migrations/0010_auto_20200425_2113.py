# Generated by Django 3.0.5 on 2020-04-25 21:13

import datetime
import django.core.validators
from django.db import migrations, models
import re


class Migration(migrations.Migration):

    dependencies = [
        ('myApp', '0009_auto_20200414_2145'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailverifyrecord',
            name='send_time',
            field=models.DateTimeField(default=datetime.datetime(2020, 4, 25, 21, 13, 10, 314300), verbose_name='发送时间'),
        ),
        migrations.AlterField(
            model_name='student',
            name='avatar',
            field=models.FileField(default='/media/img/avatars/default.jpg', upload_to='img/avatars', verbose_name='用户头像'),
        ),
        migrations.AlterField(
            model_name='student',
            name='defaultSite',
            field=models.SmallIntegerField(default=1, verbose_name='默认站点'),
        ),
        migrations.AlterField(
            model_name='student',
            name='siteList',
            field=models.CharField(default='1', help_text='表示当前用户的可用站点', max_length=200, validators=[django.core.validators.RegexValidator(re.compile('^\\d+(?:,\\d+)*\\Z'), code='invalid', message='Enter only digits separated by commas.')], verbose_name='站点'),
        ),
    ]
