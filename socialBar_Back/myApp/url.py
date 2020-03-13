from django.urls import re_path
from . import views

urlpatterns = [
    # path('', views.index, name='index'),
    re_path(r'^login$', views.login),
    re_path(r'^emailValidate$', views.emailValidate),
    re_path(r'^sendEmail$', views.sendEmailRegisterCodeView),
    re_path(r'^setPwd$', views.setPwd)
]