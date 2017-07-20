import gdax
from MarinerStrategy import MarinerStrategy

if __name__ == '__main__':
    MARKET_SENTIMENT = 'BEAR'
    TICKER = 'ETH-USD'
    PERCENT = .00025 #backtest to choose percent volume threshold
    whale_strat = MarinerStrategy(sentiment = MARKET_SENTIMENT, ticker = TICKER, percent = PERCENT)
    whale_strat.run()