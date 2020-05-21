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
from asgiref.sync import async_to_sync, sync_to_async
from channels.layers import get_channel_layer
from django.db import connection


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


commonRes = {
    'code': 200,
    'result': '成功',
    'success': True
}


def userVerified(request):
    res = {
        'success': False,
        'result': '获取用户登录信息失败，请重新登录',
        'code': 403
    }
    sId = request.get_signed_cookie('login_id', default=None, salt='id')
    if not sId:
        return HttpResponse(json.dumps(res), content_type="application/json")
    # student = Student.objects.filter(id=sId).first()
    # if student.status != 1:
    #     res['result'] = '用户还未实名认证，完成实名认证解锁更多操作哦！'
    #     return HttpResponse(json.dumps(res), content_type="application/json")


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
        stuId = request.GET.get('userId')
        if stuId:
            student = Student.objects.get(id=stuId)
            res['studentInfo']['postsNum'] = len(Post.objects.filter(userId=stuId))
            loginStu = model_to_dict(Student.objects.get(id=sId))
            res['studentInfo']['followed'] = False
            if int(stuId) in eval(loginStu['starList']):
                res['studentInfo']['followed'] = True
        else:
            student = Student.objects.filter(id=sId).first()
            res['studentInfo']['postsNum'] = len(Post.objects.filter(userId=sId))
        # res['result'] = serializers.serialize('json', student)
        res['success'] = True
        res['result'] = '获取用户数据成功'
        res['code'] = 200
        # res['studentInfo'] = model_to_dict(student)
        # print(res)
        res['studentInfo']['id'] = student.id
        res['studentInfo']['avatar'] = str(student.avatar)
        res['studentInfo']['nickName'] = student.nickname
        res['studentInfo']['birthday'] = student.birthday
        res['studentInfo']['status'] = student.status
        res['studentInfo']['age'] = student.age
        res['studentInfo']['currentSchool'] = student.currentSchool
        res['studentInfo']['currentEducation'] = student.currentEducation
        res['studentInfo']['gender'] = student.gender
        res['studentInfo']['starsNum'] = len(eval(student.starList))
        res['studentInfo']['fansNum'] = len(eval(student.fansList))
        return JsonResponse(res)


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
        fanList = eval(Student.objects.get(id=userId).fansList)
        userName = response.get('nickName')
        createPlace = ""
        if response.get('createPlace'):
            createPlace = response.get('createPlace')
        content = response.get('content')
        site = response.get('site')
        dynamic = Post.objects.create(userId=Student.objects.filter(id=userId).first(), userName=userName,
                                      createPlace=createPlace, content=content, site=site, imgs=[])
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
        if fanList:
            for i in fanList:
                s = Student.objects.get(id=i)
                siteList = eval(s.siteList)
                for j in siteList:
                    if j['id'] == site:
                        s.unReadPost += 1
                        s.save()
                        break
        return JsonResponse(context)


# 改变默认站点
def changeSite(request):
    context = {
        'code': 200,
        'result': '更换站点成功',
        'success': True
    }
    if request.method == 'POST':
        response = eval(request.body.decode())
        site = response.get('site')
        sId = request.get_signed_cookie('login_id', default=None, salt='id')
        student = Student.objects.filter(id=sId).first()
        student.defaultSite = site
        student.save()
        return JsonResponse(context)


