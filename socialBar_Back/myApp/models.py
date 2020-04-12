from django.db import models
from datetime import datetime

# Create your models here.


class Student(models.Model):
    email = models.EmailField(max_length=50, verbose_name="邮箱")
    password = models.CharField(max_length=200, verbose_name="密码")
    name = models.CharField(max_length=200, null=True, verbose_name="登录名")
    address = models.CharField(max_length=200, null=True, verbose_name="地址")
    birthday = models.DateTimeField(null=True, verbose_name="生日")
    nickname = models.CharField(max_length=200, null=True, verbose_name="昵称")
    gender = models.IntegerField(null=True, help_text="1表示男性，2表示女性", verbose_name="性别")
    phone = models.CharField(max_length=200, null=True, verbose_name="电话")
    siteList = models.CharField(max_length=200, null=True, verbose_name="站点", help_text="表示当前用户的可用站点")
    status = models.SmallIntegerField(verbose_name="用户状态", choices=(
        (1, "可用"),
        (2, "锁定"),
        (0, "注销")
    ), default=1)
    currentSchool = models.CharField(max_length=20, null=True, verbose_name="当前学校名称")
    defaultSite = models.SmallIntegerField(verbose_name="默认站点", null=True)
    starList = models.TextField(verbose_name="关注列表", null=True)
    fansList = models.TextField(verbose_name="粉丝列表", null=True)
    avatar = models.FileField(verbose_name="用户头像", upload_to="img/avatars", blank=True, null=True)


# 邮箱验证
class EmailVerifyRecord(models.Model):
    # 验证码
    code = models.CharField(max_length=20, verbose_name="验证码")
    email = models.EmailField(max_length=50, verbose_name="邮箱")
    send_time = models.DateTimeField(verbose_name="发送时间", default=datetime.now())

    class Meta:
        verbose_name = u"邮箱验证码"
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return '{0}({1})'.format(self.code, self.email)


class Certification(models.Model):
    idCard = models.CharField(verbose_name="身份证号", max_length=18)
    name = models.CharField(verbose_name="姓名", max_length=20)
    fromPlace = models.SmallIntegerField(verbose_name="生源地", help_text="以市为单位")
    specialist = models.SmallIntegerField(verbose_name="专科大学", null=True)
    undergraduate = models.SmallIntegerField(verbose_name="本科大学", null=True)
    master = models.SmallIntegerField(verbose_name="硕士大学", null=True)
    doctor = models.SmallIntegerField(verbose_name="博士大学", null=True)
    studentCard = models.SmallIntegerField(verbose_name="学生证号", null=True)
    faceImg = models.FileField(verbose_name="学生照片", upload_to="img/faces", blank=True, null=True)
    idCardImg1 = models.FileField(verbose_name="身份证正面", upload_to="img/idCardImg", blank=True, null=True)
    idCardImg2 = models.FileField(verbose_name="身份证反面", upload_to="img/idCardImg", blank=True, null=True)
    city = models.SmallIntegerField(verbose_name="当前城市")
    school = models.SmallIntegerField(verbose_name="当前学校")


class Site(models.Model):
    id = models.SmallIntegerField(verbose_name="站点id", primary_key=True)
    siteName = models.SmallIntegerField(verbose_name="站点名称")


class Post(models.Model):
    userId = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name="学生id")
    userName = models.CharField(max_length=200, verbose_name="用户昵称")
    createTime = models.DateField(verbose_name="创建时间")
    createPlace = models.CharField(verbose_name="创建地点", max_length=50)
    introduction = models.CharField(verbose_name="简介", max_length=50)
    content = models.TextField(verbose_name="内容")
    tags = models.CharField(verbose_name="标签", max_length=200)
    likes = models.IntegerField(verbose_name="点赞数")
    comments = models.IntegerField(verbose_name="评论数")
    forwards = models.IntegerField(verbose_name="转发数")
    imgs = models.TextField(verbose_name="图片")


class History(models.Model):
    userId = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name="学生id")
    postId = models.ForeignKey(Post, on_delete=models.CASCADE, verbose_name="动态id")
    viewTime = models.DateField(verbose_name="浏览时间")


class Interactive(models.Model):
    userId = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name="学生id")
    postId = models.ForeignKey(Post, on_delete=models.CASCADE, verbose_name="动态id")
    type = models.SmallIntegerField(verbose_name="互动类型", choices=(
        (1, "点赞"),
        (2, "收藏"),
        (3, "转发")
    ))
    activeTime = models.DateField(verbose_name="互动时间")


class Comment(models.Model):
    formUser = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name="评论用户id", related_name="fromUser")
    toUser = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name="回复用户id", null=True, related_name="toUser")
    postId = models.ForeignKey(Post, on_delete=models.CASCADE, verbose_name="评论动态id")
    content = models.TextField(verbose_name="评论内容")
    time = models.DateField(verbose_name="评论时间")
    active = models.SmallIntegerField(verbose_name="生效", choices=(
        (1, "生效"),
        (0, "失效")
    ))
    toComment = models.IntegerField(verbose_name="评论id", null=True)


class Chat(models.Model):
    fromStudent = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name="发送学生id", related_name="fromStudent")
    toStudent = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name="接收学生id", related_name="toStudent")
    content = models.CharField(max_length=2000, verbose_name="文本内容", null=True)
    type = models.SmallIntegerField(choices=(
        (1, "文本"),
        (2, "图片"),
        (3, "文件")
    ), verbose_name="消息类型")
    img = models.FileField(upload_to="img/chat", blank=True, null=True, verbose_name="消息图片")
    file = models.FileField(upload_to="file/chat", null=True, verbose_name="消息文件")

