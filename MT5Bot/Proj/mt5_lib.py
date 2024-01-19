import MetaTrader5
import pandas as pd


def start_mt5(proj_settings):
    """
    Function to start MetaTrader5
    :param proj_settings: Json with user settings, username, password, server, path, symbols, timeframe
    :return: Boolean - True = successful start, False = failed to start
    """
    # Bring in data from settings.json and format to correct data type
    username = proj_settings["mt5"]["username"]
    username = int(username)
    password = proj_settings["mt5"]["password"]
    server = proj_settings["mt5"]["server"]
    mt5_pathway = proj_settings["mt5"]["mt5_pathway"]

    # Try to open MT5

    mt5_init = False
    try:
        mt5_init = MetaTrader5.initialize(
            path=mt5_pathway,
            login=username,
            password=password,
            server=server
        )
    except Exception as e:
        print(f"Error initalizing MT5: {e}")
        mt5_init = False

    # If initialized, attempt to login

    mt5_login = False
    try:
        mt5_login = MetaTrader5.login(
            login=username,
            password=password,
            server=server
        )
    except Exception as e:
        print(f"Error logging into MT5: {e}")
        mt5_login = False

    if mt5_login:
        return True

    return False


def symbol_init(symbol):
    """
    Function to initialize symbol
    :param symbol: string of symbol
    :return: True if successful, False if not
    """
    all_symbols = MetaTrader5.symbols_get()

    symbol_names = []
    # Create List of symbol names
    for sym in all_symbols:
        symbol_names.append(sym.name)

    # If symbol exists, initialize the symbol
    if symbol in symbol_names:
        try:
            MetaTrader5.symbol_select(symbol, True)
            return True
        except Exception as e:
            print(f"Error initializing symbol {symbol}. Error: {e}")
            return False
    else:
        print(f"Symbol {symbol} does not exist")


def get_candlesticks(symbol, timeframe, n_candles=50000):
    """
    Function that gets candlestick data from MT5.
    :param symbol: string of the symbol to be retrieved
    :param timeframe: string of the timerframe to be retrieved
    :param n_candles: integer number of candles to be retrieved. Upper bound of 50000
    :return: dataframe of candles
    """
    if n_candles > 50000:
        raise ValueError("Number of candles cannot exceed 50000")
    mt5_timeframe = set_query_timeframe(timeframe)

    candles = MetaTrader5.copy_rates_from_pos(
        symbol,
        mt5_timeframe,
        1,
        n_candles
    )

    data = pd.DataFrame(candles)
    return data


def set_query_timeframe(timeframe):
    """
    Switch user-friendly inputs to MT5 timeframe.
    :param timeframe: string of timeframe
    :return: MT5 timerframe object
    """

    if timeframe == "M1":
        return MetaTrader5.TIMEFRAME_M1
    elif timeframe == "M2":
        return MetaTrader5.TIMEFRAME_M2
    elif timeframe == "M3":
        return MetaTrader5.TIMEFRAME_M3
    elif timeframe == "M4":
        return MetaTrader5.TIMEFRAME_M4
    elif timeframe == "M5":
        return MetaTrader5.TIMEFRAME_M5
    elif timeframe == "M6":
        return MetaTrader5.TIMEFRAME_M6
    elif timeframe == "M10":
        return MetaTrader5.TIMEFRAME_M10
    elif timeframe == "M12":
        return MetaTrader5.TIMEFRAME_M12
    elif timeframe == "M15":
        return MetaTrader5.TIMEFRAME_M15
    elif timeframe == "M20":
        return MetaTrader5.TIMEFRAME_M20
    elif timeframe == "M30":
        return MetaTrader5.TIMEFRAME_M30
    elif timeframe == "H1":
        return MetaTrader5.TIMEFRAME_H1
    elif timeframe == "H2":
        return MetaTrader5.TIMEFRAME_H2
    elif timeframe == "H3":
        return MetaTrader5.TIMEFRAME_H3
    elif timeframe == "H4":
        return MetaTrader5.TIMEFRAME_H4
    elif timeframe == "H6":
        return MetaTrader5.TIMEFRAME_H6
    elif timeframe == "H8":
        return MetaTrader5.TIMEFRAME_H8
    elif timeframe == "H12":
        return MetaTrader5.TIMEFRAME_H12
    elif timeframe == "D1":
        return MetaTrader5.TIMEFRAME_D1
    elif timeframe == "W1":
        return MetaTrader5.TIMEFRAME_W1
    elif timeframe == "MN1":
        return MetaTrader5.TIMEFRAME_MN1
    else:
        print(f"Incorrect timeframe provided. {timeframe}")
        raise ValueError("Input the correct timeframe")


