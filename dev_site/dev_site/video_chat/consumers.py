# blank/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer

class SignalingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print("WebSocket connect:", self.scope["path"], self.scope.get("client"))
        self.room = self.scope['url_route']['kwargs']['room_name']
        self.group_name = f"signaling_{self.room}"
        # Join a group so both browsers share it
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    # Receive messages from browser, broadcast to group
    async def receive(self, text_data):
        data = json.loads(text_data)
        # data should be { "type": "offer"/"answer"/"ice", ... }
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'signal_message',
                'message': data
            }
        )

    # Handler for group messages
    async def signal_message(self, event):
        await self.send(text_data=json.dumps(event['message']))
