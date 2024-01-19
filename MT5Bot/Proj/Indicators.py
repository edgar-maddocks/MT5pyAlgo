import pandas as pd
import numpy as np
import talib

import helper_funcs as hlp

def ema(dataframe, ema_size):
    """
    Function that calcuates ema of given size.
    :param dataframe: dataframe object of candle data
    :param ema_size: size of ema
    :return: dataframe object
    """

    ema_size = ema_size if ema_size > 0 else 14
    ema_name = "ema_" + str(ema_size)

    if hlp.check_package_imported("talib") is True:
        try:
            dataframe[ema_name] = talib.EMA(dataframe["close"], ema_size)
            return dataframe
        except:
            pass

    smoothing = 2 / (ema_size + 1)

    # Calculate the inital mean value using standard SMA
    initial_mean = dataframe["close"].head(ema_size).mean()

    # Iterate through dataframe and calculate values
    for i in range(len(dataframe)):
        if i == ema_size:
            dataframe.loc[i, ema_name] = initial_mean
        elif i > ema_size:
            # Use EMA (Today) = Closing price x multiplier + EMA (previous day) x (1-multiplier)
            ema_value = (dataframe.loc[i, "close"] * smoothing) + (dataframe.loc[i - 1, ema_name] * (1 - smoothing))
            dataframe.loc[i, ema_name] = ema_value
        else:
            dataframe.loc[i, ema_name] = 0.0

    return dataframe


def sma(dataframe, sma_size):
    """
    Function that calculates SMA of given size
    :param dataframe: dataframe object of candlestick-like data
    :param sma_size: size of sma
    :return: dataframe object
    """

    sma_size = sma_size if sma_size > 0 else 14
    sma_name = "sma_" + str(sma_size)

    if hlp.check_package_imported("talib") is True:
        try:
            dataframe[sma_name] = talib.SMA(dataframe["close"], sma_size)
            return dataframe
        except:
            pass
    else:
        # Calculate initial mean
        initial_mean = dataframe["close"].head(sma_size).mean()

        # Iterate through and add values
        for i in range(len(dataframe)):
            if i == sma_size:
                dataframe.loc[i, sma_name] = initial_mean
            elif i > sma_size:
                dataframe.loc[i, sma_name] = dataframe.loc[i:i + sma_size, "close"].mean()
            else:
                dataframe.loc[i, sma_name] = 0.0

    return dataframe


def rsi(dataframe, rsi_length):
    """
    Function that calculates the RSI of a dataframe, of a given length
    :param dataframe: dataframe of candlestick-like data
    :param rsi_length: length of the rsi to use
    :return: dataframe object
    """
    rsi_length = rsi_length if rsi_length > 0 else 14
    rsi_name = "rsi_" + str(rsi_length)

    if hlp.check_package_imported("talib") is True:
        try:
            dataframe[rsi_name] = talib.RSI(dataframe["close"], rsi_length)
            return dataframe
        except:
            pass
    else:

        changes = dataframe["Close"].diff()

        gains = changes.copy()
        losses = changes.copy()

        gains[gains < 0] = 0
        losses[losses > 0] = 0

        avg_gain = gains.rolling(rsi_length).mean()
        avg_loss = losses.rolling(rsi_length).mean().abs()

        rsi = 100 - (100 / (1 + (avg_gain / avg_loss)))

        for i in range(len(dataframe)):
            if i >= rsi_length:
                dataframe.loc[i , rsi_name] = rsi.loc[i]
            else:
                dataframe.loc[i, rsi_name] = 0.0

    return dataframe


