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
import base64
from django.core.files.base import ContentFile


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
        'result': '登录请求失败',
        'studentInfo': None
    }
    print(request.POST)
    if request.method == 'POST':
        sId = request.get_signed_cookie('login_id', default=None, salt='id')
        print(sId)
        if sId:
            students = Student.objects.filter(id=sId)
            student = students.first()
            context['log_status'] = 1
            context['code'] = 200
            context['user_id'] = student.id
            context['success'] = True
            context['result'] = '使用cookie自动登录成功'
            # print(student)
            # print(type(student))
            context['studentInfo'] = serializers.serialize('json', students)
            response = HttpResponse(json.dumps(context), content_type="application/json")
            response.set_signed_cookie('login_id', student.id, salt="id", max_age=60 * 60 * 24 * 7)
            return response
        # request.META["CSRF_COOKIE_USED"] = True
        reqBody = eval(request.body.decode())
        reqUsername = reqBody.get('email')
        reqPassword = reqBody.get('password')
        try:
            students = Student.objects.filter(email=reqUsername)
            student = Student.objects.filter(email=reqUsername).first()
            if student:
                if student.password == reqPassword:
                    request.session['IS_LOGIN'] = True
                    request.session['USER_Id'] = student.id
                    context['code'] = 200
                    context['log_status'] = 1
                    context['user_id'] = student.id
                    context['success'] = True
                    context['result'] = '登录成功'
                    context['studentInfo'] = serializers.serialize('json', students)
                    response = HttpResponse(json.dumps(context), content_type="application/json")
                    response.set_signed_cookie('login_id', student.id, salt="id", max_age=60*60*24*7)
                    return response
                elif student.password == "123":
                    context['code'] = 201
                    context['result'] = '该账号密码尚未设置，请使用验证码登录并前往个人界面设置密码'
                    context['success'] = False
                    return HttpResponse(json.dumps(context), content_type="application/json")
                else:
                    context['code'] = 201
                    context['result'] = '密码错误'
                    context['success'] = False
                    return HttpResponse(json.dumps(context), content_type="application/json")
            else:
                context['code'] = 202
                context['result'] = '用户不存在'
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
def emailValidate(request):
    context = {'success': False, 'code': 403, 'result': ''}
    if request.method == 'POST':
        reqBody = eval(request.body.decode())
        email = reqBody.get('email')
        code = reqBody.get('code')
        # 获取验证码类型，1代表注册，2代表忘记密码，3代表登录
        eType = reqBody.get('type')
        try:
            student = Student.objects.filter(email=email)
            if eType == "1":
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
                        # u = Student(email=email)
                        # u.save()
                        context['success'] = True
                        context['code'] = 200
                        context['result'] = '验证成功'
                        return HttpResponse(json.dumps(context), content_type="application/json")
                else:
                    context['success'] = False
                    context['code'] = 203
                    context['result'] = '邮箱已被注册'
                    return HttpResponse(json.dumps(context), content_type="application/json")
            elif eType == "2" or eType == "3":
                mObj = EmailVerifyRecord.objects.filter(email=email).order_by('-id').first()
                if not mObj:
                    context['success'] = False
                    context['code'] = 210
                    context['result'] = '请先获取验证码！'
                    return HttpResponse(json.dumps(context), content_type="application/json")
                tCode = mObj.code
                sec = (datetime.datetime.now() - mObj.send_time).seconds
                if sec > 120:
                    context['success'] = False
                    context['code'] = 205
                    context['result'] = '验证码时间超时，请重新获取'
                    return HttpResponse(json.dumps(context), content_type="application/json")
                if student:
                    if code != tCode:
                        context['success'] = False
                        context['code'] = 206
                        context['result'] = '验证码错误，请重新输入'
                        return HttpResponse(json.dumps(context), content_type="application/json")
                    if eType == "2":
                        context['success'] = True
                        context['code'] = 200
                        context['result'] = '验证成功'
                        return HttpResponse(json.dumps(context), content_type="application/json")
                    else:
                        context['success'] = True
                        context['code'] = 200
                        context['studentInfo'] = serializers.serialize('json', student)
                        context['result'] = '登录成功'
                        response = HttpResponse(json.dumps(context), content_type="application/json")
                        response.set_signed_cookie('login_id', student.id, salt="id", max_age=60*60*24*7)
                        return response
                else:
                    if eType == "3":
                        Student.objects.create(email=email, password=123)
                        context['success'] = True
                        context['code'] = 200
                        context['result'] = '邮箱还未被注册,注册并登录成功'
                        context['studentInfo'] = serializers.serialize('json', student)
                        response = HttpResponse(json.dumps(context), content_type="application/json")
                        response.set_signed_cookie('login_id', student.id, salt="id", max_age=60*60*24*7)
                        return response
                    else:
                        context['success'] = False
                        context['code'] = 204
                        context['result'] = '邮箱还未被注册'
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