# 获取动态列表
def postList(request):
    context = {
        'code': 200,
        'result': '获取列表成功',
        'postList': [],
        'success': True
    }
    if request.method == "GET":
        userId = request.get_signed_cookie('login_id', default=None, salt='id')
        pType = request.GET.get('type')
        site = request.GET.get('site')
        lastId = request.GET.get('lastId')
        if pType == '2':
            if lastId:
                lastId = (int(lastId))
                posts = Post.objects.raw('SELECT * from myapp_post WHERE site = %s and id < %s ORDER BY id DESC', [site, lastId])
            else:
                posts = Post.objects.filter(site=site).order_by('-id')
            rePost = list(posts[0:10])
            for i in range(0, len(rePost)):
                rePost[i] = model_to_dict(rePost[i])
                liked = list(Interactive.objects.filter(postId=rePost[i]['id'], userId=userId, type=1))
                stared = list(Interactive.objects.filter(postId=rePost[i]['id'], userId=userId, type=3))
                rePost[i]['liked'] = False
                rePost[i]['stared'] = False
                if liked:
                    rePost[i]['liked'] = True
                if stared:
                    rePost[i]['stared'] = True
                # print(rePost[i])
                student = model_to_dict(Student.objects.filter(id=rePost[i]['userId']).first())
                rePost[i]['avatar'] = str(student['avatar'])
                rePost[i]['currentSchool'] = student['currentSchool']
                rePost[i]['currentEducation'] = student['currentEducation']
                rePost[i]['gender'] = student['gender']
                # print(student)
            context['postList'] = rePost
            # print(rePost)
            return JsonResponse(context)
        if pType == '1':
            if lastId:
                hotValue = int(request.GET.get('hotValue'))
                lastId = (int(lastId))
                posts = Post.objects.raw(
                    'SELECT * from myapp_post WHERE site = %s and hotValue > 0 and hotValue <= %s and id < %s ORDER BY hotValue DESC, id DESC',
                    [site, hotValue, lastId])
            else:
                posts = Post.objects.raw(
                    'SELECT * from myapp_post WHERE site = %s and hotValue > 0 ORDER BY hotValue DESC, id DESC',
                    [site])
                print(posts)
            rePost = list(posts[0:10])
            print(rePost)
            for i in range(0, len(rePost)):
                rePost[i] = model_to_dict(rePost[i])
                liked = list(Interactive.objects.filter(postId=rePost[i]['id'], userId=userId, type=1))
                stared = list(Interactive.objects.filter(postId=rePost[i]['id'], userId=userId, type=3))
                rePost[i]['liked'] = False
                rePost[i]['stared'] = False
                if liked:
                    rePost[i]['liked'] = True
                if stared:
                    rePost[i]['stared'] = True
                # print(rePost[i])
                student = model_to_dict(Student.objects.filter(id=rePost[i]['userId']).first())
                rePost[i]['avatar'] = str(student['avatar'])
                rePost[i]['currentSchool'] = student['currentSchool']
                rePost[i]['currentEducation'] = student['currentEducation']
                rePost[i]['gender'] = student['gender']
                # print(student)
            context['postList'] = rePost
            # print(rePost)
            return JsonResponse(context)
        return JsonResponse(context)


