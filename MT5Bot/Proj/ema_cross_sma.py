import mt5_lib
import MetaTrader5
import Indicators
import make_trade


def ema_cross_sma(symbol, timeframe, ema, sma):
    """
    Function which runs the EMA Cross SMA strategy
    :param symbol: string of the symbol to be queried
    :param timeframe: string timeframe to be queried
    :param ema: integer of the ema
    :param sma: integer of the sma
    :return: trade event dataframe
    """
    # 1. Retrieve Data
    # 2. Calculate Indicators
    # 3. Observe if trade event has occurred
    # 4. Check last trade
    # 5. If event has occured, place order

    ema_name = "ema_" + str(ema)
    sma_name = "sma_" + str(sma)
    cross_name = ema_name + "/Cross/" + sma_name

    data = get_data(
        symbol=symbol,
        timeframe=timeframe
    )

    data = calc_indicators(
        dataframe=data,
        ema=ema,
        sma=sma
    )

    data = det_trade(
        dataframe=data,
        ema=ema,
        sma=sma,
        symbol=symbol
    )

    last_signal = data.tail(1).copy()

    if last_signal[cross_name].values == 1.0 or last_signal[cross_name].values == -1.0:
        # Make Trade
        # Create Comment
        comment = cross_name + symbol
        make_trade_result = make_trade.make_trade(
            comment=comment,
            symbol=symbol,
            take_profit=last_signal["take_profit"].values,
            stop_loss=last_signal["stop_loss"].values,
        )
    else:
        make_trade_result = False

    return make_trade_result


def det_trade(dataframe, ema, sma, symbol):
    """
    Function to calculate trade signal for strategy on given data.
    1. For each trade, stop loss distance is 2 * ATR
    2. Always market order
    4. Take profit = price + 2.5 * ( 2 * ATR )
    :param dataframe: dataframe with data and indicators
    :param ema: integer of ema size
    :param sma: integer of sma size
    :param symbol: string of symbol being traded
    :return: dataframe object with trade events
    """

    ema_name = "ema_" + str(ema)
    sma_name = "sma_" + str(sma)
    cross_name = ema_name + "/Cross/" + sma_name

    if ema > sma:
        raise ValueError("EMA is less than SMA")
    elif ema == sma:
        raise ValueError("EMA and SMA values are the same")

    dataframe = dataframe.copy()
    dataframe = dataframe.reset_index()

    dataframe["take_profit"] = 0.0
    dataframe["stop_price"] = 0.0
    dataframe["stop_loss"] = 0.0

    # Iterate through data and observe trade signal
    for i in range(len(dataframe)):
        if i < sma:
            continue
        else:
            # Find when crossover is true
            if dataframe.loc[i, cross_name] == 1.0:
                # Calc Stop loss dist
                stop_loss_dist = dataframe.loc[i, "atr_14"]
                # Get Current Market Price
                market_price = MetaTrader5.symbol_info_tick(symbol).ask
                take_profit = market_price + (1.5 * stop_loss_dist)
                stop_loss = market_price - stop_loss_dist
            elif dataframe.loc[i, cross_name] == -1.0:
                # Calc Stop loss dist
                stop_loss_dist = dataframe.loc[i, "atr_14"]
                # Get Current Market Price
                market_price = MetaTrader5.symbol_info_tick(symbol).ask
                take_profit = market_price - (1.5 * stop_loss_dist)
                stop_loss = market_price + stop_loss_dist
            else:
                continue
            # Add values to dataframe
            dataframe.loc[i, "stop_loss"] = stop_loss
            dataframe.loc[i, "take_profit"] = take_profit
    return dataframe


def calc_indicators(dataframe, ema, sma, atr=14):
    """
    Function to calculate given indicators
    :param dataframe: dataframe object of candlestick data
    :param ema: integer value for ema size
    :param sma: integer value for sma size
    :param atr: integer value for atr size, default of 14
    :return: dataframe object
    """

    dataframe = Indicators.ema(
        dataframe=dataframe,
        ema_size=ema
    )

    dataframe = Indicators.sma(
        dataframe=dataframe,
        sma_size=sma
    )

    dataframe = Indicators.atr(
        dataframe=dataframe
    )

    ema_name = "ema_" + str(ema)
    sma_name = "sma_" + str(sma)

    dataframe = Indicators.crossover(
        dataframe=dataframe,
        indicator_one=ema_name,
        indicator_two=sma_name
    )

    return dataframe


def get_data(symbol, timeframe):
    """
    Function to retrieve candlestick data from MT5
    :param symbol: string of the symbol to be queried
    :param timeframe: string of the timeframe to be queried
    :return: dataframe object of candlestick data
    """

    data = mt5_lib.get_candlesticks(
        symbol=symbol,
        timeframe=timeframe,
        n_candles=1000
    )

    return data