def atr(dataframe, atr_length=14):
    """
    A function to calculate the ATR and add it as a column to the dataframe
    :param dataframe:
    :param atr_length:
    :return:
    """

    atr_name = "atr_" + str(atr_length)

    if hlp.check_package_imported("talib") is True:
        try:
            high = dataframe["high"]
            low = dataframe["low"]
            close = dataframe["close"]
            dataframe[atr_name] = talib.ATR(high, low, close, timeperiod=atr_length)
            return dataframe
        except:
            pass
    else:
        dataframe = dataframe.copy()

        # Prepare 3 values to get real true range
        dataframe["tr0"] = abs(dataframe["high"] - dataframe["low"])
        dataframe["tr1"] = abs(dataframe["high"] - dataframe["close"].shift(1))
        dataframe["tr2"] = abs(dataframe["low"] - dataframe["close"].shift(1))

        # Calculate Real True Range
        tr = dataframe[['tr0', 'tr1', 'tr2']].max(axis=1)

        first_atr = dataframe["tr"].tail(atr_length).mean()

        for i in range(len(dataframe)):
            if i == 0:
                dataframe.loc[i, atr_name] = first_atr
            elif i > 0:
                dataframe.loc[i, atr_name] = (dataframe[atr_name].shift() * (atr_length - 1) + dataframe.loc[i, "tr"]) / atr_length

        return dataframe


def crossover(dataframe, indicator_one, indicator_two):
    """
    Function to calculate crossover between two given indicators
    :param dataframe: dataframe object of candlestick like data - should include indicators being evaluated
    :param indicator_one: name of first indicator column
    :param indicator_two: name of second indicator column
    :return: dataframe object with cross events
    """
    dataframe["crossover_is_bullish"] = 0.0

    dataframe["crossover_is_bullish"] = np.where(dataframe[indicator_one] > dataframe[indicator_two], 1.0, 0.0)

    cross_name = f"{indicator_one}/Cross/{indicator_two}"

    dataframe[cross_name] = dataframe["crossover_is_bullish"].diff()
    # Drop NA values
    dataframe.dropna(inplace=True)
    # Create crossover column
    dataframe.drop(columns="crossover_is_bullish", inplace=True)

    return dataframe


def AutoSnR(dataframe, perc_deviation, move_start_level):
    """
    Function to find the nearest support and Resistance Levels to the current price
    :param dataframe: dataframe of candlestick-like data
    :param perc_deviation: % of previous close to use as distance from the start level for other levels (.5% recommended - 0.0005)
    :param move_start_level: move start level up or down - for when market has had major shift
    :return: dataframe object
    """
    start_level = dataframe.Close[-2] * (1 + move_start_level)

    deviation_amount = start_level - (start_level * (1 - perc_deviation))
    if dataframe.Close[-1] > start_level:
        deviation_amount = (start_level * (1 + perc_deviation)) - start_level

    support_level1 = start_level - deviation_amount
    resistance_level1 = start_level + deviation_amount
    support_level2 = start_level - (2 * deviation_amount)
    resistance_level2 = start_level + (2 * deviation_amount)
    support_level3 = start_level - (3 * deviation_amount)
    resistance_level3 = start_level + (3 * deviation_amount)
    support_level4 = start_level - (4 * deviation_amount)
    resistance_level4 = start_level + (4 * deviation_amount)
    support_level5 = start_level - (5 * deviation_amount)
    resistance_level5 = start_level + (5 * deviation_amount)

    close = dataframe.Close[-1]

    res_level = 0
    sup_level = 0

    if start_level < close < resistance_level1:
        res_level = resistance_level1
        sup_level = start_level
    elif resistance_level1 < close < resistance_level2:
        res_level = resistance_level2
        sup_level = resistance_level1
    elif resistance_level2 < close < resistance_level3:
        res_level = resistance_level3
        sup_level = resistance_level2
    elif resistance_level3 < close < resistance_level4:
        res_level = resistance_level4
        sup_level = resistance_level3
    elif resistance_level4 < close < resistance_level5:
        res_level = resistance_level5
        sup_level = resistance_level4
    elif start_level > close > support_level1:
        res_level = start_level
        sup_level = support_level1
    elif support_level1 > close > support_level2:
        res_level = support_level1
        sup_level = support_level2
    elif support_level2 > close > support_level3:
        res_level = support_level2
        sup_level = support_level3
    elif support_level3 > close > support_level4:
        res_level = support_level3
        sup_level = support_level4
    elif support_level4 > close > support_level5:
        res_level = support_level4
        sup_level = support_level5

    priceDiffRes = (close - support_level4) / close * -100
    priceDiffSup = (support_level5 - close) / support_level4 * -100

    dataframe = dataframe.copy()
    dataframe.loc["support_level"] = sup_level
    dataframe.loc["resistance_level"] = res_level