# 获取动态详情
def getPostDetail(request):
    userVerified(request)
    if request.method == 'GET':
        context = {
            'code': 200,
            'result': '获取动态成功',
            'success': True,
            'poInfo': ''
        }
        pId = request.GET.get('id')
        po = Post.objects.get(id=pId)
        userId = request.get_signed_cookie('login_id', default=None, salt='id')
        before = ""
        if History.objects.filter(userId=userId, postId=pId):
            before = History.objects.filter(userId=userId, postId=pId).last()
        his = History.objects.create(userId=Student.objects.get(id=userId), postId=Post.objects.get(id=pId))
        if before:
            sec = (his.viewTime - before.viewTime).seconds
            if sec > 60 * 60 * 60 * 2:
                po.hotValue += 1
                po.save()
        else:
            po.hotValue += 1
            po.save()
        po = model_to_dict(Post.objects.get(id=pId))
        liked = list(Interactive.objects.filter(postId=po['id'], userId=userId, type=1))
        stared = list(Interactive.objects.filter(postId=po['id'], userId=userId, type=3))
        po['liked'] = False
        po['stared'] = False
        if liked:
            po['liked'] = True
        if stared:
            po['stared'] = True
        # print(rePost[i])
        comments = list(Comment.objects.filter(postId=pId, type=1))
        cLen = len(comments)
        loginStu = model_to_dict(Student.objects.get(id=userId))
        poStu = po['userId']
        po['followed'] = False
        if poStu in eval(loginStu['starList']):
            po['followed'] = True
        for i in range(0, cLen):
            comments[i] = model_to_dict(comments[i])
            student = model_to_dict(Student.objects.get(id=comments[i]['formUser']))
            liked = CommentActive.objects.filter(commentId=comments[i]['id'], fromStudent=userId, type=1)
            disliked = CommentActive.objects.filter(commentId=comments[i]['id'], fromStudent=userId, type=2)
            comments[i]['liked'] = False
            comments[i]['disliked'] = False
            if liked:
                comments[i]['liked'] = True
            if disliked:
                comments[i]['disliked'] = True
            comments[i]['children'] = 0
            children = list(Comment.objects.filter(toComment=comments[i]['id'], type=2))
            if children:
                # for j in range(0, len(children)):
                #     children[j] = model_to_dict(children[j])
                #     stu = model_to_dict(Student.objects.get(id=children[j]['formUser']))
                #     children[j]['currentSchool'] = stu['currentSchool']
                #     children[j]['nickName'] = stu['nickname']
                #     children[j]['avatar'] = str(stu['avatar'])
                #     children[j]['currentEducation'] = stu['currentEducation']
                #     children[j]['gender'] = stu['gender']
                #     print(children[j])
                comments[i]['children'] = len(children)
            comments[i]['avatar'] = str(student['avatar'])
            comments[i]['nickName'] = student['nickname']
            comments[i]['currentSchool'] = student['currentSchool']
            comments[i]['currentEducation'] = student['currentEducation']
            comments[i]['gender'] = student['gender']
        student = model_to_dict(Student.objects.filter(id=po['userId']).first())
        po['avatar'] = str(student['avatar'])
        po['currentSchool'] = student['currentSchool']
        po['currentEducation'] = student['currentEducation']
        po['gender'] = student['gender']
        po['pComments'] = comments
        context['poInfo'] = po
        return JsonResponse(context)


# 获取回复详情
def replayDetail(request):
    if request.method == 'GET':
        context = {
            'code': 200,
            'result': '获取回复成功',
            'success': True,
            'replayList': []
        }
        pId = request.GET.get('id')
        toComment = request.GET.get('toComment')
        userId = request.get_signed_cookie('login_id', default=None, salt='id')
        lastId = request.GET.get('lastId')
        if lastId:
            replays = list(Comment.objects.raw('SELECT * from myapp_comment WHERE toComment = %s and postId_id = %s and id > %s ORDER BY id', [toComment, pId, lastId]))
        else:
            replays = list(Comment.objects.filter(toComment=toComment, postId=pId))
        replayList = replays[0:10]
        for j in range(0, len(replayList)):
            replayList[j] = model_to_dict(replayList[j])
            stu = model_to_dict(Student.objects.get(id=replayList[j]['formUser']))
            liked = CommentActive.objects.filter(commentId=replayList[j]['id'], fromStudent=userId, type=1)
            disliked = CommentActive.objects.filter(commentId=replayList[j]['id'], fromStudent=userId, type=2)
            replayList[j]['liked'] = False
            replayList[j]['disliked'] = False
            if liked:
                replayList[j]['liked'] = True
            if disliked:
                replayList[j]['disliked'] = True
            replayList[j]['currentSchool'] = stu['currentSchool']
            replayList[j]['nickName'] = stu['nickname']
            replayList[j]['avatar'] = str(stu['avatar'])
            replayList[j]['currentEducation'] = stu['currentEducation']
            replayList[j]['gender'] = stu['gender']
            if replayList[j]['toUser']:
                replayList[j]['toName'] = model_to_dict(Student.objects.get(id=replayList[j]['toUser']))['nickname']
            print(replayList[j])
        context['replayList'] = replayList
    return JsonResponse(context)


