from datetime import datetime
from django.conf import settings

from market_maker.market_maker import logger, OrderManager


class RentOrderManager(OrderManager):

    def init(self):
        if settings.DRY_RUN:
            logger.info("Initializing dry run. Orders printed below represent what would be posted to BitMEX.")
        else:
            logger.info("Order Manager initializing, connecting to BitMEX. Live run: executing real trades.")

        self.start_time = datetime.now()
        self.funding_rate = self.exchange.get_funding_rate(self.exchange.symbol)
        self.instrument = self.exchange.get_instrument()
        self.starting_qty = self.exchange.get_delta()
        self.running_qty = self.starting_qty
        # self.reset()

    def prepare_order(self, side, symbol=None):
        order = {}
        multi = settings.ORDER_MULTI
        symbol = symbol if symbol else self.exchange.symbol

        ticker = self.get_ticker(symbol)
        delta = self.exchange.get_delta(self.exchange.symbol)
        futures_delta = self.exchange.get_delta(self.exchange.futures_symbol)

        margin = self.exchange.get_margin()['withdrawableMargin']
        available_quantity = int(margin * multi)

        quantity = abs(delta + futures_delta)
        if not quantity and delta:
            quantity = min([abs(delta), available_quantity])
        elif not quantity and not delta:
            quantity = available_quantity
        price = ticker['sell'] + 0.5 if side == 'Sell' else ticker['buy'] - 0.5
        return {
            'side': side,
            'price': price,
            'orderQty': quantity,
        }

    def place_orders(self, symbol='XBTUSD', closing=False):
        """Create order items for use in convergence."""

        buy_orders = []
        sell_orders = []
        # Create orders from the outside in. This is intentional - let's say the inner order gets taken;
        # then we match orders from the outside in, ensuring the fewest number of orders are amended and only
        # a new order is created in the inside. If we did it inside-out, all orders would be amended
        # down and a new order would be created at the outside.
        logger.info("Get fundingRate")
        logger.info("Current Position: %.f, Funding Rate: %.6f" %
                    (self.exchange.get_delta(), self.funding_rate))

        # XBTUSD
        if symbol == self.exchange.symbol:
            if not self.long_position_limit_exceeded() and self.funding_rate < 0:
                buy_orders.append(self.prepare_order('Buy'))
            if not self.short_position_limit_exceeded() and self.funding_rate > 0:
                sell_orders.append(self.prepare_order('Sell'))
        # XBTM18
        elif symbol == self.exchange.futures_symbol:
            if not self.short_position_limit_exceeded() and self.funding_rate < 0:
               sell_orders.append(self.prepare_order('Sell'), symbol)
            if not self.long_position_limit_exceeded() and self.funding_rate > 0:
                buy_orders.append(self.prepare_order('Buy'), symbol)

        return self.converge_orders(buy_orders, sell_orders, symbol)
