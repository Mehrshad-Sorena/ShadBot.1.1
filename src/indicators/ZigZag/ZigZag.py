from zigzag import peak_valley_pivots
import pandas as pd

def Find(dataset, index_first, index_last):

	ZigZag = peak_valley_pivots(
								dataset['close'][index_first : index_last], 
								abs(dataset['close'][index_first : index_last].pct_change(1)).max(),
								-abs(dataset['close'][index_first : index_last].pct_change(1)).max()
								)

	ts_ZigZag = pd.Series(dataset['close'][index_first:index_last], index=dataset['close'][index_first : index_last].index)
	ts_ZigZag = ts_ZigZag[ZigZag != 0]

	return ts_ZigZag