# 动态点赞
def like(request):
    if request.method == 'POST':
        req = eval(request.body.decode())
        sId = request.get_signed_cookie('login_id', default=None, salt='id')
        student = Student.objects.filter(id=sId).first()
        pId = req.get('id')
        post = Post.objects.filter(id=pId).first()
        pType = req.get('type')
        if pType == '1':
            Interactive.objects.get(userId=student, postId=post, type=1).delete()
            post.likes -= 1
            post.hotValue -= 5
        elif pType == '2':
            Interactive.objects.create(userId=student, postId=post, type=1)
            post.likes += 1
            post.hotValue += 5
        elif pType == '3':
            Interactive.objects.get(userId=student, postId=post, type=3).delete()
            post.stars -= 1
            post.hotValue -= 20
        elif pType == '4':
            Interactive.objects.create(userId=student, postId=post, type=3)
            post.stars += 1
            post.hotValue += 20
        post.save()
        return JsonResponse(commonRes)


# 评论
def comment(request):
    if request.method == 'POST':
        req = eval(request.body.decode())
        sId = request.get_signed_cookie('login_id', default=None, salt='id')
        pId = req.get('id')
        po = Post.objects.get(id=pId)
        po.comments += 1
        po.hotValue += 10
        po.save()
        content = req.get('content')
        cType = req.get('type')
        if cType == '1':
            Comment.objects.create(formUser=Student.objects.get(id=sId), postId=po, content=content, type=1)
        elif cType == '2':
            toComment = req.get('toComment')
            toStudent = req.get('toStudent')
            if toStudent:
                Comment.objects.create(formUser=Student.objects.get(id=sId), toUser=Student.objects.get(id=toStudent),
                                       toComment=toComment, postId=po, content=content, type=2)
            else:
                Comment.objects.create(formUser=Student.objects.get(id=sId), toComment=toComment, postId=po,
                                       content=content, type=2)
        return JsonResponse(commonRes)


# 评论点赞
def likeComment(request):
    if request.method == "POST":
        req = eval(request.body.decode())
        sId = request.get_signed_cookie('login_id', default=None, salt='id')
        cId = req.get('id')
        com = Comment.objects.get(id=cId)
        stu = Student.objects.get(id=sId)
        cType = req.get('type')
        if cType == '1':
            comDis = CommentActive.objects.filter(commentId=com, fromStudent=stu, type=2)
            if comDis:
                CommentActive.objects.get(commentId=com, fromStudent=stu, type=2).delete()
                com.dislikes -= 1
            CommentActive.objects.create(commentId=com, fromStudent=stu, type=1)
            com.likes += 1
        elif cType == '2':
            CommentActive.objects.get(commentId=com, fromStudent=stu, type=1).delete()
            com.likes -= 1
        elif cType == '3':
            CommentActive.objects.create(commentId=com, fromStudent=stu, type=2)
            comLik = CommentActive.objects.filter(commentId=com, fromStudent=stu, type=1)
            if comLik:
                CommentActive.objects.get(commentId=com, fromStudent=stu, type=1).delete()
                com.likes -= 1
            com.dislikes += 1
        elif cType == '4':
            CommentActive.objects.get(commentId=com, fromStudent=stu, type=2).delete()
            com.dislikes -= 1
        com.save()
        return JsonResponse(commonRes)


