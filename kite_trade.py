import os
from types import SimpleNamespace
try:
    import requests
except ImportError:
    os.system('python -m pip install requests')
try:
    import dateutil
except ImportError:
    os.system('python -m pip install python-dateutil')


import requests
import dateutil.parser


def get_enctoken(userid, password, twofa):
    session = requests.Session()
    response = session.post('https://kite.zerodha.com/api/login', data={
        "user_id": userid,
        "password": password
    })
    response = session.post('https://kite.zerodha.com/api/twofa', data={
        "request_id": response.json()['data']['request_id'],
        "twofa_value": twofa,
        "user_id": response.json()['data']['user_id']
    })
    enctoken = response.cookies.get('enctoken')
    if enctoken:
        return enctoken
    else:
        raise Exception("Enter valid details !!!!")


class KiteApp:
    PRODUCT = SimpleNamespace(MIS='MIS', CNC='CNC', NRML='NRML', CO='CO')
    ORDER_TYPE = SimpleNamespace(MARKET="MARKET", LIMIT="LIMIT", SLM="SL-M", SL="SL")
    VARIETY = SimpleNamespace(REGULAR="regular", CO="co", AMO="amo")
    TRANSACTION = SimpleNamespace(BUY='BUY', SELL='SELL')
    VALIDITY = SimpleNamespace(DAY='DAY',IOC='IOC')
    EXCHANGE = SimpleNamespace(NSE='NSE', BSE='BSE', NFO='NFO', CDS='CDS', BFO='BFO', MCX='MCX')

    def __init__(self, enctoken):
        self.enctoken = enctoken
        self.headers = {"Authorization": f"enctoken {self.enctoken}"}
        self.session = requests.session()
        self.root_url = "https://kite.zerodha.com/oms"
        self.session.get(self.root_url, headers=self.headers)

    def instruments(self, exchange=None):
        data = self.session.get(f"https://api.kite.trade/instruments").text.split("\n")
        Exchange = []
        for i in data[1:-1]:
            row = i.split(",")
            if exchange is None or exchange == row[11]:
                Exchange.append({'instrument_token': int(row[0]), 'exchange_token': row[1], 'tradingsymbol': row[2],
                                 'name': row[3][1:-1], 'last_price': float(row[4]),
                                 'expiry': dateutil.parser.parse(row[5]).date() if row[5] != "" else None,
                                 'strike': float(row[6]), 'tick_size': float(row[7]), 'lot_size': int(row[8]),
                                 'instrument_type': row[9], 'segment': row[10],
                                 'exchange': row[11]})
        return Exchange

    def historical_data(self, instrument_token, from_date, to_date, interval, continuous=False, oi=False):
        params = {"from": from_date,
                  "to": to_date,
                  "interval": interval,
                  "continuous": 1 if continuous else 0,
                  "oi": 1 if oi else 0}
        lst = self.session.get(
            f"{self.root_url}/instruments/historical/{instrument_token}/{interval}", params=params,
            headers=self.headers).json()["data"]["candles"]
        records = []
        for i in lst:
            record = {"date": dateutil.parser.parse(i[0]), "open": i[1], "high": i[2], "low": i[3],
                      "close": i[4], "volume": i[5],}
            if len(i) == 7:
                record["oi"] = i[6]
            records.append(record)
        return records

    def margins(self):
        margins = self.session.get(f"{self.root_url}/user/margins", headers=self.headers).json()["data"]
        return margins

    def profile(self):
        profile = self.session.get(f"{self.root_url}/user/profile", headers=self.headers).json()["data"]
        return profile

    def orders(self):
        orders = self.session.get(f"{self.root_url}/orders", headers=self.headers).json()["data"]
        return orders

    def positions(self):
        positions = self.session.get(f"{self.root_url}/portfolio/positions", headers=self.headers).json()["data"]
        return positions

    def place_order(self, variety, exchange, tradingsymbol, transaction_type, quantity, product, order_type, price=None,
                    validity=None, disclosed_quantity=None, trigger_price=None, squareoff=None, stoploss=None,
                    trailing_stoploss=None, tag=None):
        params = locals()
        del params["self"]
        for k in list(params.keys()):
            if params[k] is None:
                del params[k]
        order_id = self.session.post(f"{self.root_url}/orders/{variety}",
                                     data=params, headers=self.headers).json()["data"]["order_id"]
        return order_id

    def modify_order(self, variety, order_id, parent_order_id=None, quantity=None, price=None, order_type=None,
                     trigger_price=None, validity=None, disclosed_quantity=None):
        params = locals()
        del params["self"]
        for k in list(params.keys()):
            if params[k] is None:
                del params[k]

        order_id = self.session.put(f"{self.root_url}/orders/{variety}/{order_id}",
                                    data=params, headers=self.headers).json()["data"][
            "order_id"]
        return order_id

    def cancel_order(self, variety, order_id, parent_order_id=None):
        order_id = self.session.delete(f"{self.root_url}/orders/{variety}/{order_id}",
                                       data={"parent_order_id": parent_order_id} if parent_order_id else {},
                                       headers=self.headers).json()["data"]["order_id"]
        return order_id
