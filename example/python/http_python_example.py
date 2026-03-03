import time
import requests
import json

# Extra headers
test_headers = {
    'Content-Type': 'application/json'
}

'''
# Special Note:
# GitHub: https://github.com/alltick/realtime-forex-crypto-stock-tick-finance-websocket-api
# Token Application: https://alltick.co
# Replace "testtoken" in the URL below with your own token
# API addresses for forex, cryptocurrencies, and precious metals:
# https://quote.alltick.co/quote-b-ws-api
# Stock API address:
# https://quote.alltick.co/quote-stock-b-ws-api
Encode the following JSON and copy it to the "query" field of the HTTP query string
{"trace": "python_http_test1", "data": {"code": "700.HK", "kline_type": 1, "kline_timestamp_end": 0, "query_kline_num": 2, "adjust_type": 0}}
{"trace": "python_http_test2", "data": {"symbol_list": [{"code": "700.HK"}, {"code": "UNH.US"}]}}
{"trace": "python_http_test3", "data": {"symbol_list": [{"code": "700.HK"}, {"code": "UNH.US"}]}}
'''
# Ask the user for their API token; prompt if not provided via environment
api_token = input('请输入您的API_KEY (token): ').strip()
if not api_token:
    raise ValueError('API_KEY不能为空')

# prepare example URLs using the user token and querying a foreign option contract
# (the API treats options like any other symbol code)
# prompt for a symbol so you can test with different contracts
OPTION_CODE = input('请输入期权合约代码（例如 AAPL230918C00150000），按回车默认使用 AAPL.US: ').strip()
if not OPTION_CODE:
    print('未输入期权代码，将使用默认现货 AAPL.US 进行测试')
    OPTION_CODE = 'AAPL.US'

base = 'https://quote.alltick.co/quote-stock-b-api'

# prepare three queries with the chosen code
query1 = '{"trace":"python_http_test1","data":{"code":"' + OPTION_CODE + '","kline_type":1,"kline_timestamp_end":0,"query_kline_num":2,"adjust_type":0}}'
test_url1 = f"{base}/kline?token={api_token}&query={requests.utils.quote(query1)}"

query2 = '{"trace":"python_http_test2","data":{"symbol_list":[{"code":"' + OPTION_CODE + '"}]}}'
query3 = '{"trace":"python_http_test3","data":{"symbol_list":[{"code":"' + OPTION_CODE + '"}]}}'
# URL-encode queries using requests.utils.quote for safety
encoded2 = requests.utils.quote(query2)
encoded3 = requests.utils.quote(query3)


test_url2 = f"{base}/depth-tick?token={api_token}&query={encoded2}"

test_url3 = f"{base}/trade-tick?token={api_token}&query={encoded3}"

resp1 = requests.get(url=test_url1, headers=test_headers)
# pause ten seconds between each call to avoid rate limiting
time.sleep(10)
resp2 = requests.get(url=test_url2, headers=test_headers)

# another ten‑second delay before the next request
time.sleep(10)
resp3 = requests.get(url=test_url3, headers=test_headers)

# we define the output columns you requested and format a row per response
columns = [
    "contractID",
    "symbol",
    "expiration",
    "strike",
    "type",
    "last",
    "mark",
    "bid",
    "bid_size",
    "ask",
    "ask_size",
    "volume",
    "open_intel",  # note: might appear as open_int or open_intel in data
    "date",
    "implied_vc",
    "delta",
    "gamma",
    "theta",
    "vega",
    "rho"
]

for idx, resp in enumerate((resp1, resp2, resp3), start=1):
    try:
        data = resp.json()
    except ValueError:
        print(f"response {idx} not JSON:\n{resp.text}")
        continue

    print(f"\n--- response {idx} ---")

    # flattened dict to search both top-level and inside data
    flat = {}
    if isinstance(data, dict):
        flat.update(data)
        if isinstance(data.get('data'), dict):
            flat.update(data['data'])

    # assemble row according to columns list
    row = {}
    for col in columns:
        # try direct key, also allow mapping open_intel←open_int
        if col in flat:
            row[col] = flat[col]
        elif col == 'open_intel' and 'open_int' in flat:
            row[col] = flat['open_int']
        else:
            row[col] = None

    # print row with types
    for col, val in row.items():
        print(f"{col} ({type(val).__name__}): {val}")

    # also show complete object for debugging
    print(f"full object: {data}")
