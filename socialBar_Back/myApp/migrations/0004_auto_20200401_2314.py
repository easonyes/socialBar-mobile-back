# Generated by Django 2.2.11 on 2020-04-01 23:14

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('myApp', '0003_auto_20200312_2139'),
    ]

    operations = [
        migrations.CreateModel(
            name='Certification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('idCard', models.CharField(max_length=18, verbose_name='身份证号')),
                ('name', models.CharField(max_length=20, verbose_name='姓名')),
                ('fromPlace', models.SmallIntegerField(help_text='以市为单位', verbose_name='生源地')),
                ('specialist', models.SmallIntegerField(null=True, verbose_name='专科大学')),
                ('undergraduate', models.SmallIntegerField(null=True, verbose_name='本科大学')),
                ('master', models.SmallIntegerField(null=True, verbose_name='硕士大学')),
                ('doctor', models.SmallIntegerField(null=True, verbose_name='博士大学')),
                ('studentCard', models.SmallIntegerField(null=True, verbose_name='学生证号')),
                ('faceImg', models.ImageField(blank=True, null=True, upload_to='img/faces', verbose_name='学生照片')),
                ('idCardImg1', models.ImageField(blank=True, null=True, upload_to='img/idCardImg', verbose_name='身份证正面')),
                ('idCardImg2', models.ImageField(blank=True, null=True, upload_to='img/idCardImg', verbose_name='身份证反面')),
                ('city', models.SmallIntegerField(verbose_name='当前城市')),
                ('school', models.SmallIntegerField(verbose_name='当前学校')),
            ],
        ),
        migrations.CreateModel(
            name='Site',
            fields=[
                ('id', models.SmallIntegerField(primary_key=True, serialize=False, verbose_name='站点id')),
                ('siteName', models.SmallIntegerField(verbose_name='站点名称')),
            ],
        ),
        migrations.RemoveField(
            model_name='emailverifyrecord',
            name='send_type',
        ),
        migrations.AddField(
            model_name='student',
            name='avatar',
            field=models.ImageField(blank=True, null=True, upload_to='img/avatars', verbose_name='用户头像'),
        ),
        migrations.AddField(
            model_name='student',
            name='currentSchool',
            field=models.CharField(max_length=20, null=True, verbose_name='当前学校名称'),
        ),
        migrations.AddField(
            model_name='student',
            name='defaultSite',
            field=models.SmallIntegerField(null=True, verbose_name='默认站点'),
        ),
        migrations.AddField(
            model_name='student',
            name='fansList',
            field=models.TextField(null=True, verbose_name='粉丝列表'),
        ),
        migrations.AddField(
            model_name='student',
            name='siteList',
            field=models.CharField(help_text='表示当前用户的可用站点', max_length=200, null=True, verbose_name='站点'),
        ),
        migrations.AddField(
            model_name='student',
            name='starList',
            field=models.TextField(null=True, verbose_name='关注列表'),
        ),
        migrations.AddField(
            model_name='student',
            name='status',
            field=models.SmallIntegerField(choices=[(1, '可用'), (2, '锁定'), (0, '注销')], default=1, verbose_name='用户状态'),
        ),
        migrations.AlterField(
            model_name='emailverifyrecord',
            name='send_time',
            field=models.DateTimeField(default=datetime.datetime(2020, 4, 1, 23, 14, 26, 996408), verbose_name='发送时间'),
        ),
        migrations.AlterField(
            model_name='student',
            name='address',
            field=models.CharField(max_length=200, null=True, verbose_name='地址'),
        ),
        migrations.AlterField(
            model_name='student',
            name='birthday',
            field=models.DateTimeField(null=True, verbose_name='生日'),
        ),
        migrations.AlterField(
            model_name='student',
            name='email',
            field=models.EmailField(max_length=50, verbose_name='邮箱'),
        ),
        migrations.AlterField(
            model_name='student',
            name='gender',
            field=models.IntegerField(help_text='1表示男性，2表示女性', null=True, verbose_name='性别'),
        ),
        migrations.AlterField(
            model_name='student',
            name='name',
            field=models.CharField(max_length=200, null=True, verbose_name='登录名'),
        ),
        migrations.AlterField(
            model_name='student',
            name='nickname',
            field=models.CharField(max_length=200, null=True, verbose_name='昵称'),
        ),
        migrations.AlterField(
            model_name='student',
            name='password',
            field=models.CharField(max_length=200, verbose_name='密码'),
        ),
        migrations.AlterField(
            model_name='student',
            name='phone',
            field=models.CharField(max_length=200, null=True, verbose_name='电话'),
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('userName', models.CharField(max_length=200, verbose_name='用户昵称')),
                ('createTime', models.DateField(verbose_name='创建时间')),
                ('createPlace', models.CharField(max_length=50, verbose_name='创建地点')),
                ('introduction', models.CharField(max_length=50, verbose_name='简介')),
                ('content', models.TextField(verbose_name='内容')),
                ('tags', models.CharField(max_length=200, verbose_name='标签')),
                ('likes', models.IntegerField(verbose_name='点赞数')),
                ('comments', models.IntegerField(verbose_name='评论数')),
                ('forwards', models.IntegerField(verbose_name='转发数')),
                ('imgs', models.TextField(verbose_name='图片')),
                ('userId', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myApp.Student', verbose_name='学生id')),
            ],
        ),
        migrations.CreateModel(
            name='Interactive',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.SmallIntegerField(choices=[(1, '点赞'), (2, '收藏'), (3, '转发')], verbose_name='互动类型')),
                ('activeTime', models.DateField(verbose_name='互动时间')),
                ('postId', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myApp.Post', verbose_name='动态id')),
                ('userId', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myApp.Student', verbose_name='学生id')),
            ],
        ),
        migrations.CreateModel(
            name='History',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('viewTime', models.DateField(verbose_name='浏览时间')),
                ('postId', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myApp.Post', verbose_name='动态id')),
                ('userId', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myApp.Student', verbose_name='学生id')),
            ],
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField(verbose_name='评论内容')),
                ('time', models.DateField(verbose_name='评论时间')),
                ('active', models.SmallIntegerField(choices=[(1, '生效'), (0, '失效')], verbose_name='生效')),
                ('toComment', models.IntegerField(null=True, verbose_name='评论id')),
                ('formUser', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fromUser', to='myApp.Student', verbose_name='评论用户id')),
                ('postId', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myApp.Post', verbose_name='评论动态id')),
                ('toUser', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='toUser', to='myApp.Student', verbose_name='回复用户id')),
            ],
        ),
        migrations.CreateModel(
            name='Chat',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.CharField(max_length=2000, null=True, verbose_name='文本内容')),
                ('type', models.SmallIntegerField(choices=[(1, '文本'), (2, '图片'), (3, '文件')], verbose_name='消息类型')),
                ('img', models.ImageField(blank=True, null=True, upload_to='img/chat', verbose_name='消息图片')),
                ('file', models.FileField(null=True, upload_to='file/chat', verbose_name='消息文件')),
                ('fromStudent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fromStudent', to='myApp.Student', verbose_name='发送学生id')),
                ('toStudent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='toStudent', to='myApp.Student', verbose_name='接收学生id')),
            ],
        ),
    ]
