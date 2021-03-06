# Generated by Django 3.0.5 on 2020-05-15 00:03

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myApp', '0011_auto_20200512_1948'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='unReadPost',
            field=models.IntegerField(default=0, verbose_name='未读动态'),
        ),
        migrations.AlterField(
            model_name='comment',
            name='time',
            field=models.CharField(default='2020-05-15 00:03:04', max_length=50, verbose_name='评论时间'),
        ),
        migrations.AlterField(
            model_name='commentactive',
            name='time',
            field=models.CharField(default='2020-05-15 00:03:04', max_length=50, verbose_name='评论时间'),
        ),
        migrations.AlterField(
            model_name='emailverifyrecord',
            name='send_time',
            field=models.DateTimeField(default=datetime.datetime(2020, 5, 15, 0, 3, 4, 700819), verbose_name='发送时间'),
        ),
        migrations.AlterField(
            model_name='interactive',
            name='activeTime',
            field=models.CharField(default='2020-05-15 00:03:04', max_length=50, verbose_name='互动时间'),
        ),
        migrations.AlterField(
            model_name='post',
            name='createTime',
            field=models.CharField(default='2020-05-15 00:03:04', max_length=50, verbose_name='创建时间'),
        ),
    ]
