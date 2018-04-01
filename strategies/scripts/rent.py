from strategies.rent_strategy import logger, RentOrderManager


def run(*args):
    logger.info('BitMEX Market Maker Version:' )

    usd_manager = RentOrderManager(symbol='XBTUSD')
    m18_manager = RentOrderManager(symbol='XBTM18')
    # Try/except just keeps ctrl-c from printing an ugly stacktrace
    try:
        usd_manager.init()
        m18_manager.init()
        usd_manager.place_orders()
        m18_manager.place_orders()
        # om.run_loop()
        return usd_manager, m18_manager
    except (KeyboardInterrupt, SystemExit):
        sys.exit()
