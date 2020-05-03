# Generated by Django 3.0.5 on 2020-05-01 00:35

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myApp', '0013_auto_20200430_2304'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='chatList',
            field=models.CharField(max_length=200, null=True, verbose_name='聊天列表'),
        ),
        migrations.AlterField(
            model_name='emailverifyrecord',
            name='send_time',
            field=models.DateTimeField(default=datetime.datetime(2020, 5, 1, 0, 35, 46, 162700), verbose_name='发送时间'),
        ),
    ]
