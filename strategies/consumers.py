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
        resolved_query = event['message']
        command = resolved_query.upper()
        response = self.prepare_response(resolved_query)

        if command == 'RUN XBTUSD':
            self.manager.place_orders('XBTUSD')
            response['result']['fulfillment']['messages'].append(
                self.prepare_message('Opening orders XBTUSD')
            )

        elif command == 'RUN XBTM18':
            self.manager.place_orders('XBTM18')
            response['result']['fulfillment']['messages'].append(
                self.prepare_message('Opening orders XBTM18')
            )

        elif command == 'DELTA':
            delta = self.manager.exchange.calc_pts_delta()
            text = 'Delta: %.4f' % delta.get('basis')
            title = 'XBTUSD: %s' % str(delta.get('XBTUSD'))
            subtitle = 'XBTM18: %s' % str(delta.get('XBTM18'))
            response['result']['fulfillment']['messages'].append(
                self.prepare_message(text, title, subtitle)
            )

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': response
        }))

    def prepare_response(self, query):
        return {
            'result': {
                'resolvedQuery': query,
                'fulfillment': {
                    'messages': []
                }
            }
        }

    def prepare_message(self, text, title=None, subtitle=None):
        return {
            'type': 'basic_card',
            'image': None,
            'buttons': [],
            'title': title,
            'subtitle': subtitle,
            'formattedText': text,
        }
