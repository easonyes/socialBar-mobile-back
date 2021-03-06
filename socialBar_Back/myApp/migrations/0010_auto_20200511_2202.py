# Generated by Django 3.0.5 on 2020-05-11 22:02

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myApp', '0009_auto_20200509_1349'),
    ]

    operations = [
        migrations.AddField(
            model_name='chat',
            name='unread',
            field=models.BooleanField(db_index=True, default=True, verbose_name='是否未读'),
        ),
        migrations.AlterField(
            model_name='comment',
            name='time',
            field=models.CharField(default='2020-05-11 22:02:54', max_length=50, verbose_name='评论时间'),
        ),
        migrations.AlterField(
            model_name='commentactive',
            name='time',
            field=models.CharField(default='2020-05-11 22:02:54', max_length=50, verbose_name='评论时间'),
        ),
        migrations.AlterField(
            model_name='emailverifyrecord',
            name='send_time',
            field=models.DateTimeField(default=datetime.datetime(2020, 5, 11, 22, 2, 54, 258937), verbose_name='发送时间'),
        ),
        migrations.AlterField(
            model_name='interactive',
            name='activeTime',
            field=models.CharField(default='2020-05-11 22:02:54', max_length=50, verbose_name='互动时间'),
        ),
        migrations.AlterField(
            model_name='post',
            name='createTime',
            field=models.CharField(default='2020-05-11 22:02:54', max_length=50, verbose_name='创建时间'),
        ),
    ]
