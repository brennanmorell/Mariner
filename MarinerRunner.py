import GDAX, time
from MarinerStrategy import MarinerStrategy

if __name__ == '__main__':
    MARKET_SENTIMENT = 'BEAR'
    TICKER = 'ETH-USD'
    PERCENT = .0005
    whale_strat = MarinerStrategy(sentiment = MARKET_SENTIMENT, ticker = TICKER, percent = PERCENT)
    whale_strat.start()