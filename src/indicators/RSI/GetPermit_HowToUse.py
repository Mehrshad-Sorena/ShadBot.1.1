from src.utils.DataReader.MetaTraderReader5.LoginGetData import LoginGetData as getdata
from .Parameters import Parameters
from .Config import Config
from .MACD import MACD
import pandas as pd



loging = getdata()
# loging.account_name = 'mehrshadpc'
# loging.initilizer()
# loging.login()


parameters = Parameters()
config = Config()

# ind_params = indicator_parameters()
# ind_config = indicator_config()



parameters.elements['dataset_5M'], parameters.elements['dataset_1H'] = loging.readall(symbol = 'XAUUSD_i', number_5M = 'all', number_1H = 'all')

parameters.elements['symbol'] = 'XAUUSD_i'
parameters.elements['RSI_apply_to'] = 'close'

print(parameters.elements['dataset_1H']['XAUUSD_i'])

rsi = RSI(parameters = parameters, config = config)
rsi_calc = rsi.GetPermit(
							dataset_5M = parameters.elements['dataset_5M'],
							dataset_1H = parameters.elements['dataset_1H'], 
							symbol = 'XAUUSD_i',
							signaltype = 'buy',
							signalpriority = 'primary',
							flag_savepic = False
						)