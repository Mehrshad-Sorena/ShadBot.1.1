# from src.Utils.Divergence.Parameters import Parameters as Divergence_Parameters
from src.utils.DataReader.MetaTraderReader5.LoginGetData import LoginGetData as getdata
from src.utils.Divergence.Config import Config as Divergence_Config
from src.utils.Divergence.Divergence import Divergence
from src.indicators.ZigZag import ZigZag
import matplotlib.pyplot as plt
import pandas_ta as ind
import pandas as pd
import numpy as np
import os



import matplotlib.pyplot as plt






class Tester:

	def __init__(
				self,
				parameters
				):
		self.elements = dict(
							{

							#Elemns For Tester:

							__class__.__name__ + '_coef_money': parameters.elements['Tester_coef_money'],
							__class__.__name__ + '_spred': parameters.elements['Tester_spred'],

							#////////////////////////////////

							#Elemns Gloal:

							'st_percent_min': parameters.elements['st_percent_min'],
							'st_percent_max': parameters.elements['st_percent_max'],

							'tp_percent_min': parameters.elements['tp_percent_min'],
							'tp_percent_max': parameters.elements['tp_percent_max'],

							#////////////////////////////////
							}
							)

		#*****************************

	def FlagFinderBuy(self, dataset_5M_real, dataset_5M, extereme, flaglearn, loc_end_5M, money, signals, indicator = '', flag_savepic = False):
		
		spred = self.elements['Tester_spred']

		dataset_5M_real = dataset_5M_real.copy(deep = True)

		if signals['signal'][loc_end_5M] == 'buy_primary':
			if dataset_5M_real['low'][signals['index_back'][loc_end_5M]] < dataset_5M_real['low'][loc_end_5M]:
				extereme = extereme.assign(
										flag =  'no_flag',
										tp_pr =  np.nan,
										st_pr =  np.nan,
										index_tp =  np.nan,
										index_st = np.nan,
										money = money,
										time = np.nan,
										)
				return extereme

		elif signals['signal'][loc_end_5M] == 'buy_secondry':
			if dataset_5M_real['low'][signals['index_back'][loc_end_5M]] > dataset_5M_real['low'][loc_end_5M]:
				extereme = extereme.assign(
										flag =  'no_flag',
										tp_pr =  np.nan,
										st_pr =  np.nan,
										index_tp =  np.nan,
										index_st = np.nan,
										money = money,
										time = np.nan,
										)
				return extereme

		#Checking SMA:

		SMA_50 = ind.sma(dataset_5M['close'], length = 50)
		SMA_25 = ind.sma(dataset_5M['close'], length = 25)

		index_start_ZigZag = int(signals['index_back'][loc_end_5M])

		loc_end_5M_price = loc_end_5M

		if False:#(len(np.where(dataset_5M_real['low'][loc_end_5M: loc_end_5M + 50] >= SMA_50[int(signals['index_back'][loc_end_5M]) : loc_end_5M].min())[0])) > 1:
			loc_end_5M_price = loc_end_5M +  min(np.where(dataset_5M_real['low'][loc_end_5M: loc_end_5M + 50] >=SMA_50[int(signals['index_back'][loc_end_5M]) : loc_end_5M].min())[0])

			# zigzag = ZigZag.Find(
			# 						dataset = dataset_5M_real, 
			# 						index_first = index_start_ZigZag, 
			# 						index_last = loc_end_5M_price
			# 						)

			# if zigzag.values[-2] > dataset_5M_real['low'][loc_end_5M_price]:
				
			# 	extereme = extereme.assign(
			# 							flag =  'no_flag',
			# 							tp_pr =  np.nan,
			# 							st_pr =  np.nan,
			# 							index_tp =  np.nan,
			# 							index_st = np.nan,
			# 							money = money,
			# 							time = np.nan,
			# 							)
			# 	return extereme

		elif False:#len(np.where(dataset_5M_real['low'][loc_end_5M: loc_end_5M + 50] >= SMA_50[int(signals['index_back'][loc_end_5M]) : loc_end_5M].min())[0]) == 1:
			loc_end_5M_price = loc_end_5M + np.where(dataset_5M_real['low'][loc_end_5M: loc_end_5M + 50] >= SMA_50[int(signals['index_back'][loc_end_5M]) : loc_end_5M].min())[0][0]

			# zigzag = ZigZag.Find(
			# 						dataset = dataset_5M_real, 
			# 						index_first = index_start_ZigZag, 
			# 						index_last = loc_end_5M_price
			# 						)

			# if zigzag.values[-2] > dataset_5M_real['low'][loc_end_5M_price]:
				
			# 	extereme = extereme.assign(
			# 							flag =  'no_flag',
			# 							tp_pr =  np.nan,
			# 							st_pr =  np.nan,
			# 							index_tp =  np.nan,
			# 							index_st = np.nan,
			# 							money = money,
			# 							time = np.nan,
			# 							)
			# 	return extereme

		# else:
		# 	extereme = extereme.assign(
		# 								flag =  'no_flag',
		# 								tp_pr =  np.nan,
		# 								st_pr =  np.nan,
		# 								index_tp =  np.nan,
		# 								index_st = np.nan,
		# 								money = money,
		# 								time = np.nan,
		# 								)
		# 	return extereme

		#////////////////////////////////

		diff_pr_top = (((extereme['high_upper'][loc_end_5M]) - dataset_5M['high'][loc_end_5M_price])/dataset_5M['high'][loc_end_5M_price]) * 100
		diff_pr_down = ((dataset_5M['low'][loc_end_5M] - (extereme['low_lower'][loc_end_5M]))/dataset_5M['low'][loc_end_5M]) * 100

		# print('top = ', diff_pr_top)
		# print('down = ', diff_pr_down)

		st_percent_min = self.elements['st_percent_min']
		st_percent_max = self.elements['st_percent_max']

		tp_percent_min = self.elements['tp_percent_min']
		tp_percent_max = self.elements['tp_percent_max']

		# st_percent_min = 0.11 #0.37
		# st_percent_max = 0.1 #0.79

		# tp_percent_min = 0.13
		# tp_percent_max = 0.12

		# flaglearn = False

		if extereme.dropna().empty == True:
			diff_pr_down = st_percent_min
			extereme['low_lower'][loc_end_5M] = dataset_5M['low'][loc_end_5M] * (1-(st_percent_min/100))
			extereme['low_mid'][loc_end_5M] = dataset_5M['low'][loc_end_5M] * (1-(st_percent_min/100))
			extereme['low_upper'][loc_end_5M] = dataset_5M['low'][loc_end_5M] * (1-(st_percent_min/100))

			extereme['power_low_upper'][loc_end_5M] = 0
			extereme['power_low_mid'][loc_end_5M] = 0
			extereme['power_low_lower'][loc_end_5M] = 0


			diff_pr_top = tp_percent_min
			extereme['high_upper'][loc_end_5M] = dataset_5M['high'][loc_end_5M_price] * (1+(tp_percent_min/100))
			extereme['high_mid'][loc_end_5M] = dataset_5M['high'][loc_end_5M_price] * (1+(tp_percent_min/100))
			extereme['high_lower'][loc_end_5M] = dataset_5M['high'][loc_end_5M_price] * (1+(tp_percent_min/100))

			extereme['power_high_upper'][loc_end_5M] = 0
			extereme['power_high_mid'][loc_end_5M] = 0
			extereme['power_high_lower'][loc_end_5M] = 0


		if flaglearn == False:
			if diff_pr_down < st_percent_min:
				diff_pr_down = st_percent_min
				extereme['low_lower'][loc_end_5M] = dataset_5M['low'][loc_end_5M] * (1-(st_percent_min/100))

			if diff_pr_top < tp_percent_min:
				diff_pr_top = tp_percent_min
				extereme['high_upper'][loc_end_5M] = dataset_5M['high'][loc_end_5M_price] * (1+(tp_percent_min/100))

		if diff_pr_down > st_percent_max:
			diff_pr_down = st_percent_max
			extereme['low_lower'][loc_end_5M] = dataset_5M['low'][loc_end_5M] * (1-(st_percent_max/100))
		
		if diff_pr_top > tp_percent_max:
			diff_pr_top = tp_percent_max
			extereme['high_upper'][loc_end_5M] = dataset_5M['high'][loc_end_5M_price] * (1+(tp_percent_max/100))

		if (
			dataset_5M_real['high'][loc_end_5M_price] * (1 + spred) >= extereme['high_upper'][loc_end_5M] or
			dataset_5M_real['low'][loc_end_5M_price] <= extereme['low_lower'][loc_end_5M] #or
			#extereme.dropna().empty == True
			):
			extereme = extereme.assign(
										flag =  'no_flag',
										tp_pr =  np.nan,
										st_pr =  np.nan,
										index_tp =  np.nan,
										index_st = np.nan,
										money = money,
										time = np.nan,
										)
			return extereme


		#*************** Finding Take Profit:

		if (len(np.where(((dataset_5M_real['high'][(loc_end_5M_price):-1].values) >= extereme['high_upper'][loc_end_5M]))[0]) > 1):
			index_tp =	loc_end_5M_price + min(
											np.where(
														(
															(dataset_5M_real['high'][(loc_end_5M_price):-1].values) >= extereme['high_upper'][loc_end_5M]
														)
													)[0] 
											)

		elif (len(np.where(((dataset_5M_real['high'][(loc_end_5M_price):-1].values) >= extereme['high_upper'][loc_end_5M]))[0]) == 1):
			index_tp =	loc_end_5M_price + np.where(
													(
														(dataset_5M_real['high'][(loc_end_5M_price):-1].values) >= extereme['high_upper'][loc_end_5M]
													)
												)[0][0] 

		else:
			index_tp = -1
			tp_pr = 0
		#///////////////////////////////

		#************ Finding Stop Loss:

		if (len(np.where(((dataset_5M_real['low'][(loc_end_5M_price):-1].values) <= extereme['low_lower'][loc_end_5M]))[0]) > 1):
			index_st =	loc_end_5M_price + min(
										np.where(
													(
														(dataset_5M_real['low'][(loc_end_5M_price):-1].values) <= extereme['low_lower'][loc_end_5M]
													)
												)[0]
										)

		elif (len(np.where(((dataset_5M_real['low'][(loc_end_5M_price):-1].values) <= extereme['low_lower'][loc_end_5M]))[0]) == 1):
			index_st =	loc_end_5M_price + np.where(
												(
													(dataset_5M_real['low'][(loc_end_5M_price):-1].values) <= extereme['low_lower'][loc_end_5M]
												)
											)[0][0]

		else:
			index_st = -1
			st_pr = 0

		if (
			index_tp < index_st and
			index_tp != -1
			):

			st_pr = ((dataset_5M_real['low'][loc_end_5M_price] - np.min(dataset_5M_real['low'][loc_end_5M_price:index_tp]))/dataset_5M_real['low'][loc_end_5M_price]) * 100
			tp_pr = ((dataset_5M_real['high'][index_tp] - dataset_5M_real['high'][loc_end_5M_price]*(1 + spred))/(dataset_5M_real['high'][loc_end_5M_price] * (1 + spred))) * 100

			if tp_pr > tp_percent_max: tp_pr = tp_percent_max

			my_money = money
			coef_money = self.elements['Tester_coef_money']

			if my_money >=100:
				lot = int(my_money/100) * coef_money
			else:
				lot = coef_money

			if lot > 2000: lot = 2000

			my_money = my_money + (lot * tp_pr)

			money = my_money

			extereme = extereme.assign(
										flag =  'tp',
										tp_pr = tp_pr,
										st_pr = st_pr,
										index_tp = index_tp,
										index_st = index_st,
										money = my_money,
										time = dataset_5M_real['time'][loc_end_5M_price],
										)

		elif (
			index_tp != -1 and
			index_st == -1
			):
			st_pr = ((dataset_5M_real['low'][loc_end_5M_price] - np.min(dataset_5M_real['low'][loc_end_5M_price:index_tp]))/dataset_5M_real['low'][loc_end_5M_price]) * 100
			tp_pr = ((dataset_5M_real['high'][index_tp] - dataset_5M_real['high'][loc_end_5M_price]*(1 + spred))/(dataset_5M_real['high'][loc_end_5M_price] * (1 + spred))) * 100

			if tp_pr > tp_percent_max: tp_pr = tp_percent_max


			my_money = money
			coef_money = self.elements['Tester_coef_money']

			if my_money >=100:
				lot = int(my_money/100) * coef_money
			else:
				lot = coef_money

			if lot > 2000: lot = 2000

			my_money = my_money + (lot * tp_pr)

			money = my_money

			extereme = extereme.assign(
										flag =  'tp',
										tp_pr = tp_pr,
										st_pr = st_pr,
										index_tp = index_tp,
										index_st = index_st,
										money = my_money,
										time = dataset_5M_real['time'][loc_end_5M_price],
										)

		elif (
			index_st < index_tp and
			index_st != -1
			):
			st_pr = ((dataset_5M_real['low'][loc_end_5M_price] - dataset_5M_real['low'][index_st])/dataset_5M_real['low'][loc_end_5M_price]) * 100
			tp_pr = ((np.max(dataset_5M_real['high'][loc_end_5M_price:index_st]) - dataset_5M_real['high'][loc_end_5M_price]*(1 + spred))/(dataset_5M_real['high'][loc_end_5M_price] * (1 + spred))) * 100

			if st_pr > st_percent_max: st_pr = st_percent_max

			my_money = money
			coef_money = self.elements['Tester_coef_money']

			if my_money >=100:
				lot = int(my_money/100) * coef_money
			else:
				lot = coef_money

			if lot > 2000: lot = 2000

			my_money = my_money - (lot * st_pr)

			money = my_money

			extereme = extereme.assign(
										flag =  'st',
										tp_pr =  tp_pr,
										st_pr =  st_pr,
										index_tp =  index_tp,
										index_st = index_st,
										money = my_money,
										time = dataset_5M_real['time'][loc_end_5M_price],
										)

		elif (
			index_tp == -1 and
			index_st != -1
			):
			st_pr = ((dataset_5M_real['low'][loc_end_5M_price] - dataset_5M_real['low'][index_st])/dataset_5M_real['low'][loc_end_5M_price]) * 100
			tp_pr = ((np.max(dataset_5M_real['high'][loc_end_5M_price:index_st]) - dataset_5M_real['high'][loc_end_5M_price]*(1 + spred))/(dataset_5M_real['high'][loc_end_5M_price] * (1 + spred))) * 100
			
			if st_pr > st_percent_max: st_pr = st_percent_max

			my_money = money
			coef_money = self.elements['Tester_coef_money']

			if my_money >=100:
				lot = int(my_money/100) * coef_money
			else:
				lot = coef_money

			if lot > 2000: lot = 2000

			my_money = my_money - (lot * st_pr)

			money = my_money

			extereme = extereme.assign(
										flag =  'st',
										tp_pr =  tp_pr,
										st_pr =  st_pr,
										index_tp =  index_tp,
										index_st = index_st,
										money = my_money,
										time = dataset_5M_real['time'][loc_end_5M_price],
										)

		if index_st == index_tp:

			if index_st != -1:
				st_pr = ((dataset_5M_real['low'][loc_end_5M_price] - dataset_5M_real['low'][index_st])/dataset_5M_real['low'][loc_end_5M_price]) * 100
				tp_pr = ((np.max(dataset_5M_real['high'][loc_end_5M_price:index_st]) - dataset_5M_real['high'][loc_end_5M_price]*(1 + spred))/(dataset_5M_real['high'][loc_end_5M_price] * (1 + spred))) * 100
				
				if st_pr > st_percent_max: st_pr = st_percent_max

				my_money = money
				coef_money = self.elements['Tester_coef_money']

				if my_money >=100:
					lot = int(my_money/100) * coef_money
				else:
					lot = coef_money

				if lot > 2000: lot = 2000

				my_money = my_money - (lot * st_pr)

				money = my_money

				extereme = extereme.assign(
											flag =  'st',
											tp_pr =  tp_pr,
											st_pr =  st_pr,
											index_tp =  index_tp,
											index_st = index_st,
											money = my_money,
											time = dataset_5M_real['time'][loc_end_5M_price],
											)
			else:
				extereme = extereme.assign(
											flag =  'no_flag',
											tp_pr =  np.nan,
											st_pr =  np.nan,
											index_tp =  np.nan,
											index_st = np.nan,
											money = money,
											time = np.nan,
											)

		if False:#self.flag_pic_save_tester == True:

			path_indicator = (
						'pics/' +
						#signals['indicator_name'][signals['index'].max()] +  '/' + 
						signals['signal'][signals['index'].max()] + '/' + 
						#signals['symbol'][signals['index'].max()] + '/' +
						extereme['flag'][loc_end_5M] + '/' 
						#signals['indicator_name'][signals['index'].max()] + '/'
						)

			if not os.path.exists(path_indicator):
				os.makedirs(path_indicator)
				path_indicator = path_indicator + str(loc_end_5M)
			else:
				path_indicator = path_indicator + str(loc_end_5M)

			if extereme['flag'][loc_end_5M] != 'no_flag':
				if extereme['flag'][loc_end_5M] == 'tp':
					index_end = index_tp
				else:
					index_end = index_st

				# print(signals.columns)

				# with pd.option_context('display.max_rows', None, 'display.max_columns', None):
				# print(indicator[signals['column_div']])

				index_start = int(signals['index_back'][loc_end_5M])

				fig, (ax0, ax1) = plt.subplots(2)

				ax0.plot(dataset_5M_real.index[index_start - 20:index_end + 20], dataset_5M_real['high'][index_start - 20:index_end + 20], c = 'green')
				ax0.plot(dataset_5M_real.index[index_start - 20:index_end + 20], dataset_5M_real['low'][index_start - 20:index_end + 20], c = 'green')
				ax0.plot(SMA_50[index_start - 20:index_end + 20], c = 'r')
				ax0.plot(SMA_25[index_start - 20:index_end + 20], c = 'b')
				ax0.axhline(y = extereme['high_upper'][loc_end_5M])
				ax0.axhline(y = extereme['low_lower'][loc_end_5M])

				# ax0.plot([signals['index_back'][loc_end_5M], loc_end_5M], 
				# 	[signals['low_back'][loc_end_5M], signals['low_front'][loc_end_5M]], c = 'r')

				if False:#dataset_5M_real['low'][signals['index_back'][loc_end_5M]] < dataset_5M_real['low'][loc_end_5M]:
					# with pd.option_context('display.max_rows', None, 'display.max_columns', None):
					# 	print(signals)
					print(signals['index_back'][loc_end_5M])
					print(loc_end_5M)
					print('real back = ', dataset_5M_real['low'][signals['index_back'][loc_end_5M]])
					print('real front = ', dataset_5M_real['low'][loc_end_5M])

					print('filter back = ', dataset_5M['low'][signals['index_back'][loc_end_5M]])
					print('filter front = ', dataset_5M['low'][loc_end_5M])

				ax0.plot([signals['index_back'][loc_end_5M], loc_end_5M], 
					[dataset_5M_real['low'][signals['index_back'][loc_end_5M]], dataset_5M_real['low'][loc_end_5M]], c = 'r')

				ax0.axvline(x = loc_end_5M_price, c = 'purple', linestyle = '-.')

				ax0.axvline(x = index_end, c = 'pink', linestyle = '-.')

				
				ax1.axvline(x = index_start, c = 'r')
				ax1.axvline(x = loc_end_5M, c = 'r')
				ax1.axvline(x = loc_end_5M_price, c = 'purple', linestyle = '-.')

				index_start = index_start - indicator[signals['column_div']].index[0]
				index_end = index_end - indicator[signals['column_div']].index[0]

				ax1.plot(indicator[signals['column_div']][index_start - 20:index_end + 20])

				ax1.plot([signals['index_back'][loc_end_5M], loc_end_5M], 
					[signals['indicator_back'][loc_end_5M], signals['indicator_front'][loc_end_5M]], c = 'r')

				plt.title(label = extereme['flag'][loc_end_5M])
				plt.savefig(path_indicator, dpi=600, bbox_inches='tight')

				plt.figure().clear()
				plt.close('all')
				plt.cla()
				plt.clf()
		
		if flag_savepic == True:
			divergence_config = Divergence_Config()
			# divergence_parameters = Divergence_Parameters()
			divergence = Divergence(parameters = divergence_parameters, config = divergence_config)
			divergence.PlotSaver(
								signals = signals,
								extreme = extereme,
								loc_end_5M = loc_end_5M,
								indicator = indicator,
								dataset_5M = dataset_5M,
								res_pro_high = extereme['high_upper'][loc_end_5M],
								res_pro_low = extereme['low_lower'][loc_end_5M],
								flag_savepic = flag_savepic
								)
		return extereme

	#////////////////////////////


	#******************************

	def FlagFinderSell(self, dataset_5M_real, dataset_5M, extereme, flaglearn, loc_end_5M, money, signals, indicator = '', flag_savepic = False):
		
		spred = self.elements['Tester_spred']

		dataset_5M_real = dataset_5M_real.copy(deep = True)

		if signals['signal'][loc_end_5M] == 'sell_primary':
			if dataset_5M_real['high'][signals['index_back'][loc_end_5M]] > dataset_5M_real['high'][loc_end_5M]:
				extereme = extereme.assign(
										flag =  'no_flag',
										tp_pr =  np.nan,
										st_pr =  np.nan,
										index_tp =  np.nan,
										index_st = np.nan,
										money = money,
										time = np.nan,
										)
				return extereme

		elif signals['signal'][loc_end_5M] == 'sell_secondry':
			if dataset_5M_real['high'][signals['index_back'][loc_end_5M]] < dataset_5M_real['high'][loc_end_5M]:
				extereme = extereme.assign(
										flag =  'no_flag',
										tp_pr =  np.nan,
										st_pr =  np.nan,
										index_tp =  np.nan,
										index_st = np.nan,
										money = money,
										time = np.nan,
										)
				return extereme


		#Checking SMA:

		# SMA_50 = ind.sma(dataset_5M['close'], length = 50)
		# SMA_25 = ind.sma(dataset_5M['close'], length = 25)

		index_start_ZigZag = int(signals['index_back'][loc_end_5M])

		loc_end_5M_price = loc_end_5M

		if False:#(len(np.where(dataset_5M_real['high'][loc_end_5M: loc_end_5M + 50] < np.mean(SMA_50[int(signals['index_back'][loc_end_5M]): loc_end_5M]))[0])) > 1:
			loc_end_5M_price = loc_end_5M +  min(np.where(dataset_5M_real['high'][loc_end_5M: loc_end_5M + 50] < np.mean(SMA_50[int(signals['index_back'][loc_end_5M]): loc_end_5M]))[0])

			if SMA_25[loc_end_5M_price] > SMA_50[loc_end_5M_price]:
				extereme = extereme.assign(
										flag =  'no_flag',
										tp_pr =  np.nan,
										st_pr =  np.nan,
										index_tp =  np.nan,
										index_st = np.nan,
										money = money,
										time = np.nan,
										)
				return extereme

			zigzag = ZigZag.Find(
									dataset = dataset_5M_real, 
									index_first = index_start_ZigZag, 
									index_last = loc_end_5M_price
									)

			# if zigzag.values[-2] < dataset_5M_real['high'][loc_end_5M_price]:
				
			# 	extereme = extereme.assign(
			# 							flag =  'no_flag',
			# 							tp_pr =  np.nan,
			# 							st_pr =  np.nan,
			# 							index_tp =  np.nan,
			# 							index_st = np.nan,
			# 							money = money,
			# 							time = np.nan,
			# 							)
			# 	return extereme

		elif False:#(len(np.where(dataset_5M_real['high'][loc_end_5M: loc_end_5M + 50] < np.mean(SMA_50[int(signals['index_back'][loc_end_5M]): loc_end_5M]))[0])) == 1:
			loc_end_5M_price = loc_end_5M + np.where(dataset_5M_real['high'][loc_end_5M: loc_end_5M + 50] < np.mean(SMA_50[int(signals['index_back'][loc_end_5M]): loc_end_5M]))[0][0]

			if SMA_25[loc_end_5M_price] > SMA_50[loc_end_5M_price]:
				extereme = extereme.assign(
										flag =  'no_flag',
										tp_pr =  np.nan,
										st_pr =  np.nan,
										index_tp =  np.nan,
										index_st = np.nan,
										money = money,
										time = np.nan,
										)
				return extereme

			zigzag = ZigZag.Find(
									dataset = dataset_5M_real, 
									index_first = index_start_ZigZag, 
									index_last = loc_end_5M_price
									)

			if zigzag.values[-2] < dataset_5M_real['high'][loc_end_5M_price]:
				
				extereme = extereme.assign(
										flag =  'no_flag',
										tp_pr =  np.nan,
										st_pr =  np.nan,
										index_tp =  np.nan,
										index_st = np.nan,
										money = money,
										time = np.nan,
										)
				return extereme

		# else:
		# 	extereme = extereme.assign(
		# 								flag =  'no_flag',
		# 								tp_pr =  np.nan,
		# 								st_pr =  np.nan,
		# 								index_tp =  np.nan,
		# 								index_st = np.nan,
		# 								money = money,
		# 								time = np.nan,
		# 								)
		# 	return extereme

		#////////////////////////////////


		diff_pr_top = (((extereme['high_upper'][loc_end_5M]) - dataset_5M['high'][loc_end_5M])/dataset_5M['high'][loc_end_5M]) * 100
		diff_pr_down = ((dataset_5M['low'][loc_end_5M] - (extereme['low_lower'][loc_end_5M]))/dataset_5M['low'][loc_end_5M]) * 100

		st_percent_min = self.elements['st_percent_min']
		st_percent_max = self.elements['st_percent_max']

		tp_percent_min = self.elements['tp_percent_min']
		tp_percent_max = self.elements['tp_percent_max']
		
		# st_percent_min = 0.07
		# st_percent_max = 0.1

		# tp_percent_min = 0.18
		# tp_percent_max = 0.21

		if extereme.dropna().empty == True:

			diff_pr_top = st_percent_min
			extereme['high_upper'][loc_end_5M] = dataset_5M['high'][loc_end_5M] * (1+(st_percent_min/100))
			extereme['high_mid'][loc_end_5M] = dataset_5M['high'][loc_end_5M] * (1+(st_percent_min/100))
			extereme['high_lower'][loc_end_5M] = dataset_5M['high'][loc_end_5M] * (1+(st_percent_min/100))

			extereme['power_high_upper'][loc_end_5M] = 0
			extereme['power_high_mid'][loc_end_5M] = 0
			extereme['power_high_lower'][loc_end_5M] = 0


			diff_pr_down = tp_percent_min
			extereme['low_lower'][loc_end_5M] = dataset_5M['low'][loc_end_5M] * (1-(tp_percent_min/100))
			extereme['low_mid'][loc_end_5M] = dataset_5M['low'][loc_end_5M] * (1-(tp_percent_min/100))
			extereme['low_upper'][loc_end_5M] = dataset_5M['low'][loc_end_5M] * (1-(tp_percent_min/100))

			extereme['power_low_upper'][loc_end_5M] = 0
			extereme['power_low_mid'][loc_end_5M] = 0
			extereme['power_low_lower'][loc_end_5M] = 0


		if flaglearn == False:
			if diff_pr_top < st_percent_min:
				diff_pr_top = st_percent_min
				extereme['high_upper'][loc_end_5M] = dataset_5M['high'][loc_end_5M] * (1+(st_percent_min/100))

			if diff_pr_down < tp_percent_min:
				diff_pr_down = tp_percent_min
				extereme['low_lower'][loc_end_5M] = dataset_5M['low'][loc_end_5M] * (1-(tp_percent_min/100))

		if diff_pr_top > st_percent_max:
			diff_pr_top = st_percent_max
			extereme['high_upper'][loc_end_5M] = dataset_5M['high'][loc_end_5M] * (1+(st_percent_max/100))
		
		if diff_pr_down > tp_percent_max:
			diff_pr_down = tp_percent_max
			extereme['low_lower'][loc_end_5M] = dataset_5M['low'][loc_end_5M] * (1-(tp_percent_max/100))


		if (
			dataset_5M_real['high'][loc_end_5M_price] * (1 + spred) >= extereme['high_upper'][loc_end_5M] or
			dataset_5M_real['low'][loc_end_5M_price] <= extereme['low_lower'][loc_end_5M] #or
			# extereme.dropna().empty == True
			):
			extereme = extereme.assign(
										flag =  'no_flag',
										tp_pr =  np.nan,
										st_pr =  np.nan,
										index_tp =  np.nan,
										index_st = np.nan,
										money = money,
										time = np.nan,
										)
			return extereme

		

		#*************** Finding Take Profit:

		if (len(np.where(((dataset_5M_real['low'][(loc_end_5M_price):-1].values * (1 + spred)) <= extereme['low_lower'][loc_end_5M]))[0]) > 1):
			index_tp =	loc_end_5M_price + min(
										np.where(
													(
														(dataset_5M_real['low'][(loc_end_5M_price):-1].values) * (1 + spred) <= extereme['low_lower'][loc_end_5M]
													)
												)[0] 
										)

		elif (len(np.where(((dataset_5M_real['low'][(loc_end_5M_price):-1].values * (1 + spred)) <= extereme['low_lower'][loc_end_5M]))[0]) == 1):
			index_tp =	loc_end_5M_price + np.where(
												(
													(dataset_5M_real['low'][(loc_end_5M_price):-1].values * (1 + spred)) <= extereme['low_lower'][loc_end_5M]
												)
											)[0][0] 

		else:
			index_tp = -1
			tp_pr = 0
		#///////////////////////////////

		#************ Finding Stop Loss:

		if (len(np.where(((dataset_5M_real['high'][(loc_end_5M_price):-1].values * (1 + spred)) >= extereme['high_upper'][loc_end_5M]))[0]) > 1):
			index_st =	loc_end_5M_price + min(
										np.where(
													(
														(dataset_5M_real['high'][(loc_end_5M_price):-1].values * (1 + spred)) >= extereme['high_upper'][loc_end_5M]
													)
												)[0]
										)

		elif (len(np.where(((dataset_5M_real['high'][(loc_end_5M_price):-1].values * (1 + spred)) >= extereme['high_upper'][loc_end_5M]))[0]) == 1):
			index_st =	loc_end_5M_price + np.where(
												(
													(dataset_5M_real['high'][(loc_end_5M_price):-1].values * (1 + spred)) >= extereme['high_upper'][loc_end_5M]
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

			if tp_pr > tp_percent_max: tp_pr = tp_percent_max

			my_money = money
			coef_money = self.elements['Tester_coef_money']

			if my_money >=100:
				lot = int(my_money/100) * coef_money
			else:
				lot = coef_money

			if lot > 2000: lot = 2000

			my_money = my_money + (lot * tp_pr)

			money = my_money

			extereme = extereme.assign(
										flag =  'tp',
										tp_pr = tp_pr,
										st_pr = st_pr,
										index_tp = index_tp,
										index_st = index_st,
										money = my_money,
										time = dataset_5M_real['time'][loc_end_5M_price],
										)

		elif (
			index_tp != -1 and
			index_st == -1
			):
			st_pr = ((np.max(dataset_5M_real['high'][loc_end_5M_price:index_tp]) - dataset_5M_real['high'][loc_end_5M_price])/dataset_5M_real['high'][loc_end_5M_price]) * 100
			tp_pr = ((dataset_5M_real['low'][loc_end_5M_price] - dataset_5M_real['low'][index_tp] * (1 + spred))/(dataset_5M_real['low'][loc_end_5M_price])) * 100

			if tp_pr > tp_percent_max: tp_pr = tp_percent_max

			my_money = money
			coef_money = self.elements['Tester_coef_money']

			if my_money >=100:
				lot = int(my_money/100) * coef_money
			else:
				lot = coef_money

			if lot > 2000: lot = 2000

			my_money = my_money + (lot * tp_pr)

			money = my_money

			extereme = extereme.assign(
										flag =  'tp',
										tp_pr = tp_pr,
										st_pr = st_pr,
										index_tp = index_tp,
										index_st = index_st,
										money = my_money,
										time = dataset_5M_real['time'][loc_end_5M_price],
										)

		elif (
			index_st < index_tp and
			index_st != -1
			):
			st_pr = ((dataset_5M_real['high'][index_st] - dataset_5M_real['high'][loc_end_5M_price])/dataset_5M_real['high'][loc_end_5M_price]) * 100
			tp_pr = ((dataset_5M_real['low'][loc_end_5M_price] - np.min(dataset_5M_real['low'][loc_end_5M_price:index_st]) * (1 + spred))/(dataset_5M_real['low'][loc_end_5M_price])) * 100
			
			if st_pr > st_percent_max: st_pr = st_percent_max

			my_money = money
			coef_money = self.elements['Tester_coef_money']

			if my_money >=100:
				lot = int(my_money/100) * coef_money
			else:
				lot = coef_money

			if lot > 2000: lot = 2000

			my_money = my_money - (lot * st_pr)

			money = my_money

			extereme = extereme.assign(
										flag =  'st',
										tp_pr =  tp_pr,
										st_pr =  st_pr,
										index_tp =  index_tp,
										index_st = index_st,
										money = my_money,
										time = dataset_5M_real['time'][loc_end_5M_price],
										)

		elif (
			index_tp == -1 and
			index_st != -1
			):
			st_pr = ((dataset_5M_real['high'][index_st] - dataset_5M_real['high'][loc_end_5M_price])/dataset_5M_real['high'][loc_end_5M_price]) * 100
			tp_pr = ((dataset_5M_real['low'][loc_end_5M_price] - np.min(dataset_5M_real['low'][loc_end_5M_price:index_st]) * (1 + spred))/(dataset_5M_real['low'][loc_end_5M_price])) * 100
			
			if st_pr > st_percent_max: st_pr = st_percent_max

			my_money = money
			coef_money = self.elements['Tester_coef_money']

			if my_money >=100:
				lot = int(my_money/100) * coef_money
			else:
				lot = coef_money

			my_money = my_money - (lot * st_pr)

			money = my_money

			extereme = extereme.assign(
										flag =  'st',
										tp_pr =  tp_pr,
										st_pr =  st_pr,
										index_tp =  index_tp,
										index_st = index_st,
										money = my_money,
										time = dataset_5M_real['time'][loc_end_5M_price],
										)

		if index_st == index_tp:

			if index_st != -1:
				st_pr = ((dataset_5M_real['high'][index_st] - dataset_5M_real['high'][loc_end_5M_price])/dataset_5M_real['high'][loc_end_5M_price]) * 100
				tp_pr = ((dataset_5M_real['low'][loc_end_5M_price] - np.min(dataset_5M_real['low'][loc_end_5M_price:index_st]) * (1 + spred))/(dataset_5M_real['low'][loc_end_5M_price])) * 100
				
				if st_pr > st_percent_max: st_pr = st_percent_max
				
				my_money = money
				coef_money = self.elements['Tester_coef_money']

				if my_money >=100:
					lot = int(my_money/100) * coef_money
				else:
					lot = coef_money

				if lot > 2000: lot = 2000

				my_money = my_money - (lot * st_pr)

				money = my_money

				extereme = extereme.assign(
											flag =  'st',
											tp_pr =  tp_pr,
											st_pr =  st_pr,
											index_tp =  index_tp,
											index_st = index_st,
											money = my_money,
											time = dataset_5M_real['time'][loc_end_5M_price],
											)
			else:
				extereme = extereme.assign(
											flag =  'no_flag',
											tp_pr =  np.nan,
											st_pr =  np.nan,
											index_tp =  np.nan,
											index_st = np.nan,
											money = money,
											time = np.nan,
											)

		if False:#self.flag_pic_save_tester == True:

			path_indicator = (
						'pics/' +
						#signals['indicator_name'][signals['index'].max()] +  '/' + 
						signals['signal'][signals['index'].max()] + '/' + 
						#signals['symbol'][signals['index'].max()] + '/' +
						extereme['flag'][loc_end_5M] + '/' 
						#signals['indicator_name'][signals['index'].max()] + '/'
						)

			if not os.path.exists(path_indicator):
				os.makedirs(path_indicator)
				path_indicator = path_indicator + str(loc_end_5M)
			else:
				path_indicator = path_indicator + str(loc_end_5M)

			if extereme['flag'][loc_end_5M] != 'no_flag':
				if extereme['flag'][loc_end_5M] == 'tp':
					index_end = index_tp
				else:
					index_end = index_st

				# print(signals.columns)

				# with pd.option_context('display.max_rows', None, 'display.max_columns', None):
				# print(indicator[signals['column_div']])

				index_start = int(signals['index_back'][loc_end_5M])

				fig, (ax0, ax1) = plt.subplots(2)

				ax0.plot(dataset_5M_real.index[index_start - 20:index_end + 20], dataset_5M_real['high'][index_start - 20:index_end + 20], c = 'green')
				ax0.plot(dataset_5M_real.index[index_start - 20:index_end + 20], dataset_5M_real['low'][index_start - 20:index_end + 20], c = 'green')
				ax0.plot(SMA_50[index_start - 20:index_end + 20], c = 'r')
				ax0.plot(SMA_25[index_start - 20:index_end + 20], c = 'b')
				ax0.axhline(y = extereme['high_upper'][loc_end_5M])
				ax0.axhline(y = extereme['low_lower'][loc_end_5M])

				# ax0.plot([signals['index_back'][loc_end_5M], loc_end_5M], 
				# 	[signals['low_back'][loc_end_5M], signals['low_front'][loc_end_5M]], c = 'r')

				if False:#dataset_5M_real['low'][signals['index_back'][loc_end_5M]] < dataset_5M_real['low'][loc_end_5M]:
					# with pd.option_context('display.max_rows', None, 'display.max_columns', None):
					# 	print(signals)
					print(signals['index_back'][loc_end_5M])
					print(loc_end_5M)
					print('real back = ', dataset_5M_real['low'][signals['index_back'][loc_end_5M]])
					print('real front = ', dataset_5M_real['low'][loc_end_5M])

					print('filter back = ', dataset_5M['low'][signals['index_back'][loc_end_5M]])
					print('filter front = ', dataset_5M['low'][loc_end_5M])

				ax0.plot([signals['index_back'][loc_end_5M], loc_end_5M], 
					[dataset_5M_real['high'][signals['index_back'][loc_end_5M]], dataset_5M_real['high'][loc_end_5M]], c = 'r')

				ax0.axvline(x = loc_end_5M_price, c = 'purple', linestyle = '-.')

				ax0.axvline(x = index_end, c = 'pink', linestyle = '-.')

				
				ax1.axvline(x = index_start, c = 'r')
				ax1.axvline(x = loc_end_5M, c = 'r')
				ax1.axvline(x = loc_end_5M_price, c = 'purple', linestyle = '-.')

				index_start = index_start - indicator[signals['column_div']].index[0]
				index_end = index_end - indicator[signals['column_div']].index[0]

				ax1.plot(indicator[signals['column_div']][index_start - 20:index_end + 20])

				ax1.plot([signals['index_back'][loc_end_5M], loc_end_5M], 
					[signals['indicator_back'][loc_end_5M], signals['indicator_front'][loc_end_5M]], c = 'r')

				plt.title(label = extereme['flag'][loc_end_5M])
				plt.savefig(path_indicator, dpi=600, bbox_inches='tight')

				plt.figure().clear()
				plt.close('all')
				plt.cla()
				plt.clf()

		if flag_savepic == True:
			divergence_config = Divergence_Config()
			# divergence_parameters = Divergence_Parameters()
			divergence = Divergence(parameters = divergence_parameters, config = divergence_config)
			divergence.PlotSaver(
								signals = signals,
								extreme = extereme,
								loc_end_5M = loc_end_5M,
								indicator = indicator,
								dataset_5M = dataset_5M,
								res_pro_high = extereme['high_upper'][loc_end_5M],
								res_pro_low = extereme['low_lower'][loc_end_5M],
								flag_savepic = flag_savepic
								)
		# print(extereme)
		return extereme


	#/////////////////////////////



	