from src.utils.DataReader.MetaTraderReader5.LoginGetData import LoginGetData as getdata

from src.indicators.StochAstic.StochAstic import StochAstic
from src.indicators.StochAstic.Parameters import Parameters as StochAsticParameters
from src.indicators.StochAstic.Config import Config as StochAsticConfig

from src.indicators.MACD.MACD import MACD
from src.indicators.MACD.Parameters import Parameters as MacdParameters
from src.indicators.MACD.Config import Config as MacdConfig

from src.indicators.RSI.RSI import RSI
from src.indicators.RSI.Parameters import Parameters as RsiParameters
from src.indicators.RSI.Config import Config as RsiConfig

import pandas as pd
import numpy as np

import os

symbol = 'XAUUSD_i'
applyto = 'close'
number_data_5M = 'all'
number_data_1H = 'all'
start_point = 4000
coef_money = 20
money = 100
spred = 0.00045
percent = 0
tp_pr_eq = 0
st_pr_eq = 0


def BuyChecker(dataset_5M_real, tp, st, candle_index, money, coef_money, spred):

	if (
		dataset_5M_real['high'][candle_index] * (1 + spred) >= tp or
		dataset_5M_real['low'][candle_index] <= st
		):
		flag = 'no_flag'
		tp_pr = 0
		st_pr = 0

		return money, flag, tp_pr, st_pr, candle_index

	if (len(np.where(((dataset_5M_real['high'][(candle_index):-1].values) >= tp))[0]) > 1):
			index_tp =	candle_index + min(
											np.where(
														(
															(dataset_5M_real['high'][(candle_index):-1].values) >= tp
														)
													)[0] 
											)

	elif (len(np.where(((dataset_5M_real['high'][(candle_index):-1].values) >= tp))[0]) == 1):
		index_tp =	candle_index + np.where(
												(
													(dataset_5M_real['high'][(candle_index):-1].values) >= tp
												)
											)[0][0] 

	else:
		index_tp = -1
		tp_pr = 0

	if (len(np.where(((dataset_5M_real['low'][(candle_index):-1].values) <= st))[0]) > 1):
		index_st =	candle_index + min(
									np.where(
												(
													(dataset_5M_real['low'][(candle_index):-1].values) <= st
												)
											)[0]
									)

	elif (len(np.where(((dataset_5M_real['low'][(candle_index):-1].values) <= st))[0]) == 1):
		index_st =	candle_index + np.where(
											(
												(dataset_5M_real['low'][(candle_index):-1].values) <= st
											)
										)[0][0]

	else:
		index_st = -1
		st_pr = 0

	loc_end_5M_price = candle_index
	if (
		index_tp < index_st and
		index_tp != -1
		):

		st_pr = ((dataset_5M_real['low'][loc_end_5M_price] - np.min(dataset_5M_real['low'][loc_end_5M_price:index_tp]))/dataset_5M_real['low'][loc_end_5M_price]) * 100
		tp_pr = ((dataset_5M_real['high'][index_tp] - dataset_5M_real['high'][loc_end_5M_price]*(1 + spred))/(dataset_5M_real['high'][loc_end_5M_price] * (1 + spred))) * 100

		if dataset_5M_real['high'][index_tp] > tp: tp_pr = ((tp - dataset_5M_real['high'][loc_end_5M_price]*(1 + spred))/(dataset_5M_real['high'][loc_end_5M_price] * (1 + spred))) * 100

		my_money = money

		if my_money >=100:
			lot = int(my_money/100) * coef_money
		else:
			lot = coef_money

		if lot > 2000: lot = 2000

		my_money = my_money + (lot * tp_pr)

		money = my_money

		candle_index = index_tp

		flag = 'tp'

	elif (
		index_tp != -1 and
		index_st == -1
		):
		st_pr = ((dataset_5M_real['low'][loc_end_5M_price] - np.min(dataset_5M_real['low'][loc_end_5M_price:index_tp]))/dataset_5M_real['low'][loc_end_5M_price]) * 100
		tp_pr = ((dataset_5M_real['high'][index_tp] - dataset_5M_real['high'][loc_end_5M_price]*(1 + spred))/(dataset_5M_real['high'][loc_end_5M_price] * (1 + spred))) * 100

		if dataset_5M_real['high'][index_tp] > tp: tp_pr = ((tp - dataset_5M_real['high'][loc_end_5M_price]*(1 + spred))/(dataset_5M_real['high'][loc_end_5M_price] * (1 + spred))) * 100


		my_money = money

		if my_money >=100:
			lot = int(my_money/100) * coef_money
		else:
			lot = coef_money

		if lot > 2000: lot = 2000

		my_money = my_money + (lot * tp_pr)

		money = my_money

		candle_index = index_tp

		flag = 'tp'

	elif (
		index_st < index_tp and
		index_st != -1
		):
		st_pr = ((dataset_5M_real['low'][loc_end_5M_price] - dataset_5M_real['low'][index_st])/dataset_5M_real['low'][loc_end_5M_price]) * 100
		tp_pr = ((np.max(dataset_5M_real['high'][loc_end_5M_price:index_st]) - dataset_5M_real['high'][loc_end_5M_price]*(1 + spred))/(dataset_5M_real['high'][loc_end_5M_price] * (1 + spred))) * 100

		if dataset_5M_real['low'][index_st] < st: st_pr = ((dataset_5M_real['low'][loc_end_5M_price] - st)/dataset_5M_real['low'][loc_end_5M_price]) * 100

		my_money = money

		if my_money >=100:
			lot = int(my_money/100) * coef_money
		else:
			lot = coef_money

		if lot > 2000: lot = 2000

		my_money = my_money - (lot * st_pr)

		money = my_money

		candle_index = index_st

		flag = 'st'

	elif (
		index_tp == -1 and
		index_st != -1
		):
		st_pr = ((dataset_5M_real['low'][loc_end_5M_price] - dataset_5M_real['low'][index_st])/dataset_5M_real['low'][loc_end_5M_price]) * 100
		tp_pr = ((np.max(dataset_5M_real['high'][loc_end_5M_price:index_st]) - dataset_5M_real['high'][loc_end_5M_price]*(1 + spred))/(dataset_5M_real['high'][loc_end_5M_price] * (1 + spred))) * 100
		
		if dataset_5M_real['low'][index_st] < st: st_pr = ((dataset_5M_real['low'][loc_end_5M_price] - st)/dataset_5M_real['low'][loc_end_5M_price]) * 100

		my_money = money
		coef_money = self.elements['Tester_coef_money']

		if my_money >=100:
			lot = int(my_money/100) * coef_money
		else:
			lot = coef_money

		if lot > 2000: lot = 2000

		my_money = my_money - (lot * st_pr)

		money = my_money

		candle_index = index_st

		flag = 'st'

	if index_st == index_tp:

		if index_st != -1:
			st_pr = ((dataset_5M_real['low'][loc_end_5M_price] - dataset_5M_real['low'][index_st])/dataset_5M_real['low'][loc_end_5M_price]) * 100
			tp_pr = ((np.max(dataset_5M_real['high'][loc_end_5M_price:index_st]) - dataset_5M_real['high'][loc_end_5M_price]*(1 + spred))/(dataset_5M_real['high'][loc_end_5M_price] * (1 + spred))) * 100
			
			if dataset_5M_real['low'][index_st] < st: st_pr = ((dataset_5M_real['low'][loc_end_5M_price] - st)/dataset_5M_real['low'][loc_end_5M_price]) * 100

			my_money = money
			coef_money = self.elements['Tester_coef_money']

			if my_money >=100:
				lot = int(my_money/100) * coef_money
			else:
				lot = coef_money

			if lot > 2000: lot = 2000

			my_money = my_money - (lot * st_pr)

			money = my_money

			candle_index = index_st

			flag = 'st'

		else:
			flag = 'no_flag'
			tp_pr = 0
			st_pr = 0

	return money, flag, tp_pr, st_pr, candle_index