# 关注
def followStu(request):
    context = {
        'code': 200,
        'result': '关注成功',
        'success': True
    }
    if request.method == "POST":
        req = eval(request.body.decode())
        userId = request.get_signed_cookie('login_id', default=None, salt='id')
        loginStu = Student.objects.get(id=userId)
        stuDic = model_to_dict(Student.objects.get(id=userId))
        sId = req.get('id')
        fStu = Student.objects.get(id=sId)
        fanList = eval(model_to_dict(fStu)['fansList'])
        fType = req.get('type')
        starList = eval(stuDic['starList'])
        if fType == '1':
            if userId == str(sId):
                context['code'] = 210
                context['result'] = '不能关注自己'
                context['success'] = False
                return JsonResponse(context)
            starList.append(sId)
            loginStu.starList = starList
            loginStu.save()
            fanList.append(userId)
            fStu.fansList = fanList
            fStu.save()
            return JsonResponse(context)
        elif fType == '2':
            starList.remove(sId)
            loginStu.starList = starList
            loginStu.save()
            fanList.remove(userId)
            fStu.fansList = fanList
            fStu.save()
            context['result'] = "取消关注成功"
            return JsonResponse(context)
        return JsonResponse(context)


# 获取粉丝列表
def getFanList(request):
    if request.method == "GET":
        context = {
            'code': 200,
            'result': '获取粉丝列表成功',
            'success': True,
            'fanList': []
        }
        userId = request.GET.get('userId')
        fanIds = eval(model_to_dict(Student.objects.get(id=userId))['fansList'])
        fanList = []
        for i in fanIds:
            stu = model_to_dict(Student.objects.get(id=i))
            stu['avatar'] = str(stu['avatar'])
            fanList.append(stu)
        context['fanList'] = fanList
        return JsonResponse(context)


# 获取关注列表
def getStarList(request):
    if request.method == "GET":
        context = {
            'code': 200,
            'result': '获取粉丝列表成功',
            'success': True,
            'starList': []
        }
        userId = request.GET.get('userId')
        fanIds = eval(model_to_dict(Student.objects.get(id=userId))['starList'])
        fanList = []
        for i in fanIds:
            stu = model_to_dict(Student.objects.get(id=i))
            stu['avatar'] = str(stu['avatar'])
            fanList.append(stu)
        context['starList'] = fanList
        return JsonResponse(context)


# 获取发表动态列表
def getPostList(request):
    if request.method == "POST":
        context = {
            'code': 200,
            'result': '获取列表成功',
            'postList': [],
            'success': True
        }
        req = eval(request.body.decode())
        userId = req.get('userId')
        lastId = req.get('lastId')
        siteList = req.get('siteList')
        inStr = ""
        for i in siteList:
            inStr = inStr + str(i) + ", "
        print(inStr)
        if lastId:
            lastId = (int(lastId))
            posts = Post.objects.raw('SELECT * from myapp_post WHERE userId = %s and id < %s and site in ( %s ) ORDER BY id DESC', [userId, lastId, inStr])
            print(posts)
        else:
            posts = Post.objects.filter(site__in=siteList, userId=userId).order_by('-id')
        rePost = list(posts[0:10])
        for i in range(0, len(rePost)):
            rePost[i] = model_to_dict(rePost[i])
            liked = list(Interactive.objects.filter(postId=rePost[i]['id'], userId=userId, type=1))
            stared = list(Interactive.objects.filter(postId=rePost[i]['id'], userId=userId, type=3))
            rePost[i]['liked'] = False
            rePost[i]['stared'] = False
            if liked:
                rePost[i]['liked'] = True
            if stared:
                rePost[i]['stared'] = True
            # print(rePost[i])
            student = model_to_dict(Student.objects.filter(id=rePost[i]['userId']).first())
            rePost[i]['avatar'] = str(student['avatar'])
            rePost[i]['currentSchool'] = student['currentSchool']
            rePost[i]['currentEducation'] = student['currentEducation']
            rePost[i]['gender'] = student['gender']
            # print(student)
        context['postList'] = rePost
        # print(rePost)
        return JsonResponse(context)


