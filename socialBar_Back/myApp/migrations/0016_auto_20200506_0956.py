# Generated by Django 3.0.5 on 2020-05-06 09:56

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myApp', '0015_auto_20200503_1416'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='site',
            field=models.IntegerField(default=1, verbose_name='发布站点'),
        ),
        migrations.AlterField(
            model_name='emailverifyrecord',
            name='send_time',
            field=models.DateTimeField(default=datetime.datetime(2020, 5, 6, 9, 56, 37, 880546), verbose_name='发送时间'),
        ),
        migrations.AlterField(
            model_name='post',
            name='createTime',
            field=models.DateField(default=datetime.datetime(2020, 5, 6, 9, 56, 37, 882543), verbose_name='创建时间'),
        ),
    ]
