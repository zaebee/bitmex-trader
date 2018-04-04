from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer
import json

from . rent_strategy import RentOrderManager

class StrategyConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.token_key = self.scope['url_route']['kwargs']['token_key']
        self.token_secret = self.scope['url_route']['kwargs']['token_secret']

        self.manager = RentOrderManager(symbol='XBTUSD')

        self.manager.init()

        await self.channel_layer.group_add(
            self.token_key,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        self.manager.exit()
        await self.channel_layer.group_discard(
            self.token_key,
            self.channel_name
        )

    async def receive(self, text_data):
        """
        Recieve text message with command start/close/check/list for trader.
        """
        text_data_json = json.loads(text_data)
        message = text_data_json.get('message')

        if message:
            await self.channel_layer.group_send(
                self.token_key,
                {
                    'type': 'chat_message',
                    'message': message
                }
            )

    async def chat_message(self, event):
        message = event['message']
        if message == 'run XBTUSD':
            self.manager.place_orders('XBTUSD')
        elif message == 'run XBTM18':
            self.manager.place_orders('XBTM18')
        elif 'close' in message.lower():
            pass
            # TODO run mamager.loop for check exit conditions
            # self.manager.place_orders()

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))
