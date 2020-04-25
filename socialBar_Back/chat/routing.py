
from . import consumers
from django.conf.urls import url, include

websocket_urlpatterns = [
    url(r'^ws/chat/(?P<group_name>[^/]+)/$', consumers.ChatConsumer),
    url(r'^push/(?P<id>[0-9a-z]+)/$', consumers.PushConsumer),
]