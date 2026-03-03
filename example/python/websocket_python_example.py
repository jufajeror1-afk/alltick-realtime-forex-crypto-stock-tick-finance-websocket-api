import json
import time
import threading
import websocket    # pip install websocket-client

'''
# Special Note:
# GitHub: https://github.com/alltick/realtime-forex-crypto-stock-tick-finance-websocket-api
# Token Application: https://alltick.co
# Replace "testtoken" in the URL below with your own token
# API addresses for forex, cryptocurrencies, and precious metals:
# wss://quote.alltick.co/quote-b-ws-api
# Stock API address:
# wss://quote.alltick.co/quote-stock-b-ws-api
'''

class Feed(object):

    def __init__(self):
        # prompt for token and symbol
        token = input('请输入您的API_KEY (token): ').strip()
        if not token:
            raise ValueError('API_KEY不能为空')
        self.option = input('请输入期权合约代码，例如 AAPL230918C00150000，空则使用 AAPL.US: ').strip() or 'AAPL.US'
        self.url = f'wss://quote.alltick.co/quote-stock-b-ws-api?token={token}'
        self.ws = None

    def on_open(self, ws):
        """
        Callback object which is called at opening websocket.
        1 argument:
        @ ws: the WebSocketApp object
        """
        print('A new WebSocketApp is opened!')

        # subscribe to depth/tick for the selected option
        sub_param = {
            "cmd_id": 22002,  # depth quote
            "seq_id": 123,
            "trace": "subscribe-option",
            "data": {
                "symbol_list": [
                    {"code": self.option, "depth_level": 5}
                ]
            }
        }

        # If you want to run for a long time, you need to modify the code to send heartbeats periodically to avoid disconnection, please refer to the API documentation for details
        sub_str = json.dumps(sub_param)
        ws.send(sub_str)
        print("depth quote are subscribed!")

    def on_data(self, ws, string, type, continue_flag):
        """
        4 arguments.
        The 1st argument is this class object.
        The 2nd argument is utf-8 string which we get from the server.
        The 3rd argument is data type. ABNF.OPCODE_TEXT or ABNF.OPCODE_BINARY will be came.
        The 4th argument is continue flag. If 0, the data continue
        """

    def on_message(self, ws, message):
        """
        Called when a text message is received; parse JSON and display columns.
        """
        try:
            data = json.loads(message)
        except Exception:
            print('非JSON消息：', message)
            return
        # define columns same as HTTP script
        cols = [
            "contractID","symbol","expiration","strike","type","last","mark",
            "bid","bid_size","ask","ask_size","volume","open_intel","date",
            "implied_vc","delta","gamma","theta","vega","rho"
        ]
        flat = {}
        if isinstance(data, dict):
            flat.update(data)
            if isinstance(data.get('data'), dict):
                flat.update(data['data'])
        row = {c: flat.get(c) or (flat.get('open_int') if c=='open_intel' else None) for c in cols}
        # print row
        print('行情更新:')
        for c, v in row.items():
            print(f"  {c}: {v} ({type(v).__name__})")
        # optionally also dump raw
        #print('raw', data)

    def on_error(self, ws, error):
        """
        Callback object which is called when got an error.
        2 arguments:
        @ ws: the WebSocketApp object
        @ error: exception object
        """
        print(error)

    def on_close(self, ws, close_status_code, close_msg):
        """
        Callback object which is called when the connection is closed.
        2 arguments:
        @ ws: the WebSocketApp object
        @ close_status_code
        @ close_msg
        """
        print('The connection is closed!')

    def start(self):
        self.ws = websocket.WebSocketApp(
            self.url,
            on_open=self.on_open,
            on_message=self.on_message,
            on_data=self.on_data,
            on_error=self.on_error,
            on_close=self.on_close,
        )
        threading.Thread(target=self.thread_heartbeat).start()
        self.ws.run_forever()
    
    def thread_heartbeat(self):
        while True:
            time.sleep(10)  # 每 10 秒发送一次心跳
            if self.ws.sock and self.ws.sock.connected:
                heartbeat = {
                    "cmd_id":22000,
                    "seq_id":123,
                    "trace":"heartbeat",
                    "data":{}
                }
                self.ws.send(json.dumps(heartbeat))  # 发送心跳消息
                print("Sent heartbeat")


if __name__ == "__main__":
    feed = Feed()
    feed.start()