def SellChecker(dataset_5M_real, tp, st, candle_index, money, coef_money, spred):

	loc_end_5M_price = candle_index

	if (
		dataset_5M_real['high'][loc_end_5M_price] * (1 + spred) >= st or
		dataset_5M_real['low'][loc_end_5M_price] <= tp 
		):

		flag = 'no_flag'
		tp_pr = 0
		st_pr = 0

		return money, flag, tp_pr, st_pr, candle_index

	

	#*************** Finding Take Profit:

	if (len(np.where(((dataset_5M_real['low'][(loc_end_5M_price):-1].values * (1 + spred)) <= tp))[0]) > 1):
		index_tp =	loc_end_5M_price + min(
									np.where(
												(
													(dataset_5M_real['low'][(loc_end_5M_price):-1].values) * (1 + spred) <= tp
												)
											)[0] 
									)

	elif (len(np.where(((dataset_5M_real['low'][(loc_end_5M_price):-1].values * (1 + spred)) <= tp))[0]) == 1):
		index_tp =	loc_end_5M_price + np.where(
											(
												(dataset_5M_real['low'][(loc_end_5M_price):-1].values * (1 + spred)) <= tp
											)
										)[0][0] 

	else:
		index_tp = -1
		tp_pr = 0
	#///////////////////////////////

	#************ Finding Stop Loss:

	if (len(np.where(((dataset_5M_real['high'][(loc_end_5M_price):-1].values * (1 + spred)) >= st))[0]) > 1):
		index_st =	loc_end_5M_price + min(
									np.where(
												(
													(dataset_5M_real['high'][(loc_end_5M_price):-1].values * (1 + spred)) >= st
												)
											)[0]
									)

	elif (len(np.where(((dataset_5M_real['high'][(loc_end_5M_price):-1].values * (1 + spred)) >= st))[0]) == 1):
		index_st =	loc_end_5M_price + np.where(
											(
												(dataset_5M_real['high'][(loc_end_5M_price):-1].values * (1 + spred)) >= st
											)
										)[0][0]

	else:
		index_st = -1
		st_pr = 0

	if (
		index_tp < index_st and
		index_tp != -1
		):

		st_pr = ((np.max(dataset_5M_real['high'][loc_end_5M_price:index_tp]) - dataset_5M_real['high'][loc_end_5M_price])/dataset_5M_real['high'][loc_end_5M_price]) * 100
		tp_pr = ((dataset_5M_real['low'][loc_end_5M_price] - dataset_5M_real['low'][index_tp] * (1 + spred))/(dataset_5M_real['low'][loc_end_5M_price])) * 100

		if dataset_5M_real['low'][index_tp] < tp: tp_pr = ((dataset_5M_real['low'][loc_end_5M_price] - tp * (1 + spred))/(dataset_5M_real['low'][loc_end_5M_price])) * 100

		my_money = money

		if my_money >=100:
			lot = int(my_money/100) * coef_money
		else:
			lot = coef_money

		if lot > 2000: lot = 2000

		my_money = my_money + (lot * tp_pr)

		money = my_money

		candle_index = index_tp

		# print('tp = ', top_prim, ' ', down_prim)

		flag = 'tp'

	elif (
		index_tp != -1 and
		index_st == -1
		):
		st_pr = ((np.max(dataset_5M_real['high'][loc_end_5M_price:index_tp]) - dataset_5M_real['high'][loc_end_5M_price])/dataset_5M_real['high'][loc_end_5M_price]) * 100
		tp_pr = ((dataset_5M_real['low'][loc_end_5M_price] - dataset_5M_real['low'][index_tp] * (1 + spred))/(dataset_5M_real['low'][loc_end_5M_price])) * 100

		if dataset_5M_real['low'][index_tp] < tp: tp_pr = ((dataset_5M_real['low'][loc_end_5M_price] - tp * (1 + spred))/(dataset_5M_real['low'][loc_end_5M_price])) * 100

		my_money = money

		if my_money >=100:
			lot = int(my_money/100) * coef_money
		else:
			lot = coef_money

		if lot > 2000: lot = 2000

		my_money = my_money + (lot * tp_pr)

		money = my_money

		candle_index = index_tp

		# print('tp = ', top_prim, ' ', down_prim)

		flag = 'tp'

	elif (
		index_st < index_tp and
		index_st != -1
		):
		st_pr = ((dataset_5M_real['high'][index_st] - dataset_5M_real['high'][loc_end_5M_price])/dataset_5M_real['high'][loc_end_5M_price]) * 100
		tp_pr = ((dataset_5M_real['low'][loc_end_5M_price] - np.min(dataset_5M_real['low'][loc_end_5M_price:index_st]) * (1 + spred))/(dataset_5M_real['low'][loc_end_5M_price])) * 100
		
		if dataset_5M_real['high'][index_st] > st: st_pr = ((st - dataset_5M_real['high'][loc_end_5M_price])/dataset_5M_real['high'][loc_end_5M_price]) * 100

		my_money = money

		if my_money >=100:
			lot = int(my_money/100) * coef_money
		else:
			lot = coef_money

		if lot > 2000: lot = 2000

		my_money = my_money - (lot * st_pr)

		money = my_money

		candle_index = index_st

		# print('st = ', signals['pattern_day'][loc_end_5M], ' ', signals['time_high_front'][loc_end_5M].hour)

		flag = 'st'

	elif (
		index_tp == -1 and
		index_st != -1
		):
		st_pr = ((dataset_5M_real['high'][index_st] - dataset_5M_real['high'][loc_end_5M_price])/dataset_5M_real['high'][loc_end_5M_price]) * 100
		tp_pr = ((dataset_5M_real['low'][loc_end_5M_price] - np.min(dataset_5M_real['low'][loc_end_5M_price:index_st]) * (1 + spred))/(dataset_5M_real['low'][loc_end_5M_price])) * 100
		
		if dataset_5M_real['high'][index_st] > st: st_pr = ((st - dataset_5M_real['high'][loc_end_5M_price])/dataset_5M_real['high'][loc_end_5M_price]) * 100

		my_money = money

		if my_money >=100:
			lot = int(my_money/100) * coef_money
		else:
			lot = coef_money

		my_money = my_money - (lot * st_pr)

		money = my_money

		candle_index = index_st

		# print('st = ', signals['pattern_day'][loc_end_5M], ' ', signals['time_high_front'][loc_end_5M].hour)

		flag = 'st'

	if index_st == index_tp:

		if index_st != -1:
			st_pr = ((dataset_5M_real['high'][index_st] - dataset_5M_real['high'][loc_end_5M_price])/dataset_5M_real['high'][loc_end_5M_price]) * 100
			tp_pr = ((dataset_5M_real['low'][loc_end_5M_price] - np.min(dataset_5M_real['low'][loc_end_5M_price:index_st]) * (1 + spred))/(dataset_5M_real['low'][loc_end_5M_price])) * 100
			
			if dataset_5M_real['high'][index_st] > st: st_pr = ((st - dataset_5M_real['high'][loc_end_5M_price])/dataset_5M_real['high'][loc_end_5M_price]) * 100
			
			my_money = money

			if my_money >=100:
				lot = int(my_money/100) * coef_money
			else:
				lot = coef_money

			if lot > 2000: lot = 2000

			my_money = my_money - (lot * st_pr)

			money = my_money

			candle_index = index_st

			# print('st = ', signals['pattern_day'][loc_end_5M], ' ', signals['time_high_front'][loc_end_5M].hour)

			flag = 'st'

		else:
			flag = 'no_flag'
			tp_pr = 0
			st_pr = 0

	return money, flag, tp_pr, st_pr, candle_index

