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
        self.instrument = self.exchange.get_instrument()
        self.starting_qty = self.exchange.get_delta()
        self.running_qty = self.starting_qty
        # self.reset()

    def prepare_reverse_order(self, side, symbol):
        ticker = self.get_ticker(symbol)
        quantity = settings.ORDER_START_SIZE
        price = ticker['sell'] + 0.5 if side == 'Buy' else ticker['buy'] - 0.5
        # Open oopsite futures order
        return {'price': price, 'orderQty': quantity, 'side': 'Sell' if side == 'Buy' else 'Buy'}

    def prepare_order(self, funding_rate, futures=None):
        symbol = self.exchange.symbol
        futures_symbol = self.exchange.futures_symbol
        order = {}
        if funding_rate < 0:
            order = self.prepare_reverse_order('Sell', symbol)
        elif funding_rate > 0:
            order = self.prepare_reverse_order('Buy', symbol)

        if funding_rate == 0 and futures:
            # reverse futures order
            order = self.prepare_reverse_order(futures, futures_symbol)
        if order:
            return order

    def place_orders(self, symbol='XBTUSD'):
        """Create order items for use in convergence."""

        buy_orders = []
        sell_orders = []
        # Create orders from the outside in. This is intentional - let's say the inner order gets taken;
        # then we match orders from the outside in, ensuring the fewest number of orders are amended and only
        # a new order is created in the inside. If we did it inside-out, all orders would be amended
        # down and a new order would be created at the outside.
        funding_rate = self.exchange.get_funding_rate(self.exchange.symbol)
        logger.info("Get fundingRate")
        logger.info("Current Position: %.f, Funding Rate: %.6f" %
                    (self.exchange.get_delta(), funding_rate))

        if symbol == self.exchange.symbol:
            if not self.long_position_limit_exceeded() and funding_rate < 0:
                buy_orders.append(self.prepare_order(funding_rate))
            if not self.short_position_limit_exceeded() and funding_rate > 0:
                sell_orders.append(self.prepare_order(funding_rate))
        #  open reverse futures
        elif symbol == self.exchange.futures_symbol:
            if not self.short_position_limit_exceeded() and funding_rate < 0:
               sell_orders.append(self.prepare_order(0, 'Buy'))
            if not self.long_position_limit_exceeded() and funding_rate > 0:
                buy_orders.append(self.prepare_order(0, 'Sell'))


        return self.converge_orders(buy_orders, sell_orders)
