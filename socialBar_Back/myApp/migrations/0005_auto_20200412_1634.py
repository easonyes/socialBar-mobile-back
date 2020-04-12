# Generated by Django 2.2.11 on 2020-04-12 16:34

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myApp', '0004_auto_20200401_2314'),
    ]

    operations = [
        migrations.AlterField(
            model_name='certification',
            name='faceImg',
            field=models.FileField(blank=True, null=True, upload_to='img/faces', verbose_name='学生照片'),
        ),
        migrations.AlterField(
            model_name='certification',
            name='idCardImg1',
            field=models.FileField(blank=True, null=True, upload_to='img/idCardImg', verbose_name='身份证正面'),
        ),
        migrations.AlterField(
            model_name='certification',
            name='idCardImg2',
            field=models.FileField(blank=True, null=True, upload_to='img/idCardImg', verbose_name='身份证反面'),
        ),
        migrations.AlterField(
            model_name='chat',
            name='img',
            field=models.FileField(blank=True, null=True, upload_to='img/chat', verbose_name='消息图片'),
        ),
        migrations.AlterField(
            model_name='emailverifyrecord',
            name='send_time',
            field=models.DateTimeField(default=datetime.datetime(2020, 4, 12, 16, 34, 32, 493658), verbose_name='发送时间'),
        ),
        migrations.AlterField(
            model_name='student',
            name='avatar',
            field=models.FileField(blank=True, null=True, upload_to='img/avatars', verbose_name='用户头像'),
        ),
    ]