from django.db import models

# Create your models here.


class Student(models.Model):
    name = models.CharField(max_length=200)
    password = models.CharField(max_length=200)
    address = models.CharField(max_length=200, null=True)
    birthday = models.DateTimeField(null=True)
    nickname = models.CharField(max_length=200, null=True)
    gender = models.IntegerField(null=True)  # 1表示男性，2表示女性
    phone = models.CharField(max_length=200, null=True)
