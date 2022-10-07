from src.utils.DataReader.MetaTraderReader5.LoginGetData import LoginGetData as getdata
from src.utils.Optimizers import OptimizersRunner
from src.utils.Optimizers import NoiseCanceller
from src.utils.Optimizers import Optimizers

loging = getdata()

# dataset_5M, dataset_1H = loging.readall(symbol = 'XAUUSD_i', number_5M = 'all', number_1H = 'all')

# optimizersrunner = OptimizersRunner.OptimizersRunner() 

# optimizersrunner.symbol = 'XAUUSD_i'

# optimizersrunner.Run()

dataset_5M, dataset_1H = loging.readall(symbol = 'XAUUSD_i', number_5M = 'all', number_1H = 0)
symbol = 'XAUUSD_i'

# dataset_5M_real, _ = loging.readall(symbol = 'XAUUSD_i', number_5M = 'all', number_1H = 0)
# dataset_5M_real = dataset_5M_real[parameters.elements['symbol']]

optimizers = Optimizers.Optimizers() 

noise_canceller = NoiseCanceller.NoiseCanceller()
dataset_5M['XAUUSD_i']['close'] = noise_canceller.NoiseWavelet(dataset = dataset_5M['XAUUSD_i'], applyto = 'close')
dataset_5M['XAUUSD_i']['open'] = noise_canceller.NoiseWavelet(dataset = dataset_5M['XAUUSD_i'], applyto = 'open')
dataset_5M['XAUUSD_i']['high'] = noise_canceller.NoiseWavelet(dataset = dataset_5M['XAUUSD_i'], applyto = 'high')
dataset_5M['XAUUSD_i']['low'] = noise_canceller.NoiseWavelet(dataset = dataset_5M['XAUUSD_i'], applyto = 'low')
dataset_5M['XAUUSD_i']['HL/2'] = noise_canceller.NoiseWavelet(dataset = dataset_5M['XAUUSD_i'], applyto = 'HL/2')
dataset_5M['XAUUSD_i']['HLC/3'] = noise_canceller.NoiseWavelet(dataset = dataset_5M['XAUUSD_i'], applyto = 'HLC/3')
dataset_5M['XAUUSD_i']['HLCC/4'] = noise_canceller.NoiseWavelet(dataset = dataset_5M['XAUUSD_i'], applyto = 'HLCC/4')
dataset_5M['XAUUSD_i']['OHLC/4'] = noise_canceller.NoiseWavelet(dataset = dataset_5M['XAUUSD_i'], applyto = 'OHLC/4')

print('Data Ready .... ')
# sys.exit()

optimizers.symbol = 'XAUUSD_i'
optimizers.sigpriority = 'primary'
optimizers.sigtype = 'buy'
optimizers.turn = 400
optimizers.dataset = dataset_5M.copy()
optimizers.timeframe = '5M'

optimizers.MacdOptimizer()

optimizers.symbol = 'XAUUSD_i'
optimizers.sigpriority = 'secondry'
optimizers.sigtype = 'buy'
optimizers.turn = 400
optimizers.dataset = dataset_5M.copy()
optimizers.timeframe = '5M'

optimizers.MacdOptimizer()

# optimizers.symbol = 'XAUUSD_i'
# optimizers.sigpriority = 'primary'
# optimizers.sigtype = 'sell'
# optimizers.turn = 100
# optimizers.dataset = dataset_5M.copy()
# optimizers.timeframe = '5M'

# optimizers.MacdOptimizer()

optimizers.symbol = 'XAUUSD_i'
optimizers.sigpriority = 'secondry'
optimizers.sigtype = 'sell'
optimizers.turn = 400
optimizers.dataset = dataset_5M.copy()
optimizers.timeframe = '5M'

optimizers.MacdOptimizer()

# optimizers.symbol = 'XAUUSD_i'
# optimizers.sigpriority = 'primary'
# optimizers.sigtype = 'buy'
# optimizers.turn = 100
# optimizers.dataset = dataset_5M.copy()
# optimizers.timeframe = '5M'

# optimizers.StochAsticOptimizer()

# optimizers.symbol = 'XAUUSD_i'
# optimizers.sigpriority = 'secondry'
# optimizers.sigtype = 'buy'
# optimizers.turn = 100
# optimizers.dataset = dataset_5M.copy()
# optimizers.timeframe = '5M'

# optimizers.StochAsticOptimizer()

# optimizers.symbol = 'XAUUSD_i'
# optimizers.sigpriority = 'primary'
# optimizers.sigtype = 'sell'
# optimizers.turn = 100
# optimizers.dataset = dataset_5M.copy()
# optimizers.timeframe = '5M'

# optimizers.StochAsticOptimizer()

# optimizers.symbol = 'XAUUSD_i'
# optimizers.sigpriority = 'secondry'
# optimizers.sigtype = 'sell'
# optimizers.turn = 100
# optimizers.dataset = dataset_5M.copy()
# optimizers.timeframe = '5M'

# optimizers.StochAsticOptimizer()

# optimizers.symbol = 'XAUUSD_i'
# optimizers.sigpriority = 'primary'
# optimizers.sigtype = 'buy'
# optimizers.turn = 100
# optimizers.dataset = dataset_5M.copy()
# optimizers.timeframe = '5M'

# optimizers.RSIOptimizer()

# optimizers.symbol = 'XAUUSD_i'
# optimizers.sigpriority = 'secondry'
# optimizers.sigtype = 'buy'
# optimizers.turn = 100
# optimizers.dataset = dataset_5M.copy()
# optimizers.timeframe = '5M'

# optimizers.RSIOptimizer()

# optimizers.symbol = 'XAUUSD_i'
# optimizers.sigpriority = 'primary'
# optimizers.sigtype = 'sell'
# optimizers.turn = 100
# optimizers.dataset = dataset_5M.copy()
# optimizers.timeframe = '5M'

# optimizers.RSIOptimizer()

# optimizers.symbol = 'XAUUSD_i'
# optimizers.sigpriority = 'secondry'
# optimizers.sigtype = 'sell'
# optimizers.turn = 100
# optimizers.dataset = dataset_5M.copy()
# optimizers.timeframe = '5M'

# optimizers.RSIOptimizer()