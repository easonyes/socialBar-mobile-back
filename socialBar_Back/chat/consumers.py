from channels.generic.websocket import AsyncJsonWebsocketConsumer, AsyncWebsocketConsumer
import json
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import *
from myApp.models import *
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rest.settings')
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
django.setup()


class ChatConsumer(AsyncJsonWebsocketConsumer):
    chats = dict()

    async def connect(self):
        self.group_name = self.scope['url_route']['kwargs']['group_name']
        print(type(self.group_name))
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        # 将用户添加至聊天组信息chats中
        try:
            ChatConsumer.chats[self.group_name].add(self)
        except:
            ChatConsumer.chats[self.group_name] = set([self])

        # print(ChatConsumer.chats)
        # 创建连接时调用
        await self.accept()

    async def disconnect(self, close_code):
        # 连接关闭时调用
        # 将关闭的连接从群组中移除
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        # 将该客户端移除聊天组连接信息
        ChatConsumer.chats[self.group_name].remove(self)
        await self.close()

    async def receive_json(self, message, **kwargs):
        # 收到信息时调用
        to_user = message.get('to_user')
        print(type(to_user))
        from_user = message.get('from_user')
        time = message.get('time')
        # 信息发送
        length = len(ChatConsumer.chats[self.group_name])
        if length == 2:
            print('两个人')
            Chat.objects.create( fromStudent=Student.objects.get(id=int(from_user)), toStudent=Student.objects.get(id=int(to_user)),
                content=message.get('message'), type=1, unread=False )
            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "chat.message",
                    "message": message.get('message'),
                    "from_user": from_user,
                    "to_user": to_user,
                    "time": time,
                },
            )
        else:
            # try:
            #   user = Student.objects.get(id=to_user)
            #except Student.DoesNotExist:
            #   user = None
            print(to_user)
            Chat.objects.create( fromStudent=Student.objects.get(id=int(from_user)), toStudent=Student.objects.get(id=int(to_user)),
                content=message.get('message'), type=1, unread=True )
            print(to_user in ChatConsumer.chats)
            channel_layer = get_channel_layer()
            print(channel_layer)
            if to_user in ChatConsumer.chats:
                await self.channel_layer.group_send(
                    to_user,
                    {
                        "type": "push.message",
                        "event": {
                            "message": message.get('message'),
                            "from_user": from_user,
                            "to_user": to_user,
                            "time": time,
                        },
                    },
                )

    async def chat_message(self, event):
        # Handles the "chat.message" event when it's sent to us.
        # print(event)
        await self.send_json({
            "message": event["message"],
            "from_user": event["from_user"],
            "to_user": event["to_user"],
            "time": event["time"],
        })

    async def push_message(self, event):
        # print(event)
        await self.send_json({
            "message": event["message"],
            "from_user": event["from_user"],
            "to_user": event["to_user"],
            "time": event["time"],
        })


# 推送consumer
class PushConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.group_name = self.scope['url_route']['kwargs']['id']
        print(self.channel_layer)
        # 将用户添加至聊天组信息chats中
        try:
            ChatConsumer.chats[self.group_name].add(self)
        except:
            ChatConsumer.chats[self.group_name] = set([self])
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

        # print(PushConsumer.chats)

    async def push_message(self, event):
        # print(event)
        await self.send(text_data=json.dumps({
            "event": event['event']
        }))


def push(id, event):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        id,
        {
            "type": "push.message",
            "event": event
        }
    )