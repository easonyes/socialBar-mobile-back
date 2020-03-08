from django.http import HttpResponse
from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User, Group
from rest_framework import viewsets
import json
from rest_framework.response import Response
from myApp.serializers import UserSerializer, GroupSerializer
from .models import *


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


def login(request):
    context = {
        'log_status': 0,
        'user_id': -1
    }
    # request.META["CSRF_COOKIE_USED"] = True
    reqUsername = request.data['username']
    reqPassword = request.data['password']
    try:
        student = Student.objects.filter(name=reqUsername, password=reqPassword)
        if student is not None:
            request.session['IS_LOGIN'] = True
            request.session['USER_Id'] = student[0].id
            context['log_status'] = 1
            context['user_id'] = student[0].id
            return Response({"code": 200, "result": "登录成功"})
        else:
            return Response({"code": 403, "result": "密码错误"})
    except ObjectDoesNotExist:
        return Response({"code": 404, "result": "账号不存在"})


# # done
# def login(request):
#     context = {
#         'log_status': 0,
#         'user_id': -1
#     }
#
#     if request.method == 'POST':
#         name = request.POST.get('name')
#         password = request.POST.get('password')
#         print(name, password)
#         user = Student.objects.filter(name=name, password=password)
#         if user:
#             request.session['IS_LOGIN'] = True
#             request.session['USER_Id'] = user[0].id
#             context['log_status'] = 1
#             context['user_id'] = user[0].id
#             return HttpResponse(json.dumps(context), content_type="application/json")
#         else:
#             return HttpResponse(json.dumps(context), content_type="application/json")


# done
def register(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        pwd = request.POST.get('password')
        address = request.POST.get('address')
        birthday = request.POST.get('birthday')
        nickname = request.POST.get('nickname')
        gender = request.POST.get('gender')
        phone = request.POST.get('phone')
        try:
            student = Student.objects.filter(name=name, password=pwd)
            context = {'re_true': 'false', 'code': 403, 'result': ''}
            if name and pwd and not student:
                u = Student(name=name,
                            password=pwd,
                            address=address,
                            birthday=birthday,
                            nickname=nickname,
                            gender=gender,
                            phone=phone)
                u.save()
                context['re_true'] = 'true'
                context['code'] = 200
                context['result'] = '注册成功'
                return HttpResponse(json.dumps(context), content_type="application/json")
            else:
                context['re_true'] = 'false'
                context['code'] = 403
                context['result'] = '用户名已被注册'
                return HttpResponse(json.dumps(context), content_type="application/json")
        except ObjectDoesNotExist:
            context['re_true'] = 'false'
            context['code'] = 404
            context['result'] = '错误'
            return HttpResponse(json.dumps(context), content_type="application/json")