def chat(request):
    if request.method == 'GET':
        '''处理get请求，返回两用户的聊天记录'''
        # recipient = User.objects.get(username=username)
        # sender = request.user
        # qs_one = Chat.objects.filter(sender=sender,recipient=recipient)  # A发送给B的信息
        # qs_two = Chat.objects.filter(sender=recipient,recipient=sender)  # B发送给A的信息
        # all = qs_one.union(qs_two).order_by('created_at')  # 取查到的信息内容的并集，相当于他两的聊天记录
        return JsonResponse(commonRes)
    else:
        req = eval(request.body.decode())
        content = req.get('content')
        from_user = req.get('from_user')
        to_user = req.get('to_user')
        # recipient = User.objects.get(username=username)  # 消息接收者
        # content = request.POST.get('content','')  # 消息内容
        # sender = request.user  # 发送者
        # msg = Chat.objects.create(sender=sender,recipient=recipient,message=content)  # 把消息存储到数据库
        # qs_one = Chat.objects.filter(sender=sender,recipient=recipient)  # A发送给B的信息
        # qs_two = Chat.objects.filter(sender=recipient,recipient=sender)  # B发送给A的信息
        # all = qs_one.union(qs_two).order_by('created_at')  # 取查到的信息内容的并集，相当于他两的聊天记录
        channel_layer = get_channel_layer()
        # get_channel_layer()函数获得的是当前的websocket连接所对应的consumer类对象的channel_layer
        payload = {
            'type': 'receive',  # 这个type是有限制的，比如现在用到的就是cusumer的receive函数
            'message': content,  # 消息内容
            'sender': from_user,  # 发送者
            # 'created_at': str(msg.created_at)  # 创建时间
        }
        group_name = to_user  # 这里用的是接收者的用户名为组名，每个用户在进入聊天框后就会自动进入以自己用户名为组名的group
        async_to_sync(channel_layer.group_send)(group_name, payload)
        # 上一句是将channel_layer.group_send()从异步改为同步，正常的写法是channel_layer.group_send(group_name, payload)
        return JsonResponse(commonRes)


# 获取发表动态列表
def getCollectionList(request):
    if request.method == "GET":
        context = {
            'code': 200,
            'result': '获取列表成功',
            'postList': [],
            'success': True
        }
        sId = request.get_signed_cookie('login_id', default=None, salt='id')
        lastId = request.GET.get('lastId')
        if lastId:
            lastId = (int(lastId))
            cs = Interactive.objects.raw('SELECT * from myapp_interactive WHERE id < %s and userId_id = %s and type = 3 ORDER BY id DESC', [lastId, sId])
        else:
            cs = Interactive.objects.filter(userId=sId, type=3).order_by('-id')
        rePost = list(cs[0:10])
        print(rePost)
        reList = []
        for i in range(0, len(rePost)):
            po = model_to_dict(rePost[i].postId)
            print(po)
            liked = list(Interactive.objects.filter(postId=po['id'], userId=sId, type=1))
            stared = list(Interactive.objects.filter(postId=po['id'], userId=sId, type=3))
            po['liked'] = False
            po['stared'] = False
            if liked:
                po['liked'] = True
            if stared:
                po['stared'] = True
            # print(rePost[i])
            student = model_to_dict(rePost[i].userId)
            po['avatar'] = str(student['avatar'])
            po['currentSchool'] = student['currentSchool']
            po['currentEducation'] = student['currentEducation']
            po['gender'] = student['gender']
            po['iId'] = rePost[i].id
            # print(student)
            reList.append(po)
        context['postList'] = reList
        # print(rePost)
        return JsonResponse(context)