def place_order(order_type, symbol, volume, stop_loss, take_profit, comment, direct=False):
    """
    Function to place order in MT5, upon checking order first
    :param order_type: string - either SELL_STOP or BUY_STOP
    :param symbol: string of the symbol to be traded
    :param volume: string or float of the volume to be traded
    :param stop_loss: string or float of stop loss price
    :param take_profit: string or float of take profit price
    :param comment: string of the comment, to track order
    :param direct: Bool, default false. If True -> bypasses check
    :return: Trade Outcome
    """

    volume = float(volume)
    volume = round(volume, 2)

    stop_loss = float(stop_loss)
    stop_loss = round(stop_loss, 4)

    take_profit = float(take_profit)
    take_profit = round(take_profit, 4)

    # Create order dictionary to pass to MT5

    order_request = {
        "symbol": symbol,
        "volume": volume,
        "sl": stop_loss,
        "tp": take_profit,
        "type_time": MetaTrader5.ORDER_TIME_DAY,
        "comment": comment
    }

    # Set order type for the request and update request params
    # if order_type == "SELL_STOP":
    if order_type == "SELL":
        # order_request["type"] = MetaTrader5.ORDER_TYPE_SELL_STOP
        order_request["type"] = MetaTrader5.ORDER_TYPE_SELL
        # order_request["action"] = MetaTrader5.TRADE_ACTION_PENDING
        order_request["action"] = MetaTrader5.TRADE_ACTION_DEAL
        # order_request["type_filling"] = MetaTrader5.ORDER_FILLING_RETURN
        order_request["type_filling"] = MetaTrader5.ORDER_FILLING_IOC
        # if stop_price <= 0:
        #     raise ValueError("Stop price is less than or equal to 0")
        # elif stop_price > MetaTrader5.symbol_info_tick(symbol).ask:
        #     order_request["price"] = MetaTrader5.symbol_info_tick(symbol).ask
        # else:
        #     order_request["price"] = stop_price
    # elif order_type == "BUY_STOP":
    elif order_type == "BUY":
        # order_request["type"] = MetaTrader5.ORDER_TYPE_BUY_STOP
        order_request["type"] = MetaTrader5.ORDER_TYPE_BUY
        # order_request["action"] = MetaTrader5.TRADE_ACTION_PENDING
        order_request["action"] = MetaTrader5.TRADE_ACTION_DEAL
        # order_request["type_filling"] = MetaTrader5.ORDER_FILLING_RETURN
        order_request["type_filling"] = MetaTrader5.ORDER_FILLING_IOC
        # if stop_price <= 0:
        #     raise ValueError("Stop price is less than or equal to 0")
        # elif stop_price < MetaTrader5.symbol_info_tick(symbol).ask:
        #     order_request["price"] = MetaTrader5.symbol_info_tick(symbol).ask
        # else:
        #     order_request["price"] = stop_price
    else:
        raise ValueError(f"Unsupported order type: {order_type}")

    if direct:
        # Skip check and send order
        order_result = MetaTrader5.order_send(order_request)
        # Check for known errors
        if order_result[0] == 10009:
            print(f"Order for {symbol} successful")
            return True
        elif order_result[0] == 10027:
            print("Turn off AlgoTrading on MT5 Terminal")
            raise Exception("Turn off Algo Trading on MT5 Terminal")
        elif order_result[0] == 10016:
            print(f"Invalid stops for {symbol}. Stop Loss: {stop_loss}")
        elif order_result[0] == 10014:
            print(f"Invalid volume for {symbol}. Volume: {volume}")
            # Give default error response
        else:
            print(f"Error placing order for {symbol}. Error code: {order_result[0]}. Order Details: {order_result}")
            raise Exception(f"Unknown error lodging order for {symbol}")
    else:
        check_result = MetaTrader5.order_check(order_request)
        # If check passes, place an order
        if check_result[0] == 0:
            print(f"Order check for {symbol} successful. Placing order.")
            # Place the order using recursion
            place_order(
                order_type=order_type,
                symbol=symbol,
                volume=volume,
                stop_loss=stop_loss,
                take_profit=take_profit,
                comment=comment,
                direct=True
            )
        else:
            print(f"Order check failed. Details: {check_result}")



