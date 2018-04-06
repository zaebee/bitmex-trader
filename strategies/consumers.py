from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer
from datetime import datetime
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
        postOnly = False
        side = None
        resolved_query = event['message']
        command = resolved_query.upper()
        response = self.prepare_response(resolved_query)

        if 'MARKET' in command:
            postOnly = True

        if 'SELL' in command:
            side = 'Sell'
        elif 'BUY' in command:
            side = 'Buy'

        if 'XBTUSD' in command:
            self.manager.place_orders('XBTUSD', side)
            response['result']['fulfillment']['messages'].append(
                self.prepare_message('Opening orders XBTUSD')
            )

        if 'XBTM18' in command:
            self.manager.place_orders('XBTM18', side)
            response['result']['fulfillment']['messages'].append(
                self.prepare_message('Opening orders XBTM18')
            )

        if 'CANCEL' == command:
            self.manager.exchange.cancel_all_orders()
            response['result']['fulfillment']['messages'].append(
                self.prepare_message('Orders are cancelled')
            )
            self.send(text_data=json.dumps({
                'message': response
            }))

        elif 'EXIT' == command:
            manager = RentOrderManager(POST_ONLY=False)
            manager.init()
            delta = manager.exchange.calc_pts_delta()
            # if delta['basis'] > 0:
            self.manager.place_stop_orders('XBTUSD')
            manager.place_stop_orders('XBTM18')
            response['result']['fulfillment']['messages'].append(
                self.prepare_message('Exit')
            )
            self.send(text_data=json.dumps({
                'message': response
            }))


        elif 'DELTA ON' == command:
            delta = self.manager.exchange.calc_pts_delta()
            text = 'Delta: %.4f' % delta.get('basis')
            response['result']['fulfillment']['messages'].append(
                self.prepare_message(text)
            )
            self.send(text_data=json.dumps({
                'message': response
            }))

        elif 'DELTA' == command:
            delta = self.manager.exchange.calc_pts_delta()

            XBTUSD = 'XBTUSD:%s' % str(delta.get('XBTUSD'))
            XBTM18 = 'XBTM18%s' % str(delta.get('XBTM18'))
            title = 'Delta: %.4f' % delta.get('basis')

            items = [
                {'title': 'XBTUSD', 'description': XBTUSD},
                {'title': 'XBTM18', 'description': XBTM18}
            ]

            response['result']['fulfillment']['messages'].append(
                self.prepare_message(title=title, subtitle=XBTUSD, text=XBTM18)
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

    def prepare_message(self, text=None, title=None, subtitle=None, items=[], basic_type='basic_card'):
        createdAt = datetime.now()
        return {
            'type': basic_type,
            'image': None,
            'buttons': [],
            'items': items,
            'title': title,
            'subtitle': subtitle,
            'formattedText': text,
            'createdAt': createdAt.isoformat(),
        }