# 获取关注列表动态
def followPostList(request):
    if request.method == "POST":
        context = {
            'code': 200,
            'result': '获取列表成功',
            'postList': [],
            'success': True
        }
        req = eval(request.body.decode())
        userId = request.get_signed_cookie('login_id', default=None, salt='id')
        s = Student.objects.get(id=userId)
        s.unReadPost = 0
        s.save()
        starList = s.starList
        inStr1 = ""
        for i in eval(starList):
            inStr1 = inStr1 + str(i) + ","
        inStr1 = inStr1[:-1]
        if not inStr1:
            context['code'] = 210
            context['result'] = "用户还没有关注列表"
            context['success'] = True
            return JsonResponse(context)
        lastId = req.get('lastId')
        siteList = req.get('siteList')
        inStr = ""
        for i in siteList:
            inStr = inStr + str(i) + ","
        inStr = inStr[:-1]
        print(siteList)
        print(eval(starList))
        if lastId:
            lastId = (int(lastId))
            posts = Post.objects.raw('SELECT * from myapp_post WHERE userId_id in ( %s ) and id < %s and site in ( %s ) ORDER BY id DESC', [inStr1, lastId, inStr])
            print(posts)
        else:
            posts = Post.objects.filter(site__in=siteList, userId__in=eval(starList)).order_by('-id')
        rePost = list(posts[0:10])
        print(rePost)
        for i in range(0, len(rePost)):
            rePost[i] = model_to_dict(rePost[i])
            liked = list(Interactive.objects.filter(postId=rePost[i]['id'], userId=userId, type=1))
            stared = list(Interactive.objects.filter(postId=rePost[i]['id'], userId=userId, type=3))
            rePost[i]['liked'] = False
            rePost[i]['stared'] = False
            if liked:
                rePost[i]['liked'] = True
            if stared:
                rePost[i]['stared'] = True
            # print(rePost[i])
            student = model_to_dict(Student.objects.filter(id=rePost[i]['userId']).first())
            rePost[i]['avatar'] = str(student['avatar'])
            rePost[i]['currentSchool'] = student['currentSchool']
            rePost[i]['currentEducation'] = student['currentEducation']
            rePost[i]['gender'] = student['gender']
            # print(student)
        context['postList'] = rePost
        # print(rePost)
        return JsonResponse(context)


def dictfetchall(cursor):
    "从cursor获取所有行数据转换成一个字典"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


# 搜索列表及用户
def searchInfo(request):
    if request.method == "POST":
        context = {
            'code': 200,
            'result': '获取列表成功',
            'list': [],
            'success': True
        }
        req = eval(request.body.decode())
        userId = request.get_signed_cookie('login_id', default=None, salt='id')
        info = req.get('info')
        length = req.get('length')
        qType = req.get('type')
        print(type(qType))
        if qType == 1:
            siteList = req.get('siteList')
            inStr = ""
            for i in siteList:
                inStr = inStr + str(i) + ","
            inStr = inStr[:-1]
            cursor = connection.cursor()
            cursor.execute('SELECT * from myapp_post WHERE site in ( %s ) and content like "%%%s%%" ORDER BY length(content), id' %
                           (inStr, info))
            posts = dictfetchall(cursor)
            rePost = list(posts[length*10-10:length*10])
            for i in range(0, len(rePost)):
                print(rePost[i])
                liked = list(Interactive.objects.filter(postId=rePost[i]['id'], userId=userId, type=1))
                stared = list(Interactive.objects.filter(postId=rePost[i]['id'], userId=userId, type=3))
                rePost[i]['liked'] = False
                rePost[i]['stared'] = False
                if liked:
                    rePost[i]['liked'] = True
                if stared:
                    rePost[i]['stared'] = True
                # print(rePost[i])
                student = model_to_dict(Student.objects.filter(id=rePost[i]['userId_id']).first())
                rePost[i]['avatar'] = str(student['avatar'])
                rePost[i]['currentSchool'] = student['currentSchool']
                rePost[i]['currentEducation'] = student['currentEducation']
                rePost[i]['gender'] = student['gender']
                # print(student)
            context['list'] = rePost
        if qType == 2:
            cursor = connection.cursor()
            cursor.execute(
                'SELECT * from myapp_student WHERE nickName like "%%%s%%" ORDER BY length(nickName), id' % info)
            users = dictfetchall(cursor)
            reUsers = list(users[length * 10 - 10:length * 10])
            for i in reUsers:
                print(i)
            context['list'] = reUsers
        return JsonResponse(context)
