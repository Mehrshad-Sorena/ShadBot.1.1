from GeneticLearningRunner.StochAstic import Runner_BuyPrimary as StochAsticRunner
from GeneticLearningRunner.MACD import Runner_BuyPrimary as MACDRunner
from GeneticLearningRunner.RSI import Runner_BuyPrimary as RSIRunner

# for i in range(0, 500):
# print('Turn = ', i)
MACDRunner.Run(3000)
# StochAsticRunner.Run(6000)
# RSIRunner.Run(3000)