loging = getdata()
# loging.account_name = 'ahmadipc'
# loging.initilizer()
# loging.login()

dataset_5M, dataset_1H = loging.readall(symbol = symbol, number_5M = number_data_5M, number_1H = number_data_1H)

# parameters.elements['dataset_5M'] = loging.getone(timeframe = '5M', number = number_data_5M, symbol = 'XAUUSD_i')
# parameters.elements['dataset_1H'] = loging.getone(timeframe = '1H', number = 4000, symbol = 'XAUUSD_i')

# dataset_5M_real = loging.getone(timeframe = '5M', number = number_data_5M, symbol = 'XAUUSD_i')
dataset_5M_real, _ = loging.readall(symbol = symbol, number_5M = 'all', number_1H = 0)
dataset_5M_real = dataset_5M_real[symbol]

macd_parameters = MacdParameters()
macd_config = MacdConfig()

rsi_parameters = RsiParameters()
rsi_config = RsiConfig()

stochastic_parameters = StochAsticParameters()
stochastic_config = StochAsticConfig()

macd_parameters.elements['dataset_5M'] = dataset_5M
macd_parameters.elements['dataset_1H'] = dataset_1H
macd_parameters.elements['symbol'] = symbol

rsi_parameters.elements['dataset_5M'] = dataset_5M
rsi_parameters.elements['dataset_1H'] = dataset_1H
rsi_parameters.elements['symbol'] = symbol

