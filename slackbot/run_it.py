import logging
from websocket_server import WebsocketServer

def handle_message(client, server, message):
    print("MESSAGE WAS RECEIVED {message}")

server = WebsocketServer(8765, host='localhost', loglevel=logging.INFO)
server.set_fn_message_received(handle_message)

server.run_forever()


