from django.db import models
from datetime import datetime

# Create your models here.


class Student(models.Model):
    password = models.CharField(max_length=200)
    email = models.EmailField(max_length=50, verbose_name="邮箱", default="123456@qq.com")
    name = models.CharField(max_length=200, null=True)
    address = models.CharField(max_length=200, null=True)
    birthday = models.DateTimeField(null=True)
    nickname = models.CharField(max_length=200, null=True)
    gender = models.IntegerField(null=True)  # 1表示男性，2表示女性
    phone = models.CharField(max_length=200, null=True)


# 邮箱验证
class EmailVerifyRecord(models.Model):
    # 验证码
    code = models.CharField(max_length=20, verbose_name="验证码")
    email = models.EmailField(max_length=50, verbose_name="邮箱")
    # 包含注册验证和找回验证
    send_type = models.CharField(verbose_name="验证码类型", max_length=10,
                                 choices=(("register", "注册"), ("forget", "找回密码")))
    send_time = models.DateTimeField(verbose_name="发送时间", default=datetime.now())

    class Meta:
        verbose_name = u"邮箱验证码"
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return '{0}({1})'.format(self.code, self.email)