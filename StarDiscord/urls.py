"""
URL configuration for StarDiscord project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path
from StarDiscord import views

urlpatterns = [
    path('v1/sign/', views.sign),
    re_path(r'^images/(?P<image_name>\w+\.png)$', views.loadImage),
    path('v1/myselfinfo/', views.myselfInfo),
    path('v1/newchannel/', views.newChannels),
    path('v1/joinchannel/', views.joinChannel),
    path('v1/quitchannel/', views.quitChannel),
    path('v1/channelinfo/', views.channelInfo),
    path('v1/myselfinfo/', views.myselfInfo),
    path('v1/addfriend/', views.addFriend),
    path('v1/delfriend/', views.delFriend),
    path('v1/queryuser/', views.queryUser),
    path('v1/changepasswd/', views.changePasswd),
    path('v1/querychannel/', views.queryChannelInfo),
    path('v1/captcha/', views.getCaptcha),
    path('v1/pullchats/', views.pullChats),
    path('v1/addtag/', views.addTag),
]
