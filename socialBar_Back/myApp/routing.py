
from . import consumers
from django.conf.urls import url, include

websocket_urlpatterns = [
    url(r'^ws/chat/(?P<group_name>[^/]+)/$', consumers.ChatConsumer),
]