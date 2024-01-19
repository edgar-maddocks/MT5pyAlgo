import json
import os

import MetaTrader5
import pandas as pd
import time

import helper_funcs
import mt5_lib
import ema_cross_sma
import helper_funcs as hlp

settings_filepath = "settings.json"
EMACrossSMAparams_filepath = "EMACrossSMAoptimize.json"
# Import data from settings.json


def get_settings(filepath):
    """
    Get settings from settings.json
    :param filepath: file path to settings.json
    :return: Dictionary of settings
    """

    # If path exists, get the settings
    if os.path.exists(filepath):
        fh = open(filepath)
        proj_settings = json.load(fh)
        fh.close()
        return proj_settings
    else:
        raise ImportError(f"{filepath} does not exist")


def get_params(filepath):
    """
    Get settings from settings.json
    :param filepath: file path to settings.json
    :return: Dictionary of settings
    """

    # If path exists, get the settings
    if os.path.exists(filepath):
        fh = open(filepath)
        params = json.load(fh)
        fh.close()
        return params
    else:
        raise ImportError(f"{filepath} does not exist")


def start_up(proj_settings):
    """
    Start up procedures when starting MT5, initializing symbols etc.
    :param proj_settings: Json of settings
    :return: Boolean -> True = successful startup, False = failed startup
    """
    # Start MT5
    startup = mt5_lib.start_mt5(proj_settings=proj_settings)
    # Get symbols from settings
    symbols = proj_settings["mt5"]["symbols"]
    # Iterate through symbols, and initialize each
    for sym in symbols:
        outcome = mt5_lib.symbol_init(symbol=sym)
        if outcome:
            print(f"{sym} has been initialized")
        else:
            raise Exception (f"Error initializing {sym}")
    # inform user of successful startup
    if startup:
        print("MT5 started successfully")
        return True

    return False


def run_strategy(proj_settings):
    """
    Function to run the strategy for the trading bot
    :param proj_settings: JSON of project settings
    :return: Boolean, strategy ran with no errors = True
    """
    symbols = proj_settings["mt5"]["symbols"]
    timeframe = proj_settings["mt5"]["timeframe"]

    for sym in symbols:
        params = get_params(EMACrossSMAparams_filepath)["params"][sym]

        candlesticks = mt5_lib.get_candlesticks(
            symbol=sym,
            timeframe=timeframe,
            n_candles=10000
        )

        data = ema_cross_sma.ema_cross_sma(
            symbol=sym,
            timeframe=proj_settings["mt5"]["timeframe"],
            ema=params["EMA"],
            sma=params["SMA"]
        )
        if data is False:
            print(f"No Trade on {sym} was made")

    print("----------OPEN POSITIONS----------")
    helper_funcs.print_open_orders()
    print("----------------------------------")

    return True


if __name__ == '__main__':
    # Get Settings
    proj_settings = get_settings(filepath=settings_filepath)
    # Start up MT5 and initialize symbols
    startup = start_up(proj_settings=proj_settings)
    # Get dataframe of candles for each symbol

    # Display all columns in pandas
    pd.set_option("display.max_columns", None)
    # Setup loop to trade strategy, if startup is successful
    if startup:
        timeframe = proj_settings["mt5"]["check_for_trade_timeframe"]
        current_time = 0
        previous_time = 0
        totalmins = 0
        while True:
            # Get current time using BTCUSD as it trades 24/7.
            time_candle = mt5_lib.get_candlesticks(
                symbol="BTCUSD",
                timeframe=timeframe,
                n_candles=1
            )
            current_time = time_candle["time"][0]
            if current_time != previous_time:
                print("New Candle Available")
                previous_time = current_time
                totalmins = 0
                strategy = run_strategy(proj_settings=proj_settings)
            else:
                sleep_time = 5
                totalmins += sleep_time / 60
                print(f"No new candle -> Sleeping for {sleep_time}. Total mins pass: {totalmins}")
                time.sleep(sleep_time)






