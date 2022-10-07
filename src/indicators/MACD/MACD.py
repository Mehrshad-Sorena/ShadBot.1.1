import pandas_ta as ind
import pandas as pd
import numpy as np
from .Chromosome import Chromosome
import os
from .Config import Config as MACDConfig
from .Parameters import Parameters as MACDParameters
from progress.bar import Bar
from random import randint
from src.utils.Divergence.Parameters import Parameters as indicator_parameters
from src.utils.Divergence.Config import Config as indicator_config

from src.utils.ProtectResist.PRMethod.Parameters import Parameters as PRParameters
from src.utils.ProtectResist.PRMethod.Config import Config as PRConfig

from src.utils.Tools.timer import stTime

from src.utils.Divergence.Divergence import Divergence
from src.utils.Divergence.Tester import Tester

from src.utils.ProtectResist.PRMethod.Runner import Runner
from src.utils.Optimizers import NoiseCanceller

from src.indicators.ZigZag import ZigZag

import matplotlib.pyplot as plt

import copy
import sys


if 'win' in sys.platform:
	path_slash = '\\'
elif 'linux' in sys.platform:
	path_slash = '/'

#Functions Used:

#calculator_macd(self)

#/////////////////////////////////

class MACD:

	def __init__(
				self,
				parameters,
				config
				):

		self.elements = dict({
							#*********************

							__class__.__name__ + '_fast': parameters.elements[__class__.__name__ + '_fast'],
							__class__.__name__ + '_slow': parameters.elements[__class__.__name__ + '_slow'],
							__class__.__name__ + '_signal': parameters.elements[__class__.__name__ + '_signal'],

							__class__.__name__ + '_apply_to': parameters.elements[__class__.__name__ + '_apply_to'],

							'symbol': parameters.elements['symbol'],

							#///////////////////////

							#Globals:

							'dataset_5M': parameters.elements['dataset_5M'],
							'dataset_1H': parameters.elements['dataset_1H'],

							#/////////////////////////
							})

		self.cfg = dict({

						})


	def ParameterReader(self, symbol, signaltype, signalpriority):

		macd_config = MACDConfig()
		path_superhuman = macd_config.cfg['path_superhuman'] + signalpriority + path_slash + signaltype + path_slash

		macd_parameters = MACDParameters()

		pr_parameters = PRParameters()
		pr_config = PRConfig()

		ind_parameters = indicator_parameters()


		if os.path.exists(path_superhuman + symbol + '.csv'):

			GL_Results = pd.read_csv(path_superhuman + symbol + '.csv')

			if 'Unnamed: 0' in GL_Results.columns:
				GL_Results = GL_Results.drop(columns = ['Unnamed: 0'])

			# with pd.option_context('display.max_rows', None, 'display.max_columns', None):
			# 	print('DB Readed = ', GL_Results)

			for elm in GL_Results.columns:

				for pr_param_elm in pr_parameters.elements.keys():
					if pr_param_elm == elm:
						if (
							elm == 'BestFinder_alpha_low' or
							elm == 'BestFinder_alpha_high' or
							elm == 'st_percent_min' or
							elm == 'st_percent_max' or
							elm == 'tp_percent_min' or
							elm == 'tp_percent_max'
							):
							pr_parameters.elements[pr_param_elm] = GL_Results[elm][0]
						else:
							pr_parameters.elements[pr_param_elm] = int(GL_Results[elm][0])

				for pr_conf_elm in pr_config.cfg.keys():
					if pr_conf_elm == elm:
						pr_config.cfg[pr_conf_elm] = GL_Results[elm][0]


				for ind_elm in ind_parameters.elements.keys():
					if ind_elm == elm:

						if elm == 'BestFinder_alpha':
							ind_parameters.elements[ind_elm] = GL_Results[elm][0]
						else:
							ind_parameters.elements[ind_elm] = int(GL_Results[elm][0])


				for macd_elm in macd_parameters.elements.keys():
					if macd_elm == elm:
						if elm == 'MACD_apply_to':
							macd_parameters.elements[macd_elm] = GL_Results[elm][0]
						else:
							macd_parameters.elements[macd_elm] = int(GL_Results[elm][0])

			return GL_Results, path_superhuman, macd_parameters, ind_parameters, pr_parameters, pr_config

		else:
			return pd.DataFrame(), '', '', '', '', ''



	@stTime
	def Simulator(self, dataset_5M, dataset_1H, symbol, signaltype, signalpriority, flag_savepic):


		GL_Results, path_superhuman, macd_parameters, ind_parameters, pr_parameters, pr_config = self.ParameterReader(
										 																				symbol = symbol, 
										 																				signaltype = signaltype, 
										 																				signalpriority = signalpriority
										 																				)

		ind_parameters.elements['dataset_5M'] = dataset_5M
		ind_parameters.elements['dataset_1H'] = dataset_1H
		ind_config = indicator_config()
		macd_tester = Tester(parameters = ind_parameters, config = ind_config)

		self.elements = macd_parameters.elements
		self.elements['dataset_1H'] = dataset_1H
		self.elements['symbol'] = symbol

		cut_first = 0

		output = pd.DataFrame()

		for candle_counter in range(17999, len(dataset_5M[symbol]['close'])):

			if candle_counter >= 17999:
				cut_first = candle_counter - 17999

			self.elements['dataset_5M'] = {
											symbol:	dataset_5M[symbol].loc[cut_first:candle_counter,['close', 'open', 'high', 'low', 'HL/2', 'HLC/3', 'HLCC/4', 'OHLC/4', 'time']],
											}

			macd = Divergence(parameters = ind_parameters, config = ind_config)

			

			signal = pd.DataFrame()

			try:	

				macd_calc = self.calculator_macd()

				signal, _, indicator = macd.divergence(
												sigtype = signaltype,
												sigpriority = signalpriority,
												indicator = macd_calc,
												column_div = GL_Results['MACD_column_div'][0],
												ind_name = 'macd',
												dataset_5M = self.elements['dataset_5M'],
												dataset_1H = dataset_1H,
												symbol = symbol,
												flaglearn = GL_Results['islearned'][0],
												flagtest = True
												)
			except Exception as ex:
				#print(f"LastSignal {signaltype} {signalpriority}: {ex}")
				signal = pd.DataFrame()
			
			if signal.empty == False:
				lst_idx = signal['index'].iloc[-1]
			else:
				lst_idx = 0

			if np.max(self.elements['dataset_5M'][symbol]['close'].index) - 1 - lst_idx <= 6:

				sig = signal.loc[[lst_idx], 
										[
										'index', 
										'indicator_front', 
										'indicator_back', 
										'index_back', 
										'low_front', 
										'low_back', 
										'high_front', 
										'high_back',
										'time_low_front',
										'time_low_back',
										'time_high_front',
										'time_high_back',
										'div',
										'diff_extereme',
										'signal',
										'indicator_name',
										'column_div',
										'symbol'
										]]

				output = pd.concat([output , sig], ignore_index = True)
				print('lst_idx = ', lst_idx)

		with pd.option_context('display.max_rows', None, 'display.max_columns', None):
			print(output)

		signal_output = pd.DataFrame()
		learning_output = pd.DataFrame()

		try:
			signal_output, learning_output = macd_tester.RunGL(
															signal = output, 
															sigtype = signaltype, 
															flaglearn = GL_Results['islearned'][0], 
															flagtest = True,
															pr_parameters = pr_parameters,
															pr_config = pr_config,
															indicator = indicator,
															flag_savepic = flag_savepic
															)

		except Exception as ex:
			print('ERROR PR Last Signal: ',ex)
			signal_output = pd.DataFrame()
			learning_output = pd.DataFrame()

		return signal_output, learning_output


	#@stTime
	def LastSignal(self,dataset_5M, dataset_1H, symbol):

		dataset_5M_real = copy.deepcopy(dataset_5M)

		noise_canceller = NoiseCanceller.NoiseCanceller()
		dataset_5M[symbol]['close'] = noise_canceller.NoiseWavelet(dataset = dataset_5M[symbol].copy(deep = True), applyto = 'close')
		dataset_5M[symbol]['open'] = noise_canceller.NoiseWavelet(dataset = dataset_5M[symbol].copy(deep = True), applyto = 'open')
		dataset_5M[symbol]['high'] = noise_canceller.NoiseWavelet(dataset = dataset_5M[symbol].copy(deep = True), applyto = 'high')
		dataset_5M[symbol]['low'] = noise_canceller.NoiseWavelet(dataset = dataset_5M[symbol].copy(deep = True), applyto = 'low')
		dataset_5M[symbol]['HL/2'] = noise_canceller.NoiseWavelet(dataset = dataset_5M[symbol].copy(deep = True), applyto = 'HL/2')
		dataset_5M[symbol]['HLC/3'] = noise_canceller.NoiseWavelet(dataset = dataset_5M[symbol].copy(deep = True), applyto = 'HLC/3')
		dataset_5M[symbol]['HLCC/4'] = noise_canceller.NoiseWavelet(dataset = dataset_5M[symbol].copy(deep = True), applyto = 'HLCC/4')
		dataset_5M[symbol]['OHLC/4'] = noise_canceller.NoiseWavelet(dataset = dataset_5M[symbol].copy(deep = True), applyto = 'OHLC/4')

		dataset_1H[symbol]['close'] = noise_canceller.NoiseWavelet(dataset = dataset_1H[symbol].copy(deep = True), applyto = 'close')
		dataset_1H[symbol]['open'] = noise_canceller.NoiseWavelet(dataset = dataset_1H[symbol].copy(deep = True), applyto = 'open')
		dataset_1H[symbol]['high'] = noise_canceller.NoiseWavelet(dataset = dataset_1H[symbol].copy(deep = True), applyto = 'high')
		dataset_1H[symbol]['low'] = noise_canceller.NoiseWavelet(dataset = dataset_1H[symbol].copy(deep = True), applyto = 'low')
		dataset_1H[symbol]['HL/2'] = noise_canceller.NoiseWavelet(dataset = dataset_1H[symbol].copy(deep = True), applyto = 'HL/2')
		dataset_1H[symbol]['HLC/3'] = noise_canceller.NoiseWavelet(dataset = dataset_1H[symbol].copy(deep = True), applyto = 'HLC/3')
		dataset_1H[symbol]['HLCC/4'] = noise_canceller.NoiseWavelet(dataset = dataset_1H[symbol].copy(deep = True), applyto = 'HLCC/4')
		dataset_1H[symbol]['OHLC/4'] = noise_canceller.NoiseWavelet(dataset = dataset_1H[symbol].copy(deep = True), applyto = 'OHLC/4')

		#BUY Primary:

		signaltype = 'buy'
		signalpriority = 'primary'

		macd_config = MACDConfig()
		path_superhuman = macd_config.cfg['path_superhuman'] + signalpriority + path_slash + signaltype + path_slash

		if not os.path.exists(path_superhuman + symbol + '.csv'): return 'no_trade', 0, 0

		GL_Results_buy_primary, path_superhuman, macd_parameters, ind_parameters, pr_parameters_buy_primary, pr_config_buy_primary = self.ParameterReader(
												 																				symbol = symbol, 
												 																				signaltype = signaltype, 
												 																				signalpriority = signalpriority
												 																				)

		ind_config = indicator_config()
		macd = Divergence(parameters = ind_parameters, config = ind_config)

		self.elements = macd_parameters.elements
		self.elements['dataset_5M'] = dataset_5M
		self.elements['dataset_1H'] = dataset_1H
		self.elements['symbol'] = symbol

		macd_calc_buy_primary = self.calculator_macd()

		signal_buy_primary = pd.DataFrame()

		try:

			if GL_Results_buy_primary['permit'][0] == True:

				signal_buy_primary, _, _ = macd.divergence(
															sigtype = signaltype,
															sigpriority = signalpriority,
															indicator = macd_calc_buy_primary,
															column_div = GL_Results_buy_primary['MACD_column_div'][0],
															ind_name = 'macd',
															dataset_5M = dataset_5M,
															dataset_1H = dataset_1H,
															symbol = symbol,
															flaglearn = GL_Results_buy_primary['islearned'][0],
															flagtest = False
															)
			else:
				lst_idx_buy_primary = 0
				signal_buy_primary = pd.DataFrame()

		except Exception as ex:
			print(f"LastSignal {signaltype} {signalpriority}: {ex}")
			signal_buy_primary = pd.DataFrame()

		if signal_buy_primary.empty == False:
			lst_idx_buy_primary = int(signal_buy_primary['index'].iloc[-1])

		else:
			lst_idx_buy_primary = 0

		#*****************************


		#BUY Secondry:

		signaltype = 'buy'
		signalpriority = 'secondry'

		GL_Results_buy_secondry, path_superhuman, macd_parameters, ind_parameters, pr_parameters_buy_secondry, pr_config_buy_secondry = self.ParameterReader(
													 																				symbol = symbol, 
													 																				signaltype = signaltype, 
													 																				signalpriority = signalpriority
													 																				)

		ind_config = indicator_config()
		macd = Divergence(parameters = ind_parameters, config = ind_config)

		self.elements = macd_parameters.elements
		self.elements['dataset_5M'] = dataset_5M
		self.elements['dataset_1H'] = dataset_1H
		self.elements['symbol'] = symbol

		macd_calc_buy_secondry = self.calculator_macd()

		signal_buy_secondry = pd.DataFrame()

		try:

			if GL_Results_buy_secondry['permit'][0] == True:
				
				signal_buy_secondry, _, _ = macd.divergence(
															sigtype = signaltype,
															sigpriority = signalpriority,
															indicator = macd_calc_buy_secondry,
															column_div = GL_Results_buy_secondry['MACD_column_div'][0],
															ind_name = 'macd',
															dataset_5M = dataset_5M,
															dataset_1H = dataset_1H,
															symbol = symbol,
															flaglearn = GL_Results_buy_secondry['islearned'][0],
															flagtest = False
															)
			else:
				signal_buy_secondry = 0
				signal_buy_secondry = pd.DataFrame()

		except Exception as ex:
			print(f"LastSignal {signaltype} {signalpriority}: {ex}")
			signal_buy_secondry = pd.DataFrame()

		if signal_buy_secondry.empty == False:
			lst_idx_buy_secondry = int(signal_buy_secondry['index'].iloc[-1])

		else:
			lst_idx_buy_secondry = 0

		#*****************************


		#SELL Primary:

		signaltype = 'sell'
		signalpriority = 'primary'

		GL_Results_sell_primary, path_superhuman, macd_parameters, ind_parameters, pr_parameters_sell_primary, pr_config_sell_primary = self.ParameterReader(
													 																				symbol = symbol, 
													 																				signaltype = signaltype, 
													 																				signalpriority = signalpriority
													 																				)

		ind_config = indicator_config()
		macd = Divergence(parameters = ind_parameters, config = ind_config)

		self.elements = macd_parameters.elements
		self.elements['dataset_5M'] = dataset_5M
		self.elements['dataset_1H'] = dataset_1H
		self.elements['symbol'] = symbol

		macd_calc_sell_primary = self.calculator_macd()

		signal_sell_primary = pd.DataFrame()

		try:
			if GL_Results_sell_primary['permit'][0] == True:

				signal_sell_primary, _, _ = macd.divergence(
															sigtype = signaltype,
															sigpriority = signalpriority,
															indicator = macd_calc_sell_primary,
															column_div = GL_Results_sell_primary['MACD_column_div'][0],
															ind_name = 'macd',
															dataset_5M = dataset_5M,
															dataset_1H = dataset_1H,
															symbol = symbol,
															flaglearn = GL_Results_sell_primary['islearned'][0],
															flagtest = False
															)
			else:
				lst_idx_sell_primary = 0
				signal_sell_primary = pd.DataFrame()

		except Exception as ex:
			print(f"LastSignal {signaltype} {signalpriority}: {ex}")
			signal_sell_primary = pd.DataFrame()

		if signal_sell_primary.empty == False:
			lst_idx_sell_primary = int(signal_sell_primary['index'].iloc[-1])

		else:
			lst_idx_sell_primary = 0

		#*****************************


		#SELL Secondry:

		signaltype = 'sell'
		signalpriority = 'secondry'

		GL_Results_sell_secondry, path_superhuman, macd_parameters, ind_parameters, pr_parameters_sell_secondry, pr_config_sell_secondry = self.ParameterReader(
													 																				symbol = symbol, 
													 																				signaltype = signaltype, 
													 																				signalpriority = signalpriority
													 																				)

		ind_config = indicator_config()
		macd = Divergence(parameters = ind_parameters, config = ind_config)

		self.elements = macd_parameters.elements
		self.elements['dataset_5M'] = dataset_5M
		self.elements['dataset_1H'] = dataset_1H
		self.elements['symbol'] = symbol

		macd_calc_sell_secondry = self.calculator_macd()

		signal_sell_secondry = pd.DataFrame()

		try:
			if GL_Results_sell_secondry['permit'][0] == True:

				signal_sell_secondry, _, _ = macd.divergence(
															sigtype = signaltype,
															sigpriority = signalpriority,
															indicator = macd_calc_sell_secondry,
															column_div = GL_Results_sell_secondry['MACD_column_div'][0],
															ind_name = 'macd',
															dataset_5M = dataset_5M,
															dataset_1H = dataset_1H,
															symbol = symbol,
															flaglearn = GL_Results_sell_secondry['islearned'][0],
															flagtest = False
															)
			else:
				lst_idx_sell_secondry = 0
				signal_sell_secondry = pd.DataFrame()

		except Exception as ex:
			print(f"LastSignal {signaltype} {signalpriority}: {ex}")
			signal_sell_secondry = pd.DataFrame()


		if signal_sell_secondry.empty == False:
			lst_idx_sell_secondry = int(signal_sell_secondry['index'].iloc[-1])

		else:
			lst_idx_sell_secondry = 0

		#*****************************

		# print('lst_idx_buy_primary macd = ', lst_idx_buy_primary)
		# print('lst_idx_buy_secondry macd = ', lst_idx_buy_secondry)
		# print('lst_idx_sell_primary macd = ', lst_idx_sell_primary)
		# print('lst_idx_sell_secondry macd = ', lst_idx_sell_secondry)
		# print('len data = ', len(dataset_5M[symbol]['close']) - 1)

		#***** Last Signal:

		if (
			lst_idx_buy_primary > lst_idx_sell_primary and
			lst_idx_buy_primary > lst_idx_sell_secondry and
			lst_idx_buy_primary >= lst_idx_buy_secondry and
			(len(dataset_5M_real[symbol]['close']) - 1 - lst_idx_buy_primary) <= 6 and
			(len(dataset_5M_real[symbol]['close']) - 1 - lst_idx_buy_primary) >= 2
			):

			# SMA_50 = ind.sma(dataset_5M[symbol]['close'], length = 50)
			# SMA_25 = ind.sma(dataset_5M[symbol]['close'], length = 25)

			# zigzag = ZigZag.Find(
			# 						dataset = dataset_5M_real, 
			# 						index_first = int(signal_buy_primary['index_back'][lst_idx_buy_primary]), 
			# 						index_last = len(dataset_5M_real.index)
			# 						)

			if (
				macd_calc_buy_primary[GL_Results_buy_primary['MACD_column_div'][0]][lst_idx_buy_primary] < macd_calc_buy_primary[GL_Results_buy_primary['MACD_column_div'][0]][lst_idx_buy_primary + 1] and
				macd_calc_buy_primary[GL_Results_buy_primary['MACD_column_div'][0]][lst_idx_buy_primary] < macd_calc_buy_primary[GL_Results_buy_primary['MACD_column_div'][0]][lst_idx_buy_primary + 2] and
				macd_calc_buy_primary[GL_Results_buy_primary['MACD_column_div'][0]][lst_idx_buy_primary] < macd_calc_buy_primary[GL_Results_buy_primary['MACD_column_div'][0]][lst_idx_buy_primary - 1] and
				macd_calc_buy_primary[GL_Results_buy_primary['MACD_column_div'][0]][lst_idx_buy_primary] < macd_calc_buy_primary[GL_Results_buy_primary['MACD_column_div'][0]][lst_idx_buy_primary - 2] and
				dataset_5M_real[symbol]['low'][signal_buy_primary['index_back'][lst_idx_buy_primary]] > dataset_5M_real[symbol]['low'][lst_idx_buy_primary]
				# dataset_5M_real[symbol]['low'].iloc[-1] > np.mean(SMA_50[int(signal_buy_primary['index_back'][lst_idx_buy_primary]): ]) and
				# SMA_25.iloc[-1] >= SMA_50.iloc[-1] and
				# zigzag.values[-2] < dataset_5M_real['low'].iloc[-1]
				):
				# print('======> last signal buy primary macd ',symbol)
				# print('dataset length: ',len(dataset_5M[symbol]['close']))
				# print('last index: ',lst_idx_buy_primary)
				

				if lst_idx_buy_primary != 0:

					res_pro_buy_primary = pd.DataFrame()
					try:
						res_pro_buy_primary = self.ProfitFinder(
																dataset_5M = dataset_5M,
																dataset_1H = dataset_1H,
																symbol = symbol,
																signal = signal_buy_primary, 
																sigtype = 'buy', 
																pr_parameters = pr_parameters_buy_primary, 
																pr_config = pr_config_buy_primary
																)
					except Exception as ex:
						print('ERROR PR Last Signal: ',ex)
						res_pro_buy_primary = pd.DataFrame(np.zeros(int(lst_idx_buy_primary) + 1))
						res_pro_buy_primary['high_upper'] = np.nan
						res_pro_buy_primary['low_lower'] = np.nan


					if (res_pro_buy_primary.empty == False):

						diff_pr_top_buy_primary = (((res_pro_buy_primary['high_upper'][int(lst_idx_buy_primary)]) - dataset_5M_real[symbol]['high'][int(lst_idx_buy_primary)])/dataset_5M_real[symbol]['high'][int(lst_idx_buy_primary)]) * 100
						diff_pr_down_buy_primary = ((dataset_5M_real[symbol]['low'][int(lst_idx_buy_primary)] - (res_pro_buy_primary['low_lower'][int(lst_idx_buy_primary)]))/dataset_5M_real[symbol]['low'][int(lst_idx_buy_primary)]) * 100

						# if type(diff_pr_down_buy_primary) is np.ndarray:
						# 	res_pro_buy_primary['low_lower'][int(lst_idx_buy_primary)] = dataset_5M[symbol]['low'][int(lst_idx_buy_primary)]*(1-(diff_pr_down_buy_primary[0]/100))
						# else:
						# 	res_pro_buy_primary['low_lower'][int(lst_idx_buy_primary)] = dataset_5M[symbol]['low'][int(lst_idx_buy_primary)]*(1-(diff_pr_down_buy_primary/100))

						if diff_pr_top_buy_primary > pr_parameters_buy_primary.elements['tp_percent_max']:
							diff_pr_top_buy_primary = pr_parameters_buy_primary.elements['tp_percent_max']
							res_pro_buy_primary['high_upper'][int(lst_idx_buy_primary)] = dataset_5M_real[symbol]['high'][int(lst_idx_buy_primary)]*(1+(diff_pr_top_buy_primary/100))

						if diff_pr_down_buy_primary > pr_parameters_buy_primary.elements['st_percent_max']:
							diff_pr_down_buy_primary = pr_parameters_buy_primary.elements['st_percent_max']
							res_pro_buy_primary['low_lower'][int(lst_idx_buy_primary)] = dataset_5M_real[symbol]['low'][int(lst_idx_buy_primary)]*(1-(diff_pr_down_buy_primary/100))


						resist_buy = (res_pro_buy_primary['high_upper'][int(lst_idx_buy_primary)])
						protect_buy = (res_pro_buy_primary['low_lower'][int(lst_idx_buy_primary)])

						signal = 'buy_primary'

					else:
						res_pro_buy_primary = pd.DataFrame(np.zeros(int(lst_idx_buy_primary) + 1))
						res_pro_buy_primary['high_upper'] = np.nan
						res_pro_buy_primary['low_lower'] = np.nan

						diff_pr_top_buy_primary = pr_parameters_buy_primary.elements['tp_percent_min']
						res_pro_buy_primary['high_upper'][int(lst_idx_buy_primary)] = dataset_5M_real[symbol]['high'][int(lst_idx_buy_primary)]*(1+(diff_pr_top_buy_primary/100))

						diff_pr_down_buy_primary = pr_parameters_buy_primary.elements['st_percent_min']
						res_pro_buy_primary['low_lower'][int(lst_idx_buy_primary)] = dataset_5M_real[symbol]['low'][int(lst_idx_buy_primary)]*(1-(diff_pr_down_buy_primary/100))

						resist_buy = (res_pro_buy_primary['high_upper'][int(lst_idx_buy_primary)])
						protect_buy = (res_pro_buy_primary['low_lower'][int(lst_idx_buy_primary)])

						signal = 'buy_primary'

						# diff_pr_top_buy = 0
						# diff_pr_down_buy = 0
						# diff_pr_top_buy_power = 0
						# diff_pr_down_buy_power = 0

						# resist_buy = 0
						# protect_buy = 0

						# signal = 'no_trade'		

				else:
					resist_sell = 0
					protect_sell = 0

					signal = 'no_trade'	

			else:
				resist_sell = 0
				protect_sell = 0

				signal = 'no_trade'	

				# print('================================')\

		elif (
			lst_idx_buy_secondry > lst_idx_sell_primary and
			lst_idx_buy_secondry > lst_idx_sell_secondry and
			lst_idx_buy_secondry > lst_idx_buy_primary and
			(len(dataset_5M_real[symbol]['close']) - 1 - lst_idx_buy_secondry) <= 6 and
			(len(dataset_5M_real[symbol]['close']) - 1 - lst_idx_buy_secondry) >= 2
			):

			# SMA_50 = ind.sma(dataset_5M[symbol]['close'], length = 50)
			# SMA_25 = ind.sma(dataset_5M[symbol]['close'], length = 25)

			# zigzag = ZigZag.Find(
			# 						dataset = dataset_5M_real, 
			# 						index_first = int(signal_buy_secondry['index_back'][lst_idx_buy_secondry]), 
			# 						index_last = len(dataset_5M_real.index)
			# 						)

			if (
				macd_calc_buy_secondry[GL_Results_buy_secondry['MACD_column_div'][0]][lst_idx_buy_secondry] < macd_calc_buy_secondry[GL_Results_buy_secondry['MACD_column_div'][0]][lst_idx_buy_secondry + 1] and
				macd_calc_buy_secondry[GL_Results_buy_secondry['MACD_column_div'][0]][lst_idx_buy_secondry] < macd_calc_buy_secondry[GL_Results_buy_secondry['MACD_column_div'][0]][lst_idx_buy_secondry + 2] and
				macd_calc_buy_secondry[GL_Results_buy_secondry['MACD_column_div'][0]][lst_idx_buy_secondry] < macd_calc_buy_secondry[GL_Results_buy_secondry['MACD_column_div'][0]][lst_idx_buy_secondry - 1] and
				macd_calc_buy_secondry[GL_Results_buy_secondry['MACD_column_div'][0]][lst_idx_buy_secondry] < macd_calc_buy_secondry[GL_Results_buy_secondry['MACD_column_div'][0]][lst_idx_buy_secondry - 2] and
				dataset_5M_real[symbol]['low'][signal_buy_secondry['index_back'][lst_idx_buy_secondry]] < dataset_5M_real[symbol]['low'][lst_idx_buy_secondry]
				# dataset_5M_real[symbol]['low'].iloc[-1] > np.mean(SMA_50[int(signal_buy_secondry['index_back'][lst_idx_buy_secondry]): ]) and
				# SMA_25.iloc[-1] >= SMA_50.iloc[-1] and
				# zigzag.values[-2] < dataset_5M_real['low'].iloc[-1]
				):
				# print('======> last signal buy secondry macd ',symbol)
				# print('dataset length: ',len(dataset_5M[symbol]['close']))
				# print('last index: ',lst_idx_buy_secondry)
				


				if lst_idx_buy_secondry != 0:

					res_pro_buy_secondry = pd.DataFrame()
					try:
						res_pro_buy_secondry = self.ProfitFinder(
																dataset_5M = dataset_5M,
																dataset_1H = dataset_1H,
																symbol = symbol,
																signal = signal_buy_secondry, 
																sigtype = 'buy', 
																pr_parameters = pr_parameters_buy_secondry, 
																pr_config = pr_config_buy_secondry
																)
					except Exception as ex:
						print('ERROR PR Last Signal: ',ex)
						res_pro_buy_secondry = pd.DataFrame(np.zeros(int(lst_idx_buy_secondry) + 1))
						res_pro_buy_secondry['high_upper'] = np.nan
						res_pro_buy_secondry['low_lower'] = np.nan

					if (res_pro_buy_secondry.empty == False):

						diff_pr_top_buy_secondry = (((res_pro_buy_secondry['high_upper'][int(lst_idx_buy_secondry)]) - dataset_5M_real[symbol]['high'][int(lst_idx_buy_secondry)])/dataset_5M_real[symbol]['high'][int(lst_idx_buy_secondry)]) * 100
						diff_pr_down_buy_secondry = ((dataset_5M_real[symbol]['low'][int(lst_idx_buy_secondry)] - (res_pro_buy_secondry['low_lower'][int(lst_idx_buy_secondry)]))/dataset_5M_real[symbol]['low'][int(lst_idx_buy_secondry)]) * 100

						# if type(diff_pr_down_buy_primary) is np.ndarray:
						# 	res_pro_buy_primary['low_lower'][int(lst_idx_buy_primary)] = dataset_5M[symbol]['low'][int(lst_idx_buy_primary)]*(1-(diff_pr_down_buy_primary[0]/100))
						# else:
						# 	res_pro_buy_primary['low_lower'][int(lst_idx_buy_primary)] = dataset_5M[symbol]['low'][int(lst_idx_buy_primary)]*(1-(diff_pr_down_buy_primary/100))

						if diff_pr_top_buy_secondry > pr_parameters_buy_secondry.elements['tp_percent_max']:
							diff_pr_top_buy_secondry = pr_parameters_buy_secondry.elements['tp_percent_max']
							res_pro_buy_secondry['high_upper'][int(lst_idx_buy_secondry)] = dataset_5M_real[symbol]['high'][int(lst_idx_buy_secondry)]*(1+(diff_pr_top_buy_secondry/100))

						if diff_pr_down_buy_secondry > pr_parameters_buy_secondry.elements['st_percent_max']:
							diff_pr_down_buy_secondry = pr_parameters_buy_secondry.elements['st_percent_max']
							res_pro_buy_secondry['low_lower'][int(lst_idx_buy_secondry)] = dataset_5M_real[symbol]['low'][int(lst_idx_buy_secondry)]*(1-(diff_pr_down_buy_secondry/100))


						resist_buy = (res_pro_buy_secondry['high_upper'][int(lst_idx_buy_secondry)])
						protect_buy = (res_pro_buy_secondry['low_lower'][int(lst_idx_buy_secondry)])

						signal = 'buy_secondry'

					else:

						res_pro_buy_secondry = pd.DataFrame(np.zeros(int(lst_idx_buy_secondry) + 1))
						res_pro_buy_secondry['high_upper'] = np.nan
						res_pro_buy_secondry['low_lower'] = np.nan

						diff_pr_top_buy_secondry = pr_parameters_buy_secondry.elements['tp_percent_min']
						res_pro_buy_secondry['high_upper'][int(lst_idx_buy_secondry)] = dataset_5M_real[symbol]['high'][int(lst_idx_buy_secondry)]*(1+(diff_pr_top_buy_secondry/100))

						diff_pr_down_buy_secondry = pr_parameters_buy_secondry.elements['st_percent_min']
						res_pro_buy_secondry['low_lower'][int(lst_idx_buy_secondry)] = dataset_5M_real[symbol]['low'][int(lst_idx_buy_secondry)]*(1-(diff_pr_down_buy_secondry/100))


						resist_buy = (res_pro_buy_secondry['high_upper'][int(lst_idx_buy_secondry)])
						protect_buy = (res_pro_buy_secondry['low_lower'][int(lst_idx_buy_secondry)])

						signal = 'buy_secondry'

						# diff_pr_top_buy = 0
						# diff_pr_down_buy = 0
						# diff_pr_top_buy_power = 0
						# diff_pr_down_buy_power = 0

						# resist_buy = 0
						# protect_buy = 0

						# signal = 'no_trade'	

				else:
					resist_sell = 0
					protect_sell = 0

					signal = 'no_trade'	

			else:
				resist_sell = 0
				protect_sell = 0

				signal = 'no_trade'	

		elif (
			lst_idx_sell_primary > lst_idx_buy_primary and
			lst_idx_sell_primary >= lst_idx_sell_secondry and
			lst_idx_sell_primary > lst_idx_buy_secondry and
			(len(dataset_5M_real[symbol]['close']) - 1 - lst_idx_sell_primary) <= 6 and
			(len(dataset_5M_real[symbol]['close']) - 1 - lst_idx_sell_primary) >= 2
			):

			# SMA_50 = ind.sma(dataset_5M[symbol]['close'], length = 50)
			# SMA_25 = ind.sma(dataset_5M[symbol]['close'], length = 25)

			# zigzag = ZigZag.Find(
			# 						dataset = dataset_5M_real, 
			# 						index_first = int(signal_sell_primary['index_back'][lst_idx_sell_primary]), 
			# 						index_last = len(dataset_5M_real.index)
			# 						)

			if (
				macd_calc_sell_primary[GL_Results_sell_primary['MACD_column_div'][0]][lst_idx_sell_primary] > macd_calc_sell_primary[GL_Results_sell_primary['MACD_column_div'][0]][lst_idx_sell_primary + 1] and
				macd_calc_sell_primary[GL_Results_sell_primary['MACD_column_div'][0]][lst_idx_sell_primary] > macd_calc_sell_primary[GL_Results_sell_primary['MACD_column_div'][0]][lst_idx_sell_primary + 2] and
				macd_calc_sell_primary[GL_Results_sell_primary['MACD_column_div'][0]][lst_idx_sell_primary] > macd_calc_sell_primary[GL_Results_sell_primary['MACD_column_div'][0]][lst_idx_sell_primary - 1] and
				macd_calc_sell_primary[GL_Results_sell_primary['MACD_column_div'][0]][lst_idx_sell_primary] > macd_calc_sell_primary[GL_Results_sell_primary['MACD_column_div'][0]][lst_idx_sell_primary - 2] and
				dataset_5M_real[symbol]['high'][signal_sell_primary['index_back'][lst_idx_sell_primary]] < dataset_5M_real[symbol]['high'][lst_idx_sell_primary]
				# dataset_5M_real[symbol]['high'].iloc[-1] < np.mean(SMA_50[int(signal_sell_primary['index_back'][lst_idx_sell_primary]): ]) and
				# SMA_25.iloc[-1] <= SMA_50.iloc[-1] and
				# zigzag.values[-2] > dataset_5M_real['high'].iloc[-1]
				):
				# print('======> last signal sell primary macd ',symbol)
				# print('dataset length: ',len(dataset_5M_real[symbol]['close']))
				# print('last index: ',lst_idx_sell_primary)
				

				if lst_idx_sell_primary != 0:

					res_pro_sell_primary = pd.DataFrame()
					try:
						res_pro_sell_primary = self.ProfitFinder(
																dataset_5M = dataset_5M,
																dataset_1H = dataset_1H,
																symbol = symbol,
																signal = signal_sell_primary, 
																sigtype = 'sell', 
																pr_parameters = pr_parameters_sell_primary, 
																pr_config = pr_config_sell_primary
																)
					except Exception as ex:
						# print('ERROR PR Last Signal: ',ex)
						res_pro_sell_primary = pd.DataFrame(np.zeros(int(lst_idx_sell_primary) + 1))
						res_pro_sell_primary['high_upper'] = np.nan
						res_pro_sell_primary['low_lower'] = np.nan


					if (res_pro_sell_primary.empty == False):

						diff_pr_top_sell_primary = (((res_pro_sell_primary['high_upper'][int(lst_idx_sell_primary)]) - dataset_5M_real[symbol]['high'][int(lst_idx_sell_primary)])/dataset_5M_real[symbol]['high'][int(lst_idx_sell_primary)]) * 100
						diff_pr_down_sell_primary = ((dataset_5M_real[symbol]['low'][int(lst_idx_sell_primary)] - (res_pro_sell_primary['low_lower'][int(lst_idx_sell_primary)]))/dataset_5M_real[symbol]['low'][int(lst_idx_sell_primary)]) * 100


						if diff_pr_top_sell_primary > pr_parameters_sell_primary.elements['st_percent_max']:
							diff_pr_top_sell_primary = pr_parameters_sell_primary.elements['st_percent_max']
							(res_pro_sell_primary['high_upper'][int(lst_idx_sell_primary)]) = dataset_5M_real[symbol]['high'][int(lst_idx_sell_primary)]*(1+(diff_pr_top_sell_primary/100))

						if diff_pr_down_sell_primary > pr_parameters_sell_primary.elements['tp_percent_max']:
							diff_pr_down_sell_primary = pr_parameters_sell_primary.elements['tp_percent_max']
							(res_pro_sell_primary['low_lower'][int(lst_idx_sell_primary)]) = dataset_5M_real[symbol]['low'][int(lst_idx_sell_primary)]*(1-(diff_pr_down_sell_primary/100))
							

						resist_sell = (res_pro_sell_primary['high_upper'][int(lst_idx_sell_primary)])
						protect_sell = (res_pro_sell_primary['low_lower'][int(lst_idx_sell_primary)])

						signal = 'sell_primary'

					else:

						res_pro_sell_primary = pd.DataFrame(np.zeros(int(lst_idx_sell_primary) + 1))
						res_pro_sell_primary['high_upper'] = np.nan
						res_pro_sell_primary['low_lower'] = np.nan

						diff_pr_top_sell_primary = pr_parameters_sell_primary.elements['st_percent_min']
						(res_pro_sell_primary['high_upper'][int(lst_idx_sell_primary)]) = dataset_5M_real[symbol]['high'][int(lst_idx_sell_primary)]*(1+(diff_pr_top_sell_primary/100))

						diff_pr_down_sell_primary = pr_parameters_sell_primary.elements['tp_percent_min']
						(res_pro_sell_primary['low_lower'][int(lst_idx_sell_primary)]) = dataset_5M_real[symbol]['low'][int(lst_idx_sell_primary)]*(1-(diff_pr_down_sell_primary/100))
							
						resist_sell = (res_pro_sell_primary['high_upper'][int(lst_idx_sell_primary)])
						protect_sell = (res_pro_sell_primary['low_lower'][int(lst_idx_sell_primary)])

						signal = 'sell_primary'

						# diff_pr_top_sell_primary = 0
						# diff_pr_down_sell_primary = 0

						# resist_sell = 0
						# protect_sell = 0

						# signal = 'no_trade'

				else:
					resist_sell = 0
					protect_sell = 0

					signal = 'no_trade'	

			else:
				resist_sell = 0
				protect_sell = 0

				signal = 'no_trade'	

		
		elif (
			lst_idx_sell_secondry > lst_idx_buy_primary and
			lst_idx_sell_secondry > lst_idx_sell_primary and
			lst_idx_sell_secondry > lst_idx_buy_secondry and
			(len(dataset_5M_real[symbol]['close']) - 1 - lst_idx_sell_secondry) <= 6 and
			(len(dataset_5M_real[symbol]['close']) - 1 - lst_idx_sell_secondry) >= 2
			):

			# SMA_50 = ind.sma(dataset_5M[symbol]['close'], length = 50)
			# SMA_25 = ind.sma(dataset_5M[symbol]['close'], length = 25)

			# zigzag = ZigZag.Find(
			# 						dataset = dataset_5M_real, 
			# 						index_first = int(signal_sell_secondry['index_back'][lst_idx_sell_secondry]), 
			# 						index_last = len(dataset_5M_real.index)
			# 						)

			if (
				macd_calc_sell_secondry[GL_Results_sell_secondry['MACD_column_div'][0]][lst_idx_sell_secondry] > macd_calc_sell_secondry[GL_Results_sell_secondry['MACD_column_div'][0]][lst_idx_sell_secondry + 1] and
				macd_calc_sell_secondry[GL_Results_sell_secondry['MACD_column_div'][0]][lst_idx_sell_secondry] > macd_calc_sell_secondry[GL_Results_sell_secondry['MACD_column_div'][0]][lst_idx_sell_secondry + 2] and
				macd_calc_sell_secondry[GL_Results_sell_secondry['MACD_column_div'][0]][lst_idx_sell_secondry] > macd_calc_sell_secondry[GL_Results_sell_secondry['MACD_column_div'][0]][lst_idx_sell_secondry - 1] and
				macd_calc_sell_secondry[GL_Results_sell_secondry['MACD_column_div'][0]][lst_idx_sell_secondry] > macd_calc_sell_secondry[GL_Results_sell_secondry['MACD_column_div'][0]][lst_idx_sell_secondry - 2] and
				dataset_5M_real[symbol]['high'][signal_sell_secondry['index_back'][lst_idx_sell_secondry]] > dataset_5M_real[symbol]['high'][lst_idx_sell_secondry]
				# dataset_5M_real[symbol]['high'].iloc[-1] < np.mean(SMA_50[int(signal_sell_secondry['index_back'][lst_idx_sell_secondry]): ]) and
				# SMA_25.iloc[-1] <= SMA_50.iloc[-1] and
				# zigzag.values[-2] > dataset_5M_real['high'].iloc[-1]
				):

				# print('======> last signal sell secondry macd ',symbol)
				# print('dataset length: ',len(dataset_5M[symbol]['close']))
				# print('last index: ',lst_idx_sell_secondry)

				if lst_idx_sell_secondry != 0:

					res_pro_sell_secondry = pd.DataFrame()
					try:
						res_pro_sell_secondry = self.ProfitFinder(
																dataset_5M = dataset_5M,
																dataset_1H = dataset_1H,
																symbol = symbol,
																signal = signal_sell_secondry, 
																sigtype = 'sell', 
																pr_parameters = pr_parameters_sell_secondry, 
																pr_config = pr_config_sell_secondry
																)
					except Exception as ex:
						print('ERROR PR Last Signal: ',ex)
						res_pro_sell_secondry = pd.DataFrame(np.zeros(int(lst_idx_sell_secondry) + 1))
						res_pro_sell_secondry['high_upper'] = np.nan
						res_pro_sell_secondry['low_lower'] = np.nan


					if (res_pro_sell_secondry.empty == False):

						diff_pr_top_sell_secondry = (((res_pro_sell_secondry['high_upper'][int(lst_idx_sell_secondry)]) - dataset_5M_real[symbol]['high'][int(lst_idx_sell_secondry)])/dataset_5M_real[symbol]['high'][int(lst_idx_sell_secondry)]) * 100
						diff_pr_down_sell_secondry = ((dataset_5M_real[symbol]['low'][int(lst_idx_sell_secondry)] - (res_pro_sell_secondry['low_lower'][int(lst_idx_sell_secondry)]))/dataset_5M_real[symbol]['low'][int(lst_idx_sell_secondry)]) * 100


						if diff_pr_top_sell_secondry > pr_parameters_sell_secondry.elements['st_percent_max']:
							diff_pr_top_sell_secondry = pr_parameters_sell_secondry.elements['st_percent_max']
							(res_pro_sell_secondry['high_upper'][int(lst_idx_sell_secondry)]) = dataset_5M_real[symbol]['high'][int(lst_idx_sell_secondry)]*(1+(diff_pr_top_sell_secondry/100))

						if diff_pr_down_sell_secondry > pr_parameters_sell_secondry.elements['tp_percent_max']:
							diff_pr_down_sell_secondry = pr_parameters_sell_secondry.elements['tp_percent_max']
							(res_pro_sell_secondry['low_lower'][int(lst_idx_sell_secondry)]) = dataset_5M_real[symbol]['low'][int(lst_idx_sell_secondry)]*(1-(diff_pr_down_sell_secondry/100))
							

						resist_sell = (res_pro_sell_secondry['high_upper'][int(lst_idx_sell_secondry)])
						protect_sell = (res_pro_sell_secondry['low_lower'][int(lst_idx_sell_secondry)])
						
						signal = 'sell_secondry'

					else:

						res_pro_sell_secondry = pd.DataFrame(np.zeros(int(lst_idx_sell_secondry) + 1))
						res_pro_sell_secondry['high_upper'] = np.nan
						res_pro_sell_secondry['low_lower'] = np.nan
						
						diff_pr_top_sell_secondry = pr_parameters_sell_secondry.elements['st_percent_min']
						(res_pro_sell_secondry['high_upper'][int(lst_idx_sell_secondry)]) = dataset_5M_real[symbol]['high'][int(lst_idx_sell_secondry)]*(1+(diff_pr_top_sell_secondry/100))

						diff_pr_down_sell_secondry = pr_parameters_sell_secondry.elements['tp_percent_min']
						(res_pro_sell_secondry['low_lower'][int(lst_idx_sell_secondry)]) = dataset_5M_real[symbol]['low'][int(lst_idx_sell_secondry)]*(1-(diff_pr_down_sell_secondry/100))
							
						resist_sell = (res_pro_sell_secondry['high_upper'][int(lst_idx_sell_secondry)])
						protect_sell = (res_pro_sell_secondry['low_lower'][int(lst_idx_sell_secondry)])
						
						signal = 'sell_secondry'

						# diff_pr_top_sell_secondry = 0
						# diff_pr_down_sell_secondry = 0

						# resist_sell = 0
						# protect_sell = 0

						# signal = 'no_trade'		

				else:
					resist_sell = 0
					protect_sell = 0

					signal = 'no_trade'	

			else:
				resist_sell = 0
				protect_sell = 0

				signal = 'no_trade'		

				# print('================================')
		else:
			resist_sell = 0
			protect_sell = 0

			signal = 'no_trade'	

		if (
			signal == 'buy_primary' or
			signal == 'buy_secondry'
			):
			return signal, resist_buy, protect_buy
		elif (
			signal == 'sell_primary' or
			signal == 'sell_secondry'
			):
			return signal, protect_sell, resist_sell
		else:
			return signal, 0, 0


	#ProfitFinder For Last Signal:

	def ProfitFinder(self, dataset_5M,dataset_1H, symbol, signal, sigtype, pr_parameters, pr_config):

		#*************************************************************
		# Bayad Maghadir Baraye Params Va Config As func baraye PR dar GA , Learner daryaft beshan

		#/////////////////////////////////////////////////////////////

		pr_Runner = Runner(parameters = pr_parameters, config = pr_config)

		# with pd.option_context('display.max_rows', None, 'display.max_columns', None):
		# 	print('sig1 = ',signal['index'].iloc[-1])

		signals = pd.DataFrame(
								{
									'index': signal['index'].iloc[-1], 
								},
								index = [signal['index'].iloc[-1]]
								)

		# with pd.option_context('display.max_rows', None, 'display.max_columns', None):
		# 	print('sig1 = ',signals)

		signals = pr_Runner.run(
								dataset_5M = dataset_5M[symbol], 
								dataset_1H = dataset_1H[symbol],
								signals_index = signals,
								sigtype = sigtype,
								flaglearn = True,
								flagtest = False,
								indicator = 'macd',
								signals = signal,
								flag_savepic = False
								)

		# with pd.option_context('display.max_rows', None, 'display.max_columns', None):
		# 	print('sig2 = ',signal)

		signal = signal.drop(columns = ['index'], inplace = False)

		signal = signal.join(signals).dropna(inplace = False)

		# with pd.option_context('display.max_rows', None, 'display.max_columns', None):
		# 	print('sig2 = ',signal)

		return signal


	#/////////////////////////////





	def GetPermit(self, dataset_5M_real, dataset_5M, dataset_1H, symbol, signaltype, signalpriority, flag_savepic):

		GL_Results, path_superhuman, macd_parameters, ind_parameters, pr_parameters, pr_config = self.ParameterReader(
									 																				symbol = symbol, 
									 																				signaltype = signaltype, 
									 																				signalpriority = signalpriority
									 																				)

		pr_config.cfg['Tester_flag_realtest'] = True
		
		ind_config = indicator_config()
		macd = Divergence(parameters = ind_parameters, config = ind_config)

		# with pd.option_context('display.max_rows', None, 'display.max_columns', None):
		# 	print(dataset_5M[symbol].head(20))

		ind_parameters.elements['dataset_5M'] = dataset_5M.copy()
		ind_parameters.elements['dataset_1H'] = dataset_1H.copy()
		macd_tester = Tester(parameters = ind_parameters, config = ind_config)

		self.elements = macd_parameters.elements
		self.elements['dataset_5M'] = dataset_5M.copy()
		# self.elements['dataset_5M'][symbol] = dataset_5M[symbol].copy(deep = True)
		self.elements['dataset_1H'] = dataset_1H.copy()
		self.elements['symbol'] = symbol


		macd_calc = self.calculator_macd()

		# if 'permit' in GL_Results.columns:
		# 	if (
		# 		GL_Results['permit'][0] == True and
		# 		GL_Results['draw_down'][0] <= 7
		# 		): 
		# 		return GL_Results

		if True:#try:

			signal, signaltype, indicator = macd.divergence(
															sigtype = signaltype,
															sigpriority = signalpriority,
															indicator = macd_calc,
															column_div = GL_Results['MACD_column_div'][0],
															ind_name = 'macd',
															dataset_5M = dataset_5M,
															dataset_1H = dataset_1H,
															symbol = symbol,
															flaglearn = GL_Results['islearned'][0],
															flagtest = True
															)
			# with pd.option_context('display.max_rows', None, 'display.max_columns', None):
			# 	print(signal)

			# pr_parameters.elements['st_percent_min'] = 0.09
			# pr_parameters.elements['st_percent_max'] = 0.12

			# pr_parameters.elements['tp_percent_min'] = 0.26
			# pr_parameters.elements['tp_percent_max'] = 0.3

			signal_output, learning_output = macd_tester.RunGL(
																dataset_5M_real = dataset_5M_real,
																signal = signal, 
																sigtype = signaltype, 
																flaglearn = GL_Results['islearned'][0], 
																flagtest = True,
																pr_parameters = pr_parameters,
																pr_config = pr_config,
																indicator = indicator,
																flag_savepic = flag_savepic
																)
		else:#except Exception as ex:
			print('Permit Error: ', ex)

			signal_output = pd.DataFrame()
			learning_output = pd.DataFrame()

		with pd.option_context('display.max_rows', None, 'display.max_columns', None):
			print('signals = ', signal_output)

		hour_st_0 = 0
		hour_st_1 = 0
		hour_st_2 = 0
		hour_st_3 = 0
		hour_st_4 = 0
		hour_st_5 = 0
		hour_st_6 = 0
		hour_st_7 = 0
		hour_st_8 = 0
		hour_st_9 = 0
		hour_st_10 = 0
		hour_st_11 = 0
		hour_st_12 = 0
		hour_st_13 = 0
		hour_st_14 = 0
		hour_st_15 = 0
		hour_st_16 = 0
		hour_st_17 = 0
		hour_st_18 = 0
		hour_st_19 = 0
		hour_st_20 = 0
		hour_st_21 = 0
		hour_st_22 = 0
		hour_st_23 = 0

		hour_tp_0 = 0
		hour_tp_1 = 0
		hour_tp_2 = 0
		hour_tp_3 = 0
		hour_tp_4 = 0
		hour_tp_5 = 0
		hour_tp_6 = 0
		hour_tp_7 = 0
		hour_tp_8 = 0
		hour_tp_9 = 0
		hour_tp_10 = 0
		hour_tp_11 = 0
		hour_tp_12 = 0
		hour_tp_13 = 0
		hour_tp_14 = 0
		hour_tp_15 = 0
		hour_tp_16 = 0
		hour_tp_17 = 0
		hour_tp_18 = 0
		hour_tp_19 = 0
		hour_tp_20 = 0
		hour_tp_21 = 0
		hour_tp_22 = 0
		hour_tp_23 = 0

		# for elm in signal_output.index:
		# 	if signal_output['flag'][elm] == 'st':

		# 		if int(signal_output['time'][elm].hour) == 0:
		# 			hour_st_0 += signal_output['st_pr'][elm]

		# 		if int(signal_output['time'][elm].hour) == 1:
		# 			hour_st_1 += signal_output['st_pr'][elm]

		# 		if int(signal_output['time'][elm].hour) == 2:
		# 			hour_st_2 += signal_output['st_pr'][elm]

		# 		if int(signal_output['time'][elm].hour) == 3:
		# 			hour_st_3 += signal_output['st_pr'][elm]

		# 		if int(signal_output['time'][elm].hour) == 4:
		# 			hour_st_4 += signal_output['st_pr'][elm]

		# 		if int(signal_output['time'][elm].hour) == 5:
		# 			hour_st_5 += signal_output['st_pr'][elm]

		# 		if int(signal_output['time'][elm].hour) == 6:
		# 			hour_st_6 += signal_output['st_pr'][elm]

		# 		if int(signal_output['time'][elm].hour) == 7:
		# 			hour_st_7 += signal_output['st_pr'][elm]

		# 		if int(signal_output['time'][elm].hour) == 8:
		# 			hour_st_8 += signal_output['st_pr'][elm]

		# 		if int(signal_output['time'][elm].hour) == 9:
		# 			hour_st_9 += signal_output['st_pr'][elm]

		# 		if int(signal_output['time'][elm].hour) == 10:
		# 			hour_st_10 += signal_output['st_pr'][elm]

		# 		if int(signal_output['time'][elm].hour) == 11:
		# 			hour_st_11 += signal_output['st_pr'][elm]

		# 		if int(signal_output['time'][elm].hour) == 12:
		# 			hour_st_12 += signal_output['st_pr'][elm]

		# 		if int(signal_output['time'][elm].hour) == 13:
		# 			hour_st_13 += signal_output['st_pr'][elm]

		# 		if int(signal_output['time'][elm].hour) == 14:
		# 			hour_st_14 += signal_output['st_pr'][elm]

		# 		if int(signal_output['time'][elm].hour) == 15:
		# 			hour_st_15 += signal_output['st_pr'][elm]

		# 		if int(signal_output['time'][elm].hour) == 16:
		# 			hour_st_16 += signal_output['st_pr'][elm]

		# 		if int(signal_output['time'][elm].hour) == 17:
		# 			hour_st_17 += signal_output['st_pr'][elm]

		# 		if int(signal_output['time'][elm].hour) == 18:
		# 			hour_st_18 += signal_output['st_pr'][elm]

		# 		if int(signal_output['time'][elm].hour) == 19:
		# 			hour_st_19 += signal_output['st_pr'][elm]

		# 		if int(signal_output['time'][elm].hour) == 20:
		# 			hour_st_20 += signal_output['st_pr'][elm]

		# 		if int(signal_output['time'][elm].hour) == 21:
		# 			hour_st_21 += signal_output['st_pr'][elm]

		# 		if int(signal_output['time'][elm].hour) == 22:
		# 			hour_st_22 += signal_output['st_pr'][elm]

		# 		if int(signal_output['time'][elm].hour) == 23:
		# 			hour_st_23 += signal_output['st_pr'][elm]

		# for elm in signal_output.index:
		# 	if signal_output['flag'][elm] == 'tp':

		# 		if int(signal_output['time'][elm].hour) == 0:
		# 			hour_tp_0 += signal_output['tp_pr'][elm]

		# 		if int(signal_output['time'][elm].hour) == 1:
		# 			hour_tp_1 += signal_output['tp_pr'][elm]

		# 		if int(signal_output['time'][elm].hour) == 2:
		# 			hour_tp_2 += signal_output['tp_pr'][elm]

		# 		if int(signal_output['time'][elm].hour) == 3:
		# 			hour_tp_3 += signal_output['tp_pr'][elm]

		# 		if int(signal_output['time'][elm].hour) == 4:
		# 			hour_tp_4 += signal_output['tp_pr'][elm]

		# 		if int(signal_output['time'][elm].hour) == 5:
		# 			hour_tp_5 += signal_output['tp_pr'][elm]

		# 		if int(signal_output['time'][elm].hour) == 6:
		# 			hour_tp_6 += signal_output['tp_pr'][elm]

		# 		if int(signal_output['time'][elm].hour) == 7:
		# 			hour_tp_7 += signal_output['tp_pr'][elm]

		# 		if int(signal_output['time'][elm].hour) == 8:
		# 			hour_tp_8 += signal_output['tp_pr'][elm]

		# 		if int(signal_output['time'][elm].hour) == 9:
		# 			hour_tp_9 += signal_output['tp_pr'][elm]

		# 		if int(signal_output['time'][elm].hour) == 10:
		# 			hour_tp_10 += signal_output['tp_pr'][elm]

		# 		if int(signal_output['time'][elm].hour) == 11:
		# 			hour_tp_11 += signal_output['tp_pr'][elm]

		# 		if int(signal_output['time'][elm].hour) == 12:
		# 			hour_tp_12 += signal_output['tp_pr'][elm]

		# 		if int(signal_output['time'][elm].hour) == 13:
		# 			hour_tp_13 += signal_output['tp_pr'][elm]

		# 		if int(signal_output['time'][elm].hour) == 14:
		# 			hour_tp_14 += signal_output['tp_pr'][elm]

		# 		if int(signal_output['time'][elm].hour) == 15:
		# 			hour_tp_15 += signal_output['tp_pr'][elm]

		# 		if int(signal_output['time'][elm].hour) == 16:
		# 			hour_tp_16 += signal_output['tp_pr'][elm]

		# 		if int(signal_output['time'][elm].hour) == 17:
		# 			hour_tp_17 += signal_output['tp_pr'][elm]

		# 		if int(signal_output['time'][elm].hour) == 18:
		# 			hour_tp_18 += signal_output['tp_pr'][elm]

		# 		if int(signal_output['time'][elm].hour) == 19:
		# 			hour_tp_19 += signal_output['tp_pr'][elm]

		# 		if int(signal_output['time'][elm].hour) == 20:
		# 			hour_tp_20 += signal_output['tp_pr'][elm]

		# 		if int(signal_output['time'][elm].hour) == 21:
		# 			hour_tp_21 += signal_output['tp_pr'][elm]

		# 		if int(signal_output['time'][elm].hour) == 22:
		# 			hour_tp_22 += signal_output['tp_pr'][elm]

		# 		if int(signal_output['time'][elm].hour) == 23:
		# 			hour_tp_23 += signal_output['tp_pr'][elm]

		# print('ST **************************************************')
		# print(hour_st_0 )
		# print(hour_st_1 )
		# print(hour_st_2 )
		# print(hour_st_3 )
		# print(hour_st_4 )
		# print(hour_st_5 )
		# print(hour_st_6 )
		# print(hour_st_7 )
		# print(hour_st_8 )
		# print(hour_st_9 )
		# print(hour_st_10)
		# print(hour_st_11)
		# print(hour_st_12)
		# print(hour_st_13)
		# print(hour_st_14)
		# print(hour_st_15)
		# print(hour_st_16)
		# print(hour_st_17)
		# print(hour_st_18)
		# print(hour_st_19)
		# print(hour_st_20)
		# print(hour_st_21)
		# print(hour_st_22)
		# print(hour_st_23)
		# print('TP **************************************************')
		# print(hour_tp_0 )
		# print(hour_tp_1 )
		# print(hour_tp_2 )
		# print(hour_tp_3 )
		# print(hour_tp_4 )
		# print(hour_tp_5 )
		# print(hour_tp_6 )
		# print(hour_tp_7 )
		# print(hour_tp_8 )
		# print(hour_tp_9 )
		# print(hour_tp_10 )
		# print(hour_tp_11 )
		# print(hour_tp_12 )
		# print(hour_tp_13 )
		# print(hour_tp_14 )
		# print(hour_tp_15 )
		# print(hour_tp_16 )
		# print(hour_tp_17 )
		# print(hour_tp_18 )
		# print(hour_tp_19 )
		# print(hour_tp_20 )
		# print(hour_tp_21 )
		# print(hour_tp_22 )
		# print(hour_tp_23 )

		# print('Monday st ******************************************')
		# for elm in signal_output.index:
		# 	if signal_output['flag'][elm] == 'st':
		# 		if signal_output['time'][elm].day_name() == 'Monday':

		# 			print(signal_output['time'][elm].hour,':', signal_output['time'][elm].minute)

		# print('Monday tp ******************************************')
		# for elm in signal_output.index:
		# 	if signal_output['flag'][elm] == 'tp':
		# 		if signal_output['time'][elm].day_name() == 'Monday':

		# 			print(signal_output['time'][elm].hour,':', signal_output['time'][elm].minute)


		# print('Tuesday ******************************************')
		# for elm in signal_output.index:
		# 	if signal_output['flag'][elm] == 'st':
		# 		if signal_output['time'][elm].day_name() == 'Tuesday':
		# 			print(signal_output['time'][elm].hour,':', signal_output['time'][elm].minute)
		
		# print('Wednesday ******************************************')
		# for elm in signal_output.index:
		# 	if signal_output['flag'][elm] == 'st':
		# 		if signal_output['time'][elm].day_name() == 'Wednesday':
		# 			print(signal_output['time'][elm].hour,':', signal_output['time'][elm].minute)

		# print('Thursday ******************************************')
		# for elm in signal_output.index:
		# 	if signal_output['flag'][elm] == 'st':
		# 		if signal_output['time'][elm].day_name() == 'Thursday':
		# 			print(signal_output['time'][elm].hour,':', signal_output['time'][elm].minute)

		# print('Friday ******************************************')
		# for elm in signal_output.index:
		# 	if signal_output['flag'][elm] == 'st':
		# 		if signal_output['time'][elm].day_name() == 'Friday':
		# 			print(signal_output['time'][elm].hour,':', signal_output['time'][elm].minute)

		# plt.plot(signal_output['money'])
		# plt.show()

		with pd.option_context('display.max_rows', None, 'display.max_columns', None):
			print(learning_output)

		if learning_output.empty == False:

			if learning_output['score'][0] >= GL_Results['score'][0] * 0.9:
				GL_Results['permit'] = [True]

			else:
				GL_Results['permit'] = [False]
			
			GL_Results['score'][0] = learning_output['score'][0]
			GL_Results['mean_tp_pr'][0] = learning_output['mean_tp_pr'][0]
			GL_Results['mean_st_pr'][0] = learning_output['mean_st_pr'][0]
			GL_Results['max_tp_pr'][0] = learning_output['max_tp_pr'][0]
			GL_Results['max_st_pr'][0] = learning_output['max_st_pr'][0]
			GL_Results['sum_st_pr'][0] = learning_output['sum_st_pr'][0]
			GL_Results['sum_tp_pr'][0] = learning_output['sum_tp_pr'][0]

			GL_Results['num_tp_pr'][0] = learning_output['num_tp_pr'][0]
			GL_Results['num_st_pr'][0] = learning_output['num_st_pr'][0]
			GL_Results['num_trade_pr'][0] = learning_output['num_trade_pr'][0]
			GL_Results['money'][0] = learning_output['money'][0]
			GL_Results['draw_down'][0] = learning_output['draw_down'][0]

			if learning_output['max_st'][0] > 0.09: GL_Results['st_percent_max'][0] = learning_output['max_st'][0]
			if learning_output['min_st'][0] > 0.08: GL_Results['st_percent_min'][0] = learning_output['min_st'][0]
			if learning_output['max_tp'][0] > 0.27: GL_Results['tp_percent_max'][0] = learning_output['max_tp'][0]
			if learning_output['min_tp'][0] > 0.24: GL_Results['tp_percent_min'][0] = learning_output['min_tp'][0]

		else:
			GL_Results['permit'] = [False]
			GL_Results['score'][0] = 0

		if os.path.exists(path_superhuman + symbol + '.csv'):
			os.remove(path_superhuman + symbol + '.csv')

		GL_Results.to_csv(path_superhuman + symbol + '.csv')

		return GL_Results


	def Genetic(self, dataset_5M_real, dataset_5M, dataset_1H, symbol, signaltype, signalpriority, num_turn):

		if symbol == 'ETHUSD_i':
			self.elements['st_percent_up'] = 2000
			self.elements['st_percent_down'] = 1500
			self.elements['tp_percent_up'] = 2000
			self.elements['tp_percent_down'] = 1500
		else:
			self.elements['st_percent_up'] = 120
			self.elements['st_percent_down'] = 100
			self.elements['tp_percent_up'] = 120
			self.elements['tp_percent_down'] = 100

		chrom = Chromosome(parameters = self)
		macd_config = MACDConfig()
		path_elites_chromosome = macd_config.cfg['path_elites'] + signalpriority + path_slash + signaltype + path_slash + symbol + '_ChromosomeResults.csv'
		
		# while not chrom.Get(
		# 					work = 'Optimize',
		# 					signaltype = signaltype,
		# 					signalpriority = signalpriority,
		# 					symbol = symbol,
		# 					number_chromos = 10,
		# 					Chromosome = '',
		# 					chrom_counter = 0,
		# 					path_elites_chromosome = path_elites_chromosome,
		# 					alpha = 0.2
		# 					):
		# 	pass

		chromosome, macd_parameters, ind_parameters, pr_parameters, pr_config = chrom.Get(
																							work = 'BigBang',
																							signaltype = signaltype,
																							signalpriority = signalpriority,
																							symbol = symbol,
																							number_chromos = 10,
																							Chromosome = '',
																							chrom_counter = 0
																							)

		macd_config = MACDConfig()
		path_superhuman = macd_config.cfg['path_superhuman'] + signalpriority + path_slash + signaltype + path_slash
		path_elites = macd_config.cfg['path_elites'] + signalpriority + path_slash + signaltype + path_slash

		if os.path.exists(path_superhuman + symbol + '.csv'):
			max_score_gl = pd.read_csv(path_superhuman + symbol + '.csv')['score'][0]
		else:
			max_score_gl = 20

		max_score_gl = 20


		print('================================ START Genetic MACD ',signaltype,' ===> ',symbol,' ',signalpriority)
		print('\n')

		learning_output_before = pd.DataFrame()

		if (
			os.path.exists(path_elites + symbol + '_LearningResults.csv') and
			os.path.exists(path_elites + symbol + '_ChromosomeResults.csv')
			):

			learning_result = pd.read_csv(path_elites + symbol + '_LearningResults.csv').drop(columns='Unnamed: 0')
			chromosome_output = pd.read_csv(path_elites + symbol + '_ChromosomeResults.csv').drop(columns='Unnamed: 0')

			max_corr = chromosome_output['corr'].min()/3

			if num_turn <= len(learning_result['score']):
				num_turn = (len(learning_result['score'])) + 50

				if len(chromosome_output) >= num_turn:
					num_turn = len(chromosome_output) + 50

		else:
			learning_result = pd.DataFrame()
			chromosome_output = pd.DataFrame()
			max_corr = 0


		chrom_counter = 0
		all_chorms = 0
		chorm_reset_counter = 0
		bad_score_counter = 0
		bad_score_counter_2 = 0
		score = max_score_gl
		score_for_reset = 0

		learning_interval_counter = 0
		learn_counter = 1

		bad_flag = False

		bar = Bar(signaltype + ' ' + signalpriority, max = int(num_turn))

		for i in range(len(chromosome)):

			if (
				chromosome[chrom_counter]['score'] != 0 and
				chromosome[chrom_counter]['islearned'] == True and
				chromosome[chrom_counter]['isborn'] == False
				):
				chrom_counter += 1
				continue


		if chrom_counter >= len(chromosome):
			chrom_counter = 0
			print("Group Sex Start")
			chromosome, macd_parameters, ind_parameters, pr_parameters, pr_config = chrom.Get(
																								work = 'group_sex',
																								signaltype = signaltype,
																								signalpriority = signalpriority,
																								symbol = symbol,
																								number_chromos = 0,
																								Chromosome = chromosome,
																								chrom_counter = chrom_counter
																								)
			print("Group Sex Finish")

		#print(chrom_counter)




		while chrom_counter < len(chromosome):

			if chromosome == 'End_of_Chromosomes':
				# print(chromosome)
				break

			# print()
			# print('================== Num Symbol ==>',symbol, ' ' , signaltype, ' ',signalpriority)
			# print()
			# print('================== Num =========> ', len(chromosome_output))
			# print('================== Num Chroms ======> ', chrom_counter)
			# print('================== All Chorms ======> ', all_chorms)
			# print('================== Flag Learn ======> ', chromosome[chrom_counter]['islearned'])
			# print('================== Chorm Reseter ===> ',chorm_reset_counter)
			# print('===== bad score counter ========> ',bad_score_counter)
			# print('===== bad score counter 2 ======> ',bad_score_counter_2)

			# print('===== max_tp ======> ',chromosome[chrom_counter]['tp_percent_max'])
			# print('===== min_tp ======> ',chromosome[chrom_counter]['tp_percent_min'])
			# print('===== max_st ======> ',chromosome[chrom_counter]['st_percent_max'])
			# print('===== min_st ======> ',chromosome[chrom_counter]['st_percent_min'])
			# print()
			bar.next()

			

			if (chorm_reset_counter >= 27):
				chorm_reset_counter = 0
				
				chromosome, macd_parameters, ind_parameters, pr_parameters, pr_config = chrom.Get(
																							work = 'fucker_0',
																							signaltype = signaltype,
																							signalpriority = signalpriority,
																							symbol = symbol,
																							number_chromos = 0,
																							Chromosome = chromosome,
																							chrom_counter = chrom_counter
																							)


				all_chorms += 1
				continue

			# if all_chorms >= int(num_turn): break
			if all_chorms >= 200: break
			all_chorms += 1


			self.elements = macd_parameters.elements
			self.elements['dataset_5M'] = dataset_5M.copy()
			self.elements['dataset_1H'] = dataset_1H.copy()
			self.elements['symbol'] = symbol

			macd_calc = self.calculator_macd()

			ind_config = indicator_config()
			macd = Divergence(parameters = ind_parameters, config = ind_config)

			try:

				signal, signaltype, indicator = macd.divergence(
																sigtype = signaltype,
																sigpriority = signalpriority,
																indicator = macd_calc,
																column_div = chromosome[chrom_counter]['MACD_column_div'],
																ind_name = 'macd',
																dataset_5M = dataset_5M,
																dataset_1H = dataset_1H,
																symbol = symbol,
																flaglearn = chromosome[chrom_counter]['islearned'],
																flagtest = True
																)

				if chromosome[chrom_counter]['isborn'] == True:
					divergence_out_corr = pd.DataFrame(np.ones(signal.index[-1]))
					divergence_out_corr['macd'] = np.nan
					divergence_out_corr['low'] = np.nan
					divergence_out_corr['high'] = np.nan

					counter_corr = 0
					for corr_idx in signal.index:
						divergence_out_corr['macd'][counter_corr] = signal.indicator_front[corr_idx]
						divergence_out_corr['macd'][counter_corr + 1] = signal.indicator_back[corr_idx]

						divergence_out_corr['low'][counter_corr] = signal.low_front[corr_idx]
						divergence_out_corr['low'][counter_corr + 1] = signal.low_back[corr_idx]

						divergence_out_corr['high'][counter_corr] = signal.high_front[corr_idx]
						divergence_out_corr['high'][counter_corr + 1] = signal.high_back[corr_idx]

						counter_corr += 2

					divergence_out_corr = divergence_out_corr.dropna()
					divergence_out_corr = divergence_out_corr.drop(columns = [0])

					number_divergence = len(divergence_out_corr.index)/1000

					divergence_out_corr = divergence_out_corr.corr()

					chromosome[chrom_counter].update(
													{
														'corr': -((divergence_out_corr['macd'][2] * divergence_out_corr['macd'][1] * number_divergence) ** (1/3)),
													}
													)
					if (
						divergence_out_corr['macd'][2] > 0 and
						divergence_out_corr['macd'][1] > 0
						):
						chromosome[chrom_counter]['corr'] = -chromosome[chrom_counter]['corr']

					chromosome[chrom_counter].update(
													{
														'corr_low': divergence_out_corr['macd'][1],
														'corr_high': divergence_out_corr['macd'][2],
													}
													)

					if chromosome[chrom_counter]['corr'] >= max_corr:
						signal = pd.DataFrame()
						signal_output = pd.DataFrame()
						learning_output_now = pd.DataFrame()
						learning_output_before = pd.DataFrame()

				chromosome[chrom_counter]['isborn'] = False
				# print('siiiiiiignaaaaaal ====> ', len(signal['index']))

			except Exception as ex:
				# print('Divergence Error: ',ex)
				signal = pd.DataFrame()
				signal_output = pd.DataFrame()
				learning_output_now = pd.DataFrame()
				learning_output_before = pd.DataFrame()


			if signal.empty == True:
				chromosome[chrom_counter]['isborn'] = False
				chromosome[chrom_counter]['islearned'] = True
				chromosome[chrom_counter]['score'] = -1

				_, _, _, _, _ = chrom.Get(
											work = 'graveyard',
											signaltype = signaltype,
											signalpriority = signalpriority,
											symbol = symbol,
											number_chromos = 0,
											Chromosome = chromosome,
											chrom_counter = chrom_counter
											)

				chromosome, macd_parameters, ind_parameters, pr_parameters, pr_config = chrom.Get(
																							work = 'fucker_0',
																							signaltype = signaltype,
																							signalpriority = signalpriority,
																							symbol = symbol,
																							number_chromos = 0,
																							Chromosome = chromosome,
																							chrom_counter = chrom_counter
																							)
				continue

			ind_parameters.elements['dataset_5M'] = dataset_5M.copy()
			ind_parameters.elements['dataset_1H'] = dataset_1H.copy()

			macd_tester = Tester(parameters = ind_parameters, config = ind_config)
			try:

				signal_output, learning_output_now = macd_tester.RunGL(
																	dataset_5M_real = dataset_5M_real,
																	signal = signal, 
																	sigtype = signaltype, 
																	flaglearn = chromosome[chrom_counter]['islearned'], 
																	flagtest = True,
																	pr_parameters = pr_parameters,
																	pr_config = pr_config,
																	indicator = indicator,
																	flag_savepic = False
																	)

			except Exception as ex:
				# print('Learning Error: ',ex)
				# with pd.option_context('display.max_rows', None, 'display.max_columns', None):
				# 	print(signal)
				signal_output = pd.DataFrame()
				learning_output_now = pd.DataFrame()
				learning_output_before = pd.DataFrame()

			# with pd.option_context('display.max_rows', None, 'display.max_columns', None):
			# 	print(learning_output_now)
			# 	print()

			if (
				signal_output.empty == True or
				learning_output_now.empty == True
				):

				chromosome[chrom_counter]['isborn'] = False
				chromosome[chrom_counter]['islearned'] = True
				chromosome[chrom_counter]['score'] = -1

				_, _, _, _, _ = chrom.Get(
											work = 'graveyard',
											signaltype = signaltype,
											signalpriority = signalpriority,
											symbol = symbol,
											number_chromos = 0,
											Chromosome = chromosome,
											chrom_counter = chrom_counter
											)

				chromosome, macd_parameters, ind_parameters, pr_parameters, pr_config = chrom.Get(
																							work = 'fucker_0',
																							signaltype = signaltype,
																							signalpriority = signalpriority,
																							symbol = symbol,
																							number_chromos = 0,
																							Chromosome = chromosome,
																							chrom_counter = chrom_counter
																							)
				continue

			# with pd.option_context('display.max_rows', None, 'display.max_columns', None):
			# 	print(learning_output_now)

			# print()

			#print(' max score ========> ', max_score_gl)
			if (
				chromosome[chrom_counter]['islearned'] == False
				):
				bad_flag = True
				bad_score_counter += 1
				learning_output_before = learning_output_now

				if (
					learning_output_now['max_tp'][0] >= 0.1 and
					learning_output_now['score'][0] >= score_for_reset and
					learning_output_now['max_tp'][0] > learning_output_now['min_st'][0] * 1.2
					):
					chromosome[chrom_counter]['tp_percent_max'] = learning_output_now['max_tp'][0]
					flag_learn_tp_percent_max = True

					#********************************************************************************************************************************
				else:
					if (
						learning_output_now['score'][0] >= score_for_reset and
						learning_output_now['min_st'][0] != 0 and
						learning_output_now['max_st'][0] >= 0.1
						):
						chromosome[chrom_counter]['tp_percent_max'] = randint(int((learning_output_now['max_st'][0]/2)*100), int(learning_output_now['max_st'][0]*100)*2)/100

						while chromosome[chrom_counter]['tp_percent_max'] <= learning_output_now['min_st'][0]:
							chromosome[chrom_counter]['tp_percent_max'] = randint(int((learning_output_now['max_st'][0]/2)*100), int(learning_output_now['max_st'][0]*100)*2)/100

						flag_learn_tp_percent_max = True
					else:
						if (
							learning_output_now['max_tp'][0] == 0 and
							learning_output_now['min_tp'][0] == 0 and
							learning_output_now['max_st'][0] == 0 and
							learning_output_now['min_st'][0] == 0
							):
							chromosome[chrom_counter]['tp_percent_max'] = learning_output_now['max_tp_pr'][0]

							flag_learn_tp_percent_max = True

						else:

							chromosome[chrom_counter]['tp_percent_max'] = randint(self.elements['tp_percent_down'], self.elements['tp_percent_up'])/100

							flag_learn_tp_percent_max = False


				if (
					learning_output_now['score'][0] >= score_for_reset and
					learning_output_now['min_tp'][0] != 0
					):

					chromosome[chrom_counter]['tp_percent_min'] = learning_output_now['min_tp'][0]

					flag_learn_tp_percent_min = True

				else:
					if (
						learning_output_now['max_tp'][0] == 0 and
						learning_output_now['min_tp'][0] == 0 and
						learning_output_now['max_st'][0] == 0 and
						learning_output_now['min_st'][0] == 0
						):

						chromosome[chrom_counter]['tp_percent_min'] = learning_output_now['mean_tp_pr'][0]

						flag_learn_tp_percent_min = True
					else:

						chromosome[chrom_counter]['tp_percent_min'] = randint(self.elements['tp_percent_down'], self.elements['tp_percent_up'])/100

						flag_learn_tp_percent_min = False

				if (
					learning_output_now['score'][0] >= score_for_reset and
					learning_output_now['max_st'][0] >= 0.1
					):

					chromosome[chrom_counter]['st_percent_max'] = learning_output_now['max_st'][0]

					flag_learn_st_percent_max = True

				else:
					if (
						learning_output_now['max_tp'][0] == 0 and
						learning_output_now['min_tp'][0] == 0 and
						learning_output_now['max_st'][0] == 0 and
						learning_output_now['min_st'][0] == 0
						):

						chromosome[chrom_counter]['st_percent_max'] = learning_output_now['max_st_pr'][0]

						flag_learn_st_percent_max = True

					else:

						chromosome[chrom_counter]['st_percent_max'] = randint(self.elements['st_percent_down'], self.elements['st_percent_up'])/100

						flag_learn_st_percent_max = False

				if (
					learning_output_now['score'][0] >= score_for_reset and
					learning_output_now['min_st'][0] != 0
					):
					chromosome[chrom_counter]['st_percent_min'] = learning_output_now['min_st'][0]
					flag_learn_st_percent_min = True

				else:
					if (
						learning_output_now['max_tp'][0] == 0 and
						learning_output_now['min_tp'][0] == 0 and
						learning_output_now['max_st'][0] == 0 and
						learning_output_now['min_st'][0] == 0
						):

						chromosome[chrom_counter]['st_percent_min'] = learning_output_now['mean_st_pr'][0]
						flag_learn_st_percent_min = True

					else:

						chromosome[chrom_counter]['st_percent_min'] = randint(self.elements['st_percent_down'], self.elements['st_percent_up'])/100
						flag_learn_st_percent_min = False

						while chromosome[chrom_counter]['tp_percent_max'] < chromosome[chrom_counter]['st_percent_min']:
							chromosome[chrom_counter]['st_percent_min'] = randint(int((chromosome[chrom_counter]['tp_percent_max']/2)*100), 100)/100

							while chromosome[chrom_counter]['tp_percent_max'] < chromosome[chrom_counter]['st_percent_min']:
								chromosome[chrom_counter]['st_percent_min'] = randint(int((chromosome[chrom_counter]['tp_percent_max']/2)*100), 1500)/100

				if learning_output_now['diff_extereme'][0] != 0:
					diff_extereme = learning_output_now['diff_extereme'][0]
				else:
					diff_extereme = randint(1,6)

				score_for_reset = learning_output_now['score'][0]
				chromosome[chrom_counter]['islearned'] = (flag_learn_tp_percent_max & flag_learn_tp_percent_min & flag_learn_st_percent_max & flag_learn_st_percent_min)

			elif (
				learning_output_now['score'][0] >= max_score_gl * 0.99 and
				chromosome[chrom_counter]['islearned'] == True
				):

				learning_output_before['num_st_pr'] = [learning_output_now['num_st_pr'][0]]
				learning_output_before['num_tp_pr'] = [learning_output_now['num_tp_pr'][0]]
				learning_output_before['num_trade_pr'] = [learning_output_now['num_trade_pr'][0]]

				learning_output_before['score'] = [learning_output_now['score'][0]]

				learning_output_before['max_tp_pr'] = [learning_output_now['max_tp_pr'][0]]
				learning_output_before['max_st_pr'] = [learning_output_now['max_st_pr'][0]]

				learning_output_before['mean_tp_pr'] = [learning_output_now['mean_tp_pr'][0]]
				learning_output_before['mean_st_pr'] = [learning_output_now['mean_st_pr'][0]]

				learning_output_before['sum_st_pr'] = [learning_output_now['sum_st_pr'][0]]
				learning_output_before['sum_tp_pr'] = [learning_output_now['sum_tp_pr'][0]]

				learning_output_before['money'] = [learning_output_now['money'][0]]
				learning_output_before['draw_down'] = [learning_output_now['draw_down'][0]]

				learning_result = learning_result.append(learning_output_before, ignore_index=True)

				score = (learning_output_now['score'][0])
				chromosome[chrom_counter]['score'] = learning_output_now['score'][0]

				chromosome_output = chromosome_output.append(chromosome[chrom_counter], ignore_index=True)

				#Saving Elites:

				if not os.path.exists(path_elites):
					os.makedirs(path_elites)

				if os.path.exists(path_elites + symbol + '_LearningResults.csv'):
					os.remove(path_elites + symbol + '_LearningResults.csv')

				if os.path.exists(path_elites + symbol + '_ChromosomeResults.csv'):
					os.remove(path_elites + symbol + '_ChromosomeResults.csv')

				chromosome_output.to_csv(path_elites + symbol + '_ChromosomeResults.csv')
				learning_result.to_csv(path_elites + symbol + '_LearningResults.csv')

				#//////////////////////


				_, _, _, _, _ = chrom.Get(
											work = 'graveyard',
											signaltype = signaltype,
											signalpriority = signalpriority,
											symbol = symbol,
											number_chromos = 0,
											Chromosome = chromosome,
											chrom_counter = chrom_counter
											)

				chorm_reset_counter = 0
				bad_score_counter = 0
				score_for_reset = 0


				learning_output_before = pd.DataFrame()
				learning_output_now = pd.DataFrame()

				bad_flag = False

			elif (
				learning_output_now['score'][0] < max_score_gl * 0.99 and
				chromosome[chrom_counter]['islearned'] == True and
				bad_score_counter >= 4
				):

				chromosome[chrom_counter]['isborn'] = False
				chromosome[chrom_counter]['islearned'] = True
				chromosome[chrom_counter]['score'] = -1

				_, _, _, _, _ = chrom.Get(
											work = 'graveyard',
											signaltype = signaltype,
											signalpriority = signalpriority,
											symbol = symbol,
											number_chromos = 0,
											Chromosome = chromosome,
											chrom_counter = chrom_counter
											)

				chromosome, macd_parameters, ind_parameters, pr_parameters, pr_config = chrom.Get(
																							work = 'fucker_0',
																							signaltype = signaltype,
																							signalpriority = signalpriority,
																							symbol = symbol,
																							number_chromos = 0,
																							Chromosome = chromosome,
																							chrom_counter = chrom_counter
																							)

				score_for_reset = 0
				bad_score_counter = 0
				bad_score_counter_2 = 0
				continue

			else:
				chromosome[chrom_counter]['islearned'] = False
				bad_flag = True
				bad_score_counter += 1
				learning_output_before = learning_output_now

				if learning_output_now['max_st'][0] > 0.09: 
					chromosome[chrom_counter]['st_percent_max'] = learning_output_now['max_st'][0]
				else:
					chromosome[chrom_counter]['st_percent_max'] = learning_output_now['max_st_pr'][0]

				if learning_output_now['min_st'][0] > 0.08: 
					chromosome[chrom_counter]['st_percent_min'] = learning_output_now['min_st'][0]
				else:
					chromosome[chrom_counter]['st_percent_min'] = learning_output_now['mean_st_pr'][0]

				if learning_output_now['max_tp'][0] > 0.27: 
					chromosome[chrom_counter]['tp_percent_max'] = learning_output_now['max_tp'][0]
				else:
					chromosome[chrom_counter]['tp_percent_max'] = learning_output_now['max_tp_pr'][0]

				if learning_output_now['min_tp'][0] > 0.24: 
					chromosome[chrom_counter]['tp_percent_min'] = learning_output_now['min_tp'][0]
				else:
					chromosome[chrom_counter]['tp_percent_min'] = learning_output_now['mean_tp_pr'][0]


			if (
				len(chromosome_output) >= int(num_turn)
				):
				break

			if bad_flag == True:

				if bad_score_counter < 5:

					chromosome, macd_parameters, ind_parameters, pr_parameters, pr_config = chrom.Get(
																									work = 'fucker_1',
																									scoresdataframe = learning_output_now,
																									signaltype = signaltype,
																									signalpriority = signalpriority,
																									symbol = symbol,
																									number_chromos = 0,
																									Chromosome = chromosome,
																									chrom_counter = chrom_counter
																									)
					

				else:
					if (
						bad_score_counter_2 >= 3
						):
						
						chromosome, macd_parameters, ind_parameters, pr_parameters, pr_config = chrom.Get(
																									work = 'fucker_2',
																									signaltype = signaltype,
																									signalpriority = signalpriority,
																									symbol = symbol,
																									number_chromos = 0,
																									Chromosome = chromosome,
																									chrom_counter = chrom_counter
																									)

						score_for_reset = 0
						bad_score_counter = 0
						bad_score_counter_2 = 0

					else:
						chromosome, macd_parameters, ind_parameters, pr_parameters, pr_config = chrom.Get(
																										work = 'fucker_3',
																										signaltype = signaltype,
																										signalpriority = signalpriority,
																										symbol = symbol,
																										number_chromos = 0,
																										Chromosome = chromosome,
																										chrom_counter = chrom_counter
																										)
						score_for_reset = 0
						bad_score_counter_2 += 1
						bad_score_counter = 0

				continue

			chrom_counter += 1

			if (chrom_counter >= len(chromosome)):

				chrom_counter = 0

				print('Group Sex Start')

				chromosome, macd_parameters, ind_parameters, pr_parameters, pr_config = chrom.Get(
																									work = 'group_sex',
																									signaltype = signaltype,
																									signalpriority = signalpriority,
																									symbol = symbol,
																									number_chromos = 0,
																									Chromosome = chromosome,
																									chrom_counter = chrom_counter
																									)

				print('Group Sex Finish')
				continue

		#**************************** Best Find *********************************************************
		#************ Finded:
		if len(chromosome_output) > 0:

			if not os.path.exists(path_elites):
				os.makedirs(path_elites)

			if os.path.exists(path_elites + symbol + '_LearningResults.csv'):
				os.remove(path_elites + symbol + '_LearningResults.csv')

			if os.path.exists(path_elites + symbol + '_ChromosomeResults.csv'):
				os.remove(path_elites + symbol + '_ChromosomeResults.csv')

			chromosome_output.to_csv(path_elites + symbol + '_ChromosomeResults.csv')
			learning_result.to_csv(path_elites + symbol + '_LearningResults.csv')

			# with pd.option_context('display.max_rows', None, 'display.max_columns', None):
			# 	print('=======> Chorme ===> ')
			# 	print()
			# 	print('........................................................')
			# 	print(chromosome_output)
			# 	print('........................................................')
			# 	print()

			best_chromosome = pd.DataFrame()
			max_score_output = np.max(learning_result['score'].dropna())
			best_score_index = np.where(learning_result['score'] == max_score_output)[0]
			best_dict = dict()
			for idx in best_score_index:
				for clm in learning_result.columns:
					best_dict.update(
						{
						clm: learning_result[clm][idx]
						})
				for clm in chromosome_output.columns:
					best_dict.update(
						{
						clm: chromosome_output[clm][idx]
						})

				best_chromosome = best_chromosome.append(best_dict, ignore_index=True)

				for clm in best_chromosome.columns:
					if clm == 'Unnamed: 0':
						best_chromosome = best_chromosome.drop(columns='Unnamed: 0')

			# with pd.option_context('display.max_rows', None, 'display.max_columns', None):
			# 	print(best_chromosome)

			path_superhuman = macd_config.cfg['path_superhuman'] + signalpriority + path_slash + signaltype + path_slash
			if not os.path.exists(path_superhuman):
				os.makedirs(path_superhuman)

			if os.path.exists(path_superhuman + symbol + '.csv'):
				os.remove(path_superhuman + symbol + '.csv')

			best_chromosome.to_csv(path_superhuman + symbol + '.csv')
		#//////////////////////

	def calculator_macd(self):

		symbol = self.elements['symbol']
		apply_to = self.elements[__class__.__name__ + '_apply_to']
		macd_read = ind.macd(
							self.elements['dataset_5M'][symbol][apply_to],
							fast = self.elements[__class__.__name__ + '_fast'],
							slow = self.elements[__class__.__name__ + '_slow'],
							signal = self.elements[__class__.__name__ + '_signal']
							)

		column_macds = macd_read.columns[2]
		column_macd = macd_read.columns[0]
		column_macdh = macd_read.columns[1]

		macd = pd.DataFrame(
							{
								'macds': macd_read[column_macds],
								'macd': macd_read[column_macd],
								'macdh': macd_read[column_macdh],
							}
							).dropna(inplace = False)
		
		return macd