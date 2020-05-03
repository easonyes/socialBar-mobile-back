from django.http import HttpResponse, JsonResponse
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
from django.forms.models import model_to_dict
from django.core.files.base import ContentFile
from django.utils import timezone
import os
import re


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


def userVerified(request):
    res = {
        'success': False,
        'result': '获取用户登录信息失败，请重新登录',
        'code': 403
    }
    sId = request.get_signed_cookie('login_id', default=None, salt='id')
    if not sId:
        return HttpResponse(json.dumps(res), content_type="application/json")
    student = Student.objects.filter(id=sId).first()
    if student.status != 1:
        res['result'] = '用户还未实名认证，完成实名认证解锁更多操作哦！'
        return HttpResponse(json.dumps(res), content_type="application/json")


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
            # print(context['studentInfo'])
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
                        response.set_signed_cookie('login_id', student.first().id, salt="id", max_age=60*60*24*7)
                        return response
                else:
                    if eType == "3":
                        s = Student.objects.create(email=email, password=123)
                        s.nickname = '用户_' + str(student.first().id)
                        s.save()
                        context['success'] = True
                        context['code'] = 200
                        context['result'] = '邮箱还未被注册,注册并登录成功'
                        context['studentInfo'] = serializers.serialize('json', Student.objects.filter(email=email))
                        response = HttpResponse(json.dumps(context), content_type="application/json")
                        response.set_signed_cookie('login_id', student.first().id, salt="id", max_age=60*60*24*7)
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
                        students = Student.objects.filter(email=email)
                        student = students.first()
                        student.nickname = '用户_' + str(student.id)
                        student.save()
                        context['studentInfo'] = serializers.serialize('json', students)
                        context['code'] = "200"
                        context['error_email'] = "注册成功"
                        context['success'] = True
                        response = HttpResponse(json.dumps(context), content_type="application/json")
                        response.set_signed_cookie('login_id', student.id, salt="id", max_age=60 * 60 * 24 * 7)
                        return response
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
            validStu = Certification.objects.filter(email=email)
            if not validStu:
                context['code'] = 203
                context['success'] = False
                context['error_email'] = "很遗憾，您的学校暂未与本APP合作，但我们会尽快与贵校合作，请关注官网咨询。"
                return HttpResponse(json.dumps(context), content_type="application/json")
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


# 更换头像
def uploadAvatar(request):
    if request.method == 'POST':
        userVerified(request)
        context = {
            'code': 200,
            'success': True,
            'result': '更换头像成功',
            'avatar': ''
        }
        response = eval(request.body.decode())
        avatar = response.get('avatar')
        print(avatar)
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


# 实名认证
def verify(request):
    if request.method == 'POST':
        context = {
            'code': 200,
            'success': True,
            'result': '实名认证成功'
        }
        sId = request.get_signed_cookie('login_id', default=None, salt='id')
        if not sId:
            context['code'] = 403
            context['success'] = False
            context['result'] = '用户登录信息获取失败，请重新登录'
            return HttpResponse(json.dumps(context), content_type="application/json")
        response = eval(request.body.decode())
        student = Student.objects.filter(id=sId).first()
        email = student.email
        idCard = response.get('idCard')
        s = Certification.objects.filter(email=email).first()
        realId = s.idCard
        if idCard == realId:
            student.status = 1
            student.currentSchool = Site.objects.filter(id=s.school).first().siteName
            siteList = []
            sList = []
            if s.doctor:
                student.currentEducation = 4
                doc = model_to_dict(Site.objects.filter(id=s.doctor).first())
                siteList.append(doc)
                sList.append(doc['id'])
            elif s.master:
                student.currentEducation = 3
            elif s.undergraduate:
                student.currentEducation = 2
            else:
                student.currentEducation = 1
            if s.master:
                mas = model_to_dict(Site.objects.filter(id=s.master).first())
                if mas['id'] not in sList:
                    sList.append(mas['id'])
                    siteList.append(mas)
            if s.undergraduate:
                und = model_to_dict(Site.objects.filter(id=s.undergraduate).first())
                if und['id'] not in sList:
                    sList.append(und['id'])
                    siteList.append(und)
            if s.specialist:
                spe = model_to_dict(Site.objects.filter(id=s.specialist).first())
                if spe['id'] not in sList:
                    siteList.append(spe)
            siteList.append(model_to_dict(Site.objects.filter(id=s.fromPlace).first()))
            if s.city != s.fromPlace:
                siteList.append(model_to_dict(Site.objects.filter(id=s.city).first()))
            siteList.insert(0, {'id': 1, 'siteName': '主站'})
            student.siteList = siteList
            student.save()
            print(student.siteList)
            return HttpResponse(json.dumps(context), content_type="application/json")
        else:
            context['code'] = 203
            context['success'] = False
            context['result'] = '身份证错误，实名认证失败'
            return HttpResponse(json.dumps(context), content_type="application/json")
    else:
        return HttpResponse(json.dumps('请使用post'), content_type="application/json")


