import GDAX, time
from MarinerStrategy import MarinerStrategy


if __name__ == '__main__':
    MARKET_SENTIMENT = 'BEAR'
    TICKER = 'ETH-USD'
    WHALE_THRESHOLD = 100
    whale_strat = MarinerStrategy(sentiment = MARKET_SENTIMENT, ticker = TICKER, threshold = WHALE_THRESHOLD)
    whale_strat.start()