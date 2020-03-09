from django.http import HttpResponse
from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User, Group
from rest_framework import viewsets
import json
from rest_framework.response import Response
from myApp.serializers import UserSerializer, GroupSerializer
from .models import *
from django.views.decorators.csrf import csrf_exempt


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
        name = reqBody.get('name')
        pwd = reqBody.get('password')
        print(name)
        try:
            student = Student.objects.filter(name=name)
            if name and pwd and not student:
                u = Student(name=name,
                            password=pwd)
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
