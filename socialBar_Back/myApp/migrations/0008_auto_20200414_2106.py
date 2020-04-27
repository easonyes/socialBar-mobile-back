# Generated by Django 2.2.11 on 2020-04-14 21:06

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myApp', '0007_auto_20200414_2057'),
    ]

    operations = [
        migrations.AddField(
            model_name='certification',
            name='email',
            field=models.CharField(default='com', max_length=200, verbose_name='学生邮箱'),
        ),
        migrations.AlterField(
            model_name='emailverifyrecord',
            name='send_time',
            field=models.DateTimeField(default=datetime.datetime(2020, 4, 14, 21, 6, 38, 711239), verbose_name='发送时间'),
        ),
    ]