stochastic_parameters.elements['dataset_5M'] = dataset_5M
stochastic_parameters.elements['dataset_1H'] = dataset_1H
stochastic_parameters.elements['symbol'] = symbol


macd = MACD(parameters = macd_parameters, config = macd_config)
rsi = RSI(parameters = rsi_parameters, config = rsi_config)
stochastic = StochAstic(parameters = stochastic_parameters, config = stochastic_config)

candle_index = start_point

number_tp = 0
number_st = 0

output = pd.DataFrame(columns = [
								'candle_index', 
								'time', 
								'Day',
								'signal', 
								'indicator',
								'flag', 
								'number_tp', 
								'number_st', 
								'money', 
								'tp_final', 
								'st_final', 
								'percent', 
								'tp', 
								'st',
								])
	

print('Start ....')
while candle_index < dataset_5M_real.index[-1]:

	# if candle_index < 4400: 
	# 	candle_index += 1
	# 	continue

	dataset_1H_trade = dataset_1H.copy()
	dataset_1H_trade[symbol] = dataset_1H[symbol].copy(deep = True)
	dataset_5M_sliced = dataset_5M.copy()
	dataset_5M_sliced[symbol] = dataset_5M_sliced[symbol].truncate(before=candle_index - start_point, after=candle_index, axis=None, copy=True).reset_index(drop=True)
	# dataset_5M_sliced[symbol] = dataset_5M_sliced[symbol].reset_index(inplace = False)
	# dataset_5M_sliced[symbol] = dataset_5M_sliced[symbol].drop(columns = 'index')

	# print('no Sliced = ', dataset_1H[symbol])
	# print('sliced = ', dataset_5M_sliced[symbol])

	flag = 'no_flag'

	# print(candle_index)

	try:
		signal_macd, tp_macd, st_macd = macd.LastSignal(
														dataset_5M = dataset_5M_sliced.copy(), 
														dataset_1H = dataset_1H_trade.copy(), 
														symbol = symbol
														)
	except Exception as ex:
		print('MACD: ', ex)

	# dataset_1H_trade = dataset_1H.copy()
	# dataset_1H_trade[symbol] = dataset_1H[symbol].copy(deep = True)

	# try:
	# 	signal_stochastic, tp_stochastic, st_stochastic = stochastic.LastSignal(
	# 																			dataset_5M = dataset_5M_sliced.copy(), 
	# 																			dataset_1H = dataset_1H_trade.copy(), 
	# 																			symbol = symbol
	# 																			)
	# except Exception as ex:
	# 	print('RSI: ', ex)

	# dataset_1H_trade = dataset_1H.copy()
	# dataset_1H_trade[symbol] = dataset_1H[symbol].copy(deep = True)

	# try:
	# 	signal_rsi, tp_rsi, st_rsi = rsi.LastSignal(
	# 												dataset_5M = dataset_5M_sliced.copy(), 
	# 												dataset_1H = dataset_1H_trade.copy(), 
	# 												symbol = symbol
	# 												)
	# except Exception as ex:
	# 	print('StochAstic: ', ex)

	signal = 'no_signal'
	resist = 0
	protect = 0

	if signal_macd == 'buy_primary' or signal_macd == 'buy_secondry' or signal_macd == 'sell_primary' or signal_macd == 'sell_secondry':
		signal = signal_macd
		tp = tp_macd
		st = st_macd
		indicator = 'macd'

	# elif signal_stochastic == 'buy_primary' or signal_stochastic == 'buy_secondry' or signal_stochastic == 'sell_primary' or signal_stochastic == 'sell_secondry':
	# 	signal = signal_stochastic
	# 	tp = tp_stochastic
	# 	st = st_stochastic
	# 	indicator = 'stochastic'

	# elif signal_rsi == 'buy_primary' or signal_rsi == 'buy_secondry' or signal_rsi == 'sell_primary' or signal_rsi == 'sell_secondry':
	# 	signal = signal_rsi
	# 	tp = tp_rsi
	# 	st = st_rsi
	# 	indicator = 'rsi'

	# print('ccccccaaaaandle = ', candle_index)
	
	if signal == 'buy_primary' or signal == 'buy_secondry':

		# print('st = ', st)
		# print('low = ', dataset_5M_real['low'][candle_index])
		

		# print('tp = ', tp)
		# print('high = ', (1 + spred) * dataset_5M_real['high'][candle_index])
		

		# print()

		# print('signal_macd = ', signal_macd)
		# print('signal_rsi = ', signal_rsi)
		# print('signal_stochastic = ', signal_stochastic)
		# print()

		try:
			money, flag, tp_pr, st_pr, candle_index_last = BuyChecker(dataset_5M_real, tp, st, candle_index, money, coef_money, spred)
		except Exception as ex:
			print('Buy: ', ex) 
			flag = 'no_flag' 
			tp_pr = 0
			st_pr = 0

	elif signal == 'sell_primary' or signal == 'sell_secondry':

		# print('st = ', st)
		# print('high = ', (1 + spred) * dataset_5M_real['high'][candle_index])

		# print('tp = ', tp)
		# print('low = ', dataset_5M_real['low'][candle_index])

		# print()

		# print('signal_macd = ', signal_macd)
		# print('signal_rsi = ', signal_rsi)
		# print('signal_stochastic = ', signal_stochastic)
		# print()

		try:
			money, flag, tp_pr, st_pr, candle_index_last = SellChecker(dataset_5M_real, tp, st, candle_index, money, coef_money, spred)

		except: 
			print('SELL: ', ex)
			flag = 'no_flag' 
			tp_pr = 0
			st_pr = 0

	if flag == 'tp':
		percent += tp_pr
		tp_pr_eq += tp_pr
		number_tp += 1

		output = output.append(
								{
								'candle_index': candle_index,
								'time': dataset_5M_real['time'][candle_index],
								'Day': dataset_5M_real['time'][candle_index].day_name(),
								'signal': signal,
								'indicator': indicator,
								'flag': flag,
								'number_tp': number_tp,
								'number_st': number_st,
								'money': money,
								'tp_final': tp_pr_eq,
								'st_final': st_pr_eq,
								'percent': percent,
								'tp': tp_pr,
								'st': st_pr,
								},
								ignore_index = True
								)
		candle_index = candle_index_last
		print()
		with pd.option_context('display.max_rows', None, 'display.max_columns', None):
			print(output.iloc[-1])
		print()

		if os.path.exists('MainTester.csv'):
			os.remove('MainTester.csv')
		output.to_csv('MainTester.csv')

	elif flag == 'st':
		percent -= st_pr
		st_pr_eq += st_pr
		number_st += 1

		output = output.append(
								{
								'candle_index': candle_index,
								'time': dataset_5M_real['time'][candle_index],
								'Day': dataset_5M_real['time'][candle_index].day_name(),
								'signal': signal,
								'indicator': indicator,
								'flag': flag,
								'number_tp': number_tp,
								'number_st': number_st,
								'money': money,
								'tp_final': tp_pr_eq,
								'st_final': st_pr_eq,
								'percent': percent,
								'tp': tp_pr,
								'st': st_pr,
								},
								ignore_index = True
								)
		candle_index = candle_index_last
		print()
		with pd.option_context('display.max_rows', None, 'display.max_columns', None):
			print(output.iloc[-1])
		print()

		if os.path.exists('MainTester.csv'):
			os.remove('MainTester.csv')
		output.to_csv('MainTester.csv')

	if money <= 4: break

	candle_index += 1

output.to_csv('MainTester.csv')


print('* Final Money = ', money)
print('********** tp = ', tp_pr_eq)
print('********** st = ', st_pr_eq)
print('Fanal percent = ', percent)


