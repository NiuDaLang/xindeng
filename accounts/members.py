import json
from channels.generic.websocket import AsyncWebsocketConsumer

class Solar(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("solar_updates", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code): #cleanup
        await self.channel_layer.group_discard("solar_updates", self.channel_name)

    async def solar_message(self, event):
        await self.send(text_data=json.dumps({'term': event['term']}))


class ChatNotification(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if self.user.is_authenticated:
            # Create a unique group name for this specific user
            self.group_name = f"user_notifications_{self.user.id}"
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    # This method is called when the server sends a 'chat_notification' message
    async def chat_notification(self, event):
        # 'event' contains everything you sent in async_to_sync(...)
        await self.send(text_data=json.dumps({
            'type': 'new_message', # This matches your JS "if" statement
            'msg_id': event['msg_id'],
            'receiver_id': event['receiver_id'],
            'sender_id': event['sender_id'],
            'sender_name': event['sender_name'],
            'sender_avatar_url': event['sender_avatar_url'],
            'msg_content': event['msg_content'],
            'msg_img_url': event['msg_img_url'],
            'msg_timestamp': event['msg_timestamp'],
        }))