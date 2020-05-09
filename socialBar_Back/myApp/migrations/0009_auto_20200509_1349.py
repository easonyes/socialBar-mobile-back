# Generated by Django 3.0.5 on 2020-05-09 13:49

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myApp', '0008_auto_20200508_2136'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='time',
            field=models.CharField(default='2020-05-09 13:49:10', max_length=50, verbose_name='评论时间'),
        ),
        migrations.AlterField(
            model_name='commentactive',
            name='time',
            field=models.CharField(default='2020-05-09 13:49:10', max_length=50, verbose_name='评论时间'),
        ),
        migrations.AlterField(
            model_name='emailverifyrecord',
            name='send_time',
            field=models.DateTimeField(default=datetime.datetime(2020, 5, 9, 13, 49, 10, 101079), verbose_name='发送时间'),
        ),
        migrations.AlterField(
            model_name='interactive',
            name='activeTime',
            field=models.CharField(default='2020-05-09 13:49:10', max_length=50, verbose_name='互动时间'),
        ),
        migrations.AlterField(
            model_name='post',
            name='createTime',
            field=models.CharField(default='2020-05-09 13:49:10', max_length=50, verbose_name='创建时间'),
        ),
        migrations.AlterField(
            model_name='student',
            name='fansList',
            field=models.TextField(default=[], verbose_name='粉丝列表'),
        ),
        migrations.AlterField(
            model_name='student',
            name='starList',
            field=models.TextField(default=[], verbose_name='关注列表'),
        ),
    ]
