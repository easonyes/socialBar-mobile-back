from django.http import HttpResponse
from django.shortcuts import render
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User, Group
from rest_framework import viewsets
import json
from datetime import datetime
from rest_framework.response import Response
from myApp.serializers import UserSerializer, GroupSerializer
from .models import *
from django.views.decorators.csrf import csrf_exempt
from .email_util import *


# Create your views here.

#
# def index(request):
#     return HttpResponse("Hello world.")


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


@csrf_exempt
def login(request):
    context = {
        'code': 403,
        'log_status': 0,
        'user_id': -1,
        'success': False,
        'result': '登录请求失败'
    }
    print(request.POST)
    if request.method == 'POST':
        # request.META["CSRF_COOKIE_USED"] = True
        reqBody = eval(request.body.decode())
        reqUsername = reqBody.get('name')
        reqPassword = reqBody.get('password')
        try:
            student = Student.objects.filter(name=reqUsername, password=reqPassword)
            if len(student) != 0:
                request.session['IS_LOGIN'] = True
                request.session['USER_Id'] = student[0].id
                context['code'] = 200
                context['log_status'] = 1
                context['user_id'] = student[0].id
                context['success'] = True
                context['result'] = '登录成功'
                return HttpResponse(json.dumps(context), content_type="application/json")
            else:
                context['code'] = 403
                context['result'] = '用户名或密码错误'
                return HttpResponse(json.dumps(context), content_type="application/json")
        except ObjectDoesNotExist:
            context['code'] = 404
            context['result'] = '账号不存在'
            return HttpResponse(json.dumps(context), content_type="application/json")
    else:
        context = {
            'code': 405,
            'log_status': 0,
            'user_id': -1,
            'success': False,
            'result': '请使用POST请求'
        }
        return HttpResponse(json.dumps(context), content_type="application/json")


@csrf_exempt
def register(request):
    context = {'success': False, 'code': 403, 'result': ''}
    if request.method == 'POST':
        reqBody = eval(request.body.decode())
        email = reqBody.get('email')
        code = reqBody.get('code')
        try:
            student = Student.objects.filter(email=email)
            if email and not student:
                mObj = EmailVerifyRecord.objects.filter(email=email).order_by('-id').first()
                # conx = serializers.serialize("json", mObj)
                print(mObj.id)
                print(mObj.send_time)
                tCode = mObj.code
                sec = (datetime.datetime.now() - mObj.send_time).seconds
                if sec > 120:
                    context['success'] = False
                    context['code'] = 201
                    context['result'] = '验证码时间超时，请重新获取'
                    return HttpResponse(json.dumps(context), content_type="application/json")
                else:
                    if code != tCode:
                        context['success'] = False
                        context['code'] = 202
                        context['result'] = '验证码错误，请重新输入'
                        return HttpResponse(json.dumps(context), content_type="application/json")
                    # context['obj'] = mObj
                    u = Student(email=email)
                    u.save()
                    context['success'] = True
                    context['code'] = 200
                    context['result'] = '注册成功'
                    return HttpResponse(json.dumps(context), content_type="application/json")
            else:
                context['success'] = False
                context['code'] = 403
                context['result'] = '用户名已被注册'
                return HttpResponse(json.dumps(context), content_type="application/json")
        except ObjectDoesNotExist:
            context['success'] = False
            context['code'] = 404
            context['result'] = '错误'
            return HttpResponse(json.dumps(context), content_type="application/json")
    else:
        context['success'] = False
        context['code'] = 405
        context['result'] = '必须使用POST请求'
        return HttpResponse(json.dumps(context), content_type="application/json")


# 注册发送邮箱验证码
def sendEmailRegisterCodeView(request):
    if request.method == 'POST':
        context = {
            'code': "200", 'email': "", 'error_email': '', 'success': True
        }
        # print(eval(request.body.decode()))
        print(request.body)
        try:
            reqBody = eval(request.body.decode())
            print(reqBody)
            email = reqBody.get('email')
            context['email'] = email
            user_obj = Student.objects.filter(email=email).first()
            if user_obj:
                context['code'] = "111"
                context['error_email'] = "用户已存在"
                context['success'] = False
                return HttpResponse(json.dumps(context), content_type="application/json")
            else:
                # 发送邮箱
                res_email = send_code_email(email)
                if res_email:
                    # 注册用户信息，设置登陆状态为False
                    # create_last_user = Student.objects.update_or_create(email=email)
                    # if not create_last_user:
                    #     context['code'] = "201"
                    #     context['error_email'] = "注册错误，请重试"
                    #     context['success'] = False
                    #     return HttpResponse(json.dumps(context), content_type="application/json")
                    return HttpResponse(json.dumps(context), content_type="application/json")
                else:
                    context['code'] = "202"
                    context['error_email'] = "验证码发送失败, 请稍后重试"
                    context['success'] = False
                    return HttpResponse(json.dumps(context), content_type="application/json")
        except Exception as e:
            print("错误信息 : ", e)
            context['code'] = "404"
            context['error_email'] = "接口错误, 请稍后重试"
            context['success'] = False
        return HttpResponse(json.dumps(context), content_type="application/json")
