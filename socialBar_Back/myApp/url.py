from django.urls import re_path
from . import views

urlpatterns = [
    # path('', views.index, name='index'),
    re_path(r'^login$', views.login),
    re_path(r'^emailValidate$', views.emailValidate),
    re_path(r'^sendEmail$', views.sendEmailRegisterCodeView),
    re_path(r'^setPwd$', views.setPwd),
    re_path(r'^uploadAvatar$', views.uploadAvatar),
    re_path(r'^verify$', views.verify),
    re_path(r'^postDynamic$', views.postDynamic),
    re_path(r'^updateStu$', views.updateStu),
    re_path(r'^getUserInfo$', views.getUserInfo),
]