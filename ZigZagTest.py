from src.utils.DataReader.MetaTraderReader5.LoginGetData import LoginGetData as getdata
import numpy as np
import pandas as pd
import pandas_ta as ind
from zigzag import peak_valley_pivots
import matplotlib.pyplot as plt


loging = getdata()
dataset_5M, dataset_1H = loging.readall(symbol = 'XAUUSD_i', number_5M = 4000, number_1H = 0)
dataset_5M = dataset_5M['XAUUSD_i']

macd_read = ind.macd(
							dataset_5M['close'],
							fast = 12,
							slow = 26,
							signal = 9
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

for slicer in range(50, len(dataset_5M.index) - 50, 50):

	pivots = peak_valley_pivots(dataset_5M['close'][slicer:slicer + 50], abs(dataset_5M['close'][slicer:slicer + 50].pct_change(1)).mean(),
																		 -abs(dataset_5M['close'][slicer:slicer + 50].pct_change(1)).mean())
	ts_pivots = pd.Series(dataset_5M['close'][slicer:slicer + 50], index=dataset_5M['close'][slicer:slicer + 50].index)
	ts_pivots = ts_pivots[pivots != 0]

	print(ts_pivots.values)
	print(ts_pivots.values[-2])
	dataset_5M['close'][slicer:slicer + 50].plot()
	ts_pivots.plot(style='g-o');
	plt.show()


pivots = peak_valley_pivots(macd['macd'][:3999], abs(macd['macd'][:3999].pct_change(1)).min(), -abs(macd['macd'][:3999].pct_change(1)).min())

print('pivots = ', pivots)
ts_pivots = pd.Series(macd['macd'][:3999], index=macd['macd'][:3999].index)
ts_pivots = ts_pivots[pivots != 0]

print(ts_pivots)
macd['macd'][:3999].plot()
ts_pivots.plot(style='g-o');
plt.show()