# 更新用户信息
def updateStu(request):
    userVerified(request)
    context = {
        'code': 200,
        'success': True,
        'result': '信息更新成功'
    }
    if request.method == 'POST':
        # 如果 type == 1 则是更改昵称，否则为更新信息
        response = eval(request.body.decode())
        upType = response.get('type')
        print(response)
        if upType == 1:
            name = response.get('name')
            if Student.objects.filter(nickname=name):
                context['code'] = 201
                context['success'] = False
                context['result'] = '所选昵称与其他用户重复'
                return HttpResponse(json.dumps(context), content_type="application/json")
            else:
                sId = request.get_signed_cookie('login_id', default=None, salt='id')
                student = Student.objects.filter(id=sId).first()
                student.nickname = name
                student.save()
                context['result'] = '昵称更新成功'
                return HttpResponse(json.dumps(context), content_type="application/json")
        elif upType == 2:
            sId = request.get_signed_cookie('login_id', default=None, salt='id')
            student = Student.objects.filter(id=sId).first()
            birthday = response.get('birthday')
            if birthday:
                age = response.get('age')
                student.age = age
                student.birthday = birthday
            gender = response.get('gender')
            student.gender = gender
            student.save()
            return HttpResponse(json.dumps(context), content_type="application/json")


# 获取用户信息
def getUserInfo(request):
    res = {
        'success': False,
        'result': '获取用户登录信息失败，请重新登录',
        'studentInfo': {},
        'code': 403
    }
    sId = request.get_signed_cookie('login_id', default=None, salt='id')
    if not sId:
        return HttpResponse(json.dumps(res), content_type="application/json")
    else:
        student = Student.objects.filter(id=sId).first()

        # res['result'] = serializers.serialize('json', student)
        res['success'] = True
        res['result'] = '获取用户数据成功'
        res['code'] = 200
        # res['studentInfo'] = model_to_dict(student)
        # print(res)
        res['studentInfo']['nickName'] = student.nickname
        res['studentInfo']['birthday'] = student.birthday
        res['studentInfo']['age'] = student.age
        res['studentInfo']['gender'] = student.gender
        # print(context['studentInfo'])
        # response = HttpResponse(json.dumps(res), content_type="application/json")
        return JsonResponse(res)
        # return HttpResponse('ok')


# 获取用户聊天列表
def getChatList(request):
    userVerified(request)
    sId = request.get_signed_cookie('login_id', default=None, salt='id')


# 发表动态
def postDynamic(request):
    userVerified(request)
    context = {
        'success': True,
        'result': '发布成功',
        'code': 200
    }
    if request.method == 'POST':
        userId = request.get_signed_cookie('login_id', default=None, salt='id')
        response = eval(request.body.decode())
        userName = response.get('nickName')
        createPlace = ""
        if response.get('createPlace'):
            createPlace = response.get('createPlace')
        content = response.get('content')
        dynamic = Post.objects.create(userId=Student.objects.filter(id=userId).first(), userName=userName,
                                      createPlace=createPlace, content=content, imgs=[])
        imgs = response.get('imgs')
        if imgs:
            i = 0
            dir = '%s/img/dynamic/%s' % (settings.MEDIA_ROOT, dynamic.id)
            os.makedirs(dir, mode=0o777, exist_ok=True)
            dynamic.imgs = []
            for img in imgs:
                i += 1
                imgData = base64.b64decode(re.sub('^data:image/.*;base64,', '', img['content'], 0))
                save_path = '%s/%s' % (dir, str(i) + '.jpg')
                with open(save_path, "wb") as f:
                    f.write(imgData)
                    f.close()
                dynamic.imgs.append(save_path[save_path.find('/media'):])
            dynamic.save()
        print(imgs)
        return JsonResponse(context)


# 获取动态列表
def postList(request):
    context = {
        'code': 200,
        'result': '获取列表成功',
        'success': True
    }
    if request.method == "GET":
        pType = request.GET.get('type')
        if pType == 3:

            return JsonResponse(context)
        return JsonResponse(context)
