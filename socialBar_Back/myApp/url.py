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
    re_path(r'^postList$', views.postList),
    re_path(r'^changeSite$', views.changeSite),
    re_path(r'^like$', views.like),
    re_path(r'^getPostDetail$', views.getPostDetail),
    re_path(r'^comment$', views.comment),
    re_path(r'^likeComment$', views.likeComment),
    re_path(r'^replayDetail$', views.replayDetail),
    re_path(r'^followStu$', views.followStu),
    re_path(r'^getFanList$', views.getFanList),
    re_path(r'^getStarList$', views.getStarList),
    re_path(r'^getPostList$', views.getPostList),
]