import requests, json
from moneyed import Money, USD
from decimal import Decimal as D

class AEF:
    def __init__(self):
        self.load_portfolio()
    def load_portfolio(self):
        with open('aef_portfolio.json', 'r') as f:
            self.port = json.loads(f.read())
            self.port['cash'] = Money(self.port['cash'], USD)
            self.symbols = [k['symbol'] for k in self.port['holdings']]
    def get_prices(self):
        port = self.port
        cash = port['cash']
        holdings = port['holdings']
        symbols = self.symbols

        price_data = requests.get(**{
            'url': 'https://api.iextrading.com/1.0/stock/market/batch',
            'params': {
                'symbols': ','.join(self.symbols),
                'types': 'price'
            }
        }).json()

        for stock in holdings:

            stock['price'] = Money(price_data[stock['symbol']]['price'], USD)
            stock['value'] = Money(stock['price'].amount * D(stock['shares']), USD)
    def add_weights(self):
        port = self.port
        holdings_value = Money(sum([x['value'].amount for x in port['holdings']]), USD)
        port['balance'] = holdings_value + port['cash']
        for stock in port['holdings']:
            stock['weight'] = D(stock['value'] / port['balance']).quantize(D('0.0000'))
    def get_perf(self):
        price_history = requests.get(**{
            'url': 'https://api.iextrading.com/1.0/stock/market/batch',
            'params': {
                'symbols': ','.join(self.symbols),
                'types': 'chart',
                'range': '1m',
            }
        }).json()

        for stock in self.port['holdings']:
            symbol = stock['symbol']
            prices = price_history[symbol]['chart']
            five_days_prior = prices[len(prices) - 6]['close']
            most_recent = prices[len(prices) - 1]['close']
            five_day_change = D(round(((most_recent / five_days_prior) - 1), 4)).quantize(D('0.0000'))
            stock['five_day_perf'] = five_day_change
            stock['wt_perf'] = round(float(five_day_change * stock['weight']), 4)
    def biggest_impact(self):
        # print(max(self.port['holdings'], key=lambda stock: stock['wt_perf']))
        wt_perfs = [x['wt_perf'] for x in self.port['holdings']]
        # top 3 contributors
        top_3_names = [name for (n, name) in sorted(zip(wt_perfs, self.symbols), reverse=True)[:3]]
        bottom_3_names = [name for (n, name) in sorted(zip(wt_perfs, self.symbols), reverse=False)[:3]]

        def get_stock(symbol):
            return list(filter(lambda x: x['symbol'] == symbol , self.port['holdings']))[0]

        self.top_3_stocks = list(map(get_stock, top_3_names))
        self.bottom_3_stocks = list(map(get_stock, bottom_3_names))
    def display_results(self):
        print("Top 3 Contributors to our Performance\n")
        for stock in self.top_3_stocks:
            print('\t{}\n'.format(stock['symbol']))
            print('\t\t5 Day Perf: {}%'.format(round(stock['five_day_perf'] * 100, 2)))
            print('\t\tWeight: {}%'.format(round(stock['weight'] * 100, 2)))
            print('\t\tWeighted Performance: {}%\n'.format(round(stock['wt_perf'] * 100, 2)))
        print("Bottom 3 Contributors to our Performance\n")
        for stock in self.bottom_3_stocks:
            print('\t{}\n'.format(stock['symbol']))
            print('\t\t5 Day Perf: {}%'.format(round(stock['five_day_perf'] * 100, 2)))
            print('\t\tWeight: {}%'.format(round(stock['weight'] * 100, 2)))
            print('\t\tWeighted Performance: {}%\n'.format(round(stock['wt_perf'] * 100, 2)))

AEF = AEF()
AEF.get_prices()
AEF.add_weights()
AEF.get_perf()
AEF.biggest_impact()
AEF.display_results()