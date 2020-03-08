from django.db import models

# Create your models here.


class Student(models.Model):
    name = models.CharField(max_length=200)
    password = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    birthday = models.DateTimeField()
    nickname = models.CharField(max_length=200)
    gender = models.IntegerField()  # 1表示男性，2表示女性
    phone = models.CharField(max_length=200)
