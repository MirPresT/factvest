import pandas as pd
import requests
from .pretty_json import prettyJson as pj

# Sample API Object
sample_api_request = {
    'sample': True,
    'base_endpoint': 'stock',
    'symbols': ['intc'],
    'endpoints': ['quote'],
    'other_options': {},
}

base_url = 'https://api.iextrading.com/1.0'

class IexApi:
    def __init__(self):
        pass
    def get_data(self, api_request=sample_api_request):
        raw_data = self.get_iex_stock_data(
            api_request['base_endpoint'],
            api_request['symbols'],
            api_request['endpoints'],
            api_request['other_options']
        )

        try:
            if api_request['sample']:
                pj(raw_data)
        except Exception:
            pass

        return raw_data
    def make_request(self, url, options):
        return requests.get(**{
            'url': url,
            'params': options
        }).json()
    def many_sym_fmt_data(self, symbols, url, options, data):
        data_list = []
        for symbol in symbols:
            data_list.append({
                'symbol': symbol,
                'info': data[symbol]
            })
        return data_list
    def get_iex_stock_data(self, base_endpoint, symbols, endpoints, unique_params):
        # This function normalizes the iex json response so we can
        # view the information regardless of if we batch requests or not.
        # In other words, we get a similarly structured response regardless of
        # how many symbols we look up or how many end points we request
        symbols = [sym.upper() for sym in symbols]
        endpoints = [endpoint.lower() for endpoint in endpoints]
        multiple_symbols = len(symbols) > 1
        multiple_endpoints = len(endpoints) > 1

        single_symb_single_endp = not multiple_symbols and not multiple_endpoints
        single_symb_many_endp = not multiple_symbols and multiple_endpoints
        many_symb_single_endp = multiple_symbols and not multiple_endpoints
        many_symb_many_endp = multiple_symbols and multiple_endpoints

        if single_symb_single_endp:
            url = '{}/{}/{}/{}/'.format(
                base_url, base_endpoint,
                symbols[0], endpoints[0]
            )
            options = {**unique_params}
            response_data = self.make_request(url, options)

            data = [{
                'symbol': symbols[0],
                'info': {endpoints[0]: response_data}
            }]
        elif single_symb_many_endp:
            url = '{}/{}/{}/batch'.format(base_url, base_endpoint, symbols[0])

            options = {
                'types': ','.join(endpoints),
                **unique_params
            }

            response_data = self.make_request(url, options)
            info = {}

            for point in endpoints:
                info[point] = response_data[point]

            data = [{
                'symbol': symbols[0],
                'info': info
            }]
        elif many_symb_single_endp:
            url = '{}/{}/market/batch'.format(base_url, base_endpoint)

            options = {
                'symbols': ','.join(symbols),
                'types': endpoints[0],
                **unique_params
            }
            response_data = self.make_request(url, options)
            data = self.many_sym_fmt_data(symbols, url, options, response_data)
        elif many_symb_many_endp:
            url = '{}/{}/market/batch'.format(base_url, base_endpoint)

            options = { # params
                'symbols': ','.join(symbols),
                'types': ','.join(endpoints),
                **unique_params
            }
            response_data = self.make_request(url, options)
            data = self.many_sym_fmt_data(symbols, url, options, response_data)

        return data
