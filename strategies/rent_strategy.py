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

    def prepare_order(self, funding_rate):
        ticker = self.get_ticker()
        if settings.RANDOM_ORDER_SIZE is True:
            quantity = random.randint(settings.MIN_ORDER_SIZE, settings.MAX_ORDER_SIZE)
        else:
            quantity = settings.ORDER_START_SIZE

        price = ticker['buy'] if funding_rate < 0 else ticker['sell']
        return {'price': price, 'orderQty': quantity, 'side': "Buy" if funding_rate < 0 else "Sell"}

    def place_orders(self):
        """Create order items for use in convergence."""

        buy_orders = []
        sell_orders = []
        # Create orders from the outside in. This is intentional - let's say the inner order gets taken;
        # then we match orders from the outside in, ensuring the fewest number of orders are amended and only
        # a new order is created in the inside. If we did it inside-out, all orders would be amended
        # down and a new order would be created at the outside.
        funding_rate = self.exchange.get_funding_rate()
        logger.info("Get fundingRate")
        logger.info("Current Position: %.f, Funding Rate: %.6f" %
                    (self.exchange.get_delta(), funding_rate))

        if not self.long_position_limit_exceeded() and funding_rate > 0:
            buy_orders.append(self.prepare_order(funding_rate))
        if not self.short_position_limit_exceeded() and funding_rate < 0:
            sell_orders.append(self.prepare_order(funding_rate))

        return self.converge_orders(buy_orders, sell_orders)
