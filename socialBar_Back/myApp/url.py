from django.urls import re_path
from . import views

urlpatterns = [
    # path('', views.index, name='index'),
    re_path(r'^login$', views.login),
    re_path(r'^register$', views.register),
]