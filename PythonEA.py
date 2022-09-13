import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime
import time


#function to send market order
def market_order(symbol, volume, order_type,**kwargs):
    tick = mt5.symbol_info_tick(symbol)

    order_dict = {'buy': 0, 'sell': 1}
    price_dict = {'buy': tick.ask, 'sell': tick.bid}

    request = {
        'action': mt5.TRADE_ACTION_DEAL,
        'symbol': symbol,
        'volume': volume,
        'type': order_dict[order_type],
        'price': price_dict[order_type],
        'deviation': DEVIATION,
        'magic': 100,
        'comment': 'Python market order',
        'type_time': mt5.ORDER_TIME_GTC,
        'type_filling': mt5.ORDER_FILLING_IOC,
    }

    order_result = mt5.order_send(request)
    print(order_result)

    return order_result

# Function to close orders based on DON ID
def close_order(ticket):
    positions = mt5.positions_get()

    for pos in positions:
        tick = mt5.symbol_info_tick(pos.symbol)

        type_dict = {0: 1, 1: 0} # It's the opposite of the open orders, to close them.
        price_dict = {0: tick.ask, 1: tick.bid}

        if pos.ticket == ticket:
            request = {
                'action': mt5.TRADE_ACTION_DEAL,
                'position': pos.ticket,
                'symbol': pos.symbol,
                'volume': pos.volume,
                'type': type_dict[pos.type],
                'price': price_dict[pos.type],
                'deviation': DEVIATION,
                'magic': 100,
                'comment': 'Python close order',
                'type_time': mt5.ORDER_TIME_GTC,
                'type_filling': mt5.ORDER_FILLING_IOC,
            }

            order_result = mt5.order_send(request)
            print(order_result)

            return order_result

    return 'Ticket does not exist'

# Function to check how exposed I am with all my open positions
def get_exposure(symbol):
    positions = mt5.positions_get(symbol=symbol)
    if positions:
        pos_df = pd.DataFrame(positions, columns=positions[0]._asdict().keys())
        exposure = pos_df['volume'].sum()

# Function to look for trading signals
def signal(symbol, timeframe, sma_period):
    bars = mt5.copy_rates_from_pos(symbol, timeframe, 1, sma_period)
    bars_df = pd.DataFrame(bars)

    last_close = bars_df.iloc[-1].close
    sma = bars_df.close.mean()

    direction = 'flat'
    if last_close > sma:
        direction = 'buy'
    elif last_close < sma:
        direction = 'sell'

    return last_close, sma, direction


if __name__ == '__main__':

    # Strategy parameters

    SYMBOL = 'EURUSD'
    VOLUME = 0.1
    TIMEFRAME = mt5.TIMEFRAME_M5
    SMA_PERIOD = 21
    DEVIATION = 20

    mt5.initialize()

    while True:
        #Calculating the account exposure
        exposure = get_exposure(SYMBOL)

        # Calculate last candle close and SMA and checking for a signal
        last_close, sma, direction = signal(SYMBOL, TIMEFRAME, SMA_PERIOD)

        #Trading logic
        if direction == 'buy':
            #if we have a buy signal close all the SHORT positions
            for pos in mt5.positions_get():
                if pos.type == 1:    #Type 1 is SELL
                    close_order(pos.ticket)

            # If there are no positions, open a new BUY position
            if not mt5.positions_total():
                market_order(SYMBOL, VOLUME, direction)

        elif direction == 'sell':
            # if we have a SELL signal, close all the LONG positions
            for pos in mt5.positions_get():
                if pos.type == 0:  #Type 0 is BUY
                    close_order(pos.ticket)

            # If there are no positions, open a new SELL position
            if not mt5.positions_total():
                market_order(SYMBOL, VOLUME, direction)

        print('time: ', datetime.now())
        print('exposure: ', exposure)
        print('last close: ', last_close)
        print('sma: ', sma)
        print('signal: ', direction)
        print('-----------\n')

        #Update every 10 seconds

        time.sleep(10)

