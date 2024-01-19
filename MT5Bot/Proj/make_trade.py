import mt5_lib
import MetaTrader5
import helper_funcs as hlp


def make_trade(comment, symbol, take_profit, stop_loss):
    """
    Function to make a trade, when price signal is found
    :param comment: string comment
    :param symbol: string of symbol to trade
    :param take_profit: string or float of take profit price
    :param stop_loss: string or float of stop loss price
    :return: trade outcome
    """

    # todo: add in balance converter

    stop_loss = float(stop_loss)
    stop_loss = round(stop_loss, 5)

    take_profit = float(take_profit)
    take_profit = round(take_profit, 5)

    curr_price = MetaTrader5.symbol_info_tick(symbol).ask

    # Calculate lot size
    lot_size = hlp.calc_lot_size(
        stop_loss=stop_loss,
        symbol=symbol
    )

    # Determine order type
    if curr_price > stop_loss:
        #order_type = "BUY_STOP"
        order_type = "BUY"
    else:
        #order_type = "SELL_STOP"
        order_type = "SELL"

    # Send trade to MT5
    outcome = mt5_lib.place_order(
        order_type=order_type,
        symbol=symbol,
        volume=lot_size,
        stop_loss=stop_loss,
        take_profit=take_profit,
        comment=comment,
        direct=False
    )

    return outcome

