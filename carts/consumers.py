# import json
# from channels.generic.websocket import AsyncWebsocketConsumer

# class CartSyncConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         # Authenticated users get a group based on ID; guests use session key
#         if self.scope["user"].is_authenticated:
#             self.group_name = f"cart_user_{self.scope['user'].id}"
#         else:
#             session_key = self.scope["session"].session_key or "guest"
#             self.group_name = f"cart_session_{session_key}"

#         await self.channel_layer.group_add(self.group_name, self.channel_name)
#         await self.accept()

#     async def disconnect(self, close_code):
#         await self.channel_layer.group_discard(self.group_name, self.channel_name)

#     # Receive message from channel group and forward it to the browser
#     async def cart_update_message(self, event):
#         await self.send(text_data=json.dumps({
#             "action": event["action"]
#         }))


import json
from channels.generic.websocket import AsyncWebsocketConsumer

class CartSyncConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if self.scope["user"].is_authenticated:
            self.group_name = f"cart_user_{self.scope['user'].id}"
        else:
            # Safely handle uninitialized guest storage contexts
            session = self.scope.get("session")
            session_key = session.session_key if session else None
            
            if not session_key:
                self.group_name = "cart_session_anonymous_guest"
            else:
                self.group_name = f"cart_session_{session_key}"

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def cart_update_message(self, event):
        await self.send(text_data=json.dumps({
            "action": event["action"]
        }))