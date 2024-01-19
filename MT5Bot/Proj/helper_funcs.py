import sys
import talib
from forex_python.converter import CurrencyRates
import pandas as pd
import MetaTrader5

import main
import mt5_lib


def check_package_imported(package_name):
    """
    Function to check if a given package is installed
    :param package_name: string of the package name to check
    :return: Boolean -> True if installed, False if not
    """
    if package_name in sys.modules:
        return True
    else:
        print(f"It is recommended that you install and import {package_name}")
        return False


def calc_lot_size(stop_loss, symbol):

    settings_filepath = "settings.json"
    proj_settings = main.get_settings(settings_filepath)["mt5"]

    account_info = MetaTrader5.account_info()._asdict()
    balance = account_info["margin_free"]

    perc_risk = proj_settings["perc_risk"]

    curr_price = round(MetaTrader5.symbol_info_tick(symbol).ask, 5)
    price_diff = round(abs(curr_price - stop_loss), 5)
    capital_at_risk = float(balance) * float(perc_risk)

    stop_loss_dist = price_diff / (MetaTrader5.symbol_info(symbol).point * 10)

    print("Calculating position size for: ", symbol)

    pip_value = get_pip_value(symbol)
    lot_size = (capital_at_risk / (stop_loss_dist * pip_value))

    lot_size = round(lot_size, 2)

    if lot_size >= 7.01:
        lot_size = 7
    return lot_size


def get_pip_value(symbol):
    symbol_info = MetaTrader5.symbol_info(symbol)
    point = symbol_info.point * 10
    exchange_rate = get_exchange_rate(symbol)
    return (point / exchange_rate) * 100000

def get_exchange_rate(symbol):
    symbol_info = MetaTrader5.symbol_info(symbol)
    return symbol_info.bid


# Broken for now
def print_open_orders():
    positions = MetaTrader5.positions_get()
    if positions is None:
        print("No orders, error code={}".format(MetaTrader5.last_error()))
    elif len(positions) > 0:
        print("Total Open Positions = {}".format(len(positions)))
        # display these positions as a table using pandas.DataFrame
        df = pd.DataFrame(list(positions), columns=positions[0]._asdict().keys())
        df["time"] = pd.to_datetime(df["time"], unit="s")
        df.drop(["time_update", "time_msc", "time_update_msc", "external_id", "ticket", "magic", "identifier", "reason", "swap"], axis=1, inplace=True)
        print(df)