# 设置密码（注册、更改密码、重置密码）
def setPwd(request):
    context = {'success': False, 'code': 403, 'result': ''}
    if request.method == "POST":
        try:
            reqBody = eval(request.body.decode())
            email = reqBody.get("email")
            # 1代表注册，2代表更改，3代表重置
            pType = reqBody.get("type")
            code = reqBody.get("code")
            pwd = reqBody.get("password")
            nPwd = reqBody.get("newPassword")
            print(nPwd)
            student = Student.objects.filter(email=email).first()
            if pType == "2":
                if student:
                    if pwd == student.password:
                        student.password = nPwd
                        context['code'] = "200"
                        context['error_email'] = "修改密码成功"
                        context['success'] = True
                        return HttpResponse(json.dumps(context), content_type="application/json")
                    else:
                        context['code'] = "205"
                        context['error_email'] = "原密码验证错误，请重试"
                        context['success'] = False
                        return HttpResponse(json.dumps(context), content_type="application/json")
                else:
                    context['code'] = "202"
                    context['error_email'] = "找不到该邮箱的用户信息"
                    context['success'] = True
                    return HttpResponse(json.dumps(context), content_type="application/json")
            else:
                eObj = EmailVerifyRecord.objects.filter(email=email, code=code).order_by("-id").first()
                sec = (datetime.datetime.now() - eObj.send_time).seconds
                if sec > 720:
                    context['code'] = "210"
                    context['error_email'] = "验证码已失效，请重新验证"
                    context['success'] = False
                    return HttpResponse(json.dumps(context), content_type="application/json")
                if pType == "1":
                    if student:
                        context['code'] = "201"
                        context['error_email'] = "该邮箱已注册"
                        context['success'] = False
                        return HttpResponse(json.dumps(context), content_type="application/json")
                    else:
                        Student.objects.create(
                            email=email,
                            password=nPwd
                        )
                        context['code'] = "200"
                        context['error_email'] = "注册成功"
                        context['success'] = True
                        return HttpResponse(json.dumps(context), content_type="application/json")
                else:
                    if student:
                        student.password = nPwd
                        context['code'] = "200"
                        context['error_email'] = "修改密码成功"
                        context['success'] = True
                        return HttpResponse(json.dumps(context), content_type="application/json")
                    else:
                        context['code'] = "202"
                        context['error_email'] = "找不到该邮箱的用户信息"
                        context['success'] = True
                        return HttpResponse(json.dumps(context), content_type="application/json")
        except Exception as e:
            print("错误信息 : ", e)
            context['code'] = "404"
            context['error_email'] = "接口错误, 请稍后重试"
            context['success'] = False
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
            # user_obj = Student.objects.filter(email=email).first()
            # if user_obj:
            #     context['code'] = "111"
            #     context['error_email'] = "用户已存在"
            #     context['success'] = False
            #     return HttpResponse(json.dumps(context), content_type="application/json")
            # else:
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


# 上传图片
def uploadAvatar(request):
    if request.method == 'POST':
        context = {
            'code': 200,
            'success': True,
            'result': '更换头像成功',
            'avatar': ''
        }
        response = eval(request.body.decode())
        avatar = response.get('avatar')
        print(request.FILES)
        sId = request.get_signed_cookie('login_id', default=None, salt='id')
        if not sId:
            context['code'] = 403
            context['success'] = False
            context['result'] = '用户登录信息获取失败，请重新登录'
            return HttpResponse(json.dumps(context), content_type="application/json")
        s = Student.objects.filter(id=sId).first()
        print(s.avatar)
        imgData = base64.b64decode(avatar)
        # data = ContentFile(base64.b64decode(imgData), name=sId + '.jpg')  # You can save this as file instance.
        save_path = '%s/img/avatars/%s' % (settings.MEDIA_ROOT, sId + '.jpg')
        context['avatar'] = save_path[save_path.find('/media'):]
        with open(save_path, "wb") as f:
            f.write(imgData)
            f.close()
        # file_url = 'static/upload/%s.%s' % (sId, 'jpg')
        # leniyimg = open(file_url, 'wb')
        # leniyimg.write(imgData)
        # leniyimg.close()
        url = settings.ALLOWED_HOSTS[0]
        s.avatar = save_path[save_path.find('/media'):]
        s.gender = 1
        s.save()
        return HttpResponse(json.dumps(context), content_type="application/json")


# def getAvatar(request):
#     if request.method == 'GET':
#         print(request.GET.get('path'))
#         return HttpResponse(json.dumps('ok'))
        # imagepath = os.path.join(settings.BASE_DIR, "static/resume/images/{}".format(file_name))  # 图片路径
        # with open(imagepath, 'rb') as f:
        #     image_data = f.read()
