import asyncio
import aiotools
import logging
from logging.config import dictConfig
from utils import read_approved

logging_config = dict(
    version = 1,
    formatters = {
        'f': {'format':
              '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'}
        },
    handlers = {
        'h': {'class': 'logging.StreamHandler',
              'formatter': 'f',
              'level': logging.DEBUG}
        },
    root = {
        'handlers': ['h'],
        'level': logging.DEBUG,
        },
)

dictConfig(logging_config)

logger = logging.getLogger()


class Worker():
    def __init__(self, host='slackbot', port=8765):
        self.host = host
        self.port = port


    async def handle_signal(self, reader, writer):
        apporved = await read_aprroved()
        logger.info("IT IS TIME TO CHECK REDIS {approved}")
        data = await reader.read(100)
        message = data.decode()
        addr = writer.get_extra_info('peername')
        logger.info("-------------->  Received %r from %r" % (message, addr))

        logger.info("--------------> Send: %r" % message)
        writer.write(data)
        await writer.drain()
        logger.info("--------------> Close the client socket")
        writer.close()


    def start(self):
        try:
            self.loop = asyncio.get_event_loop()
        except Exception as e:
            self.loop = asyncio.new_event_loop()

        coro = asyncio.start_server(self.handle_signal, self.host, self.port, loop=self.loop)
        server = self.loop.run_until_complete(coro)
        # Serve requests until Ctrl+C is pressed
        logger.info('================>>>>Serving on {}'.format(server.sockets[0].getsockname()))
        try:
            self.loop.run_forever()
        except KeyboardInterrupt:
            pass


    def stop(self):
        self.server.close()
        self.loop.run_until_complete(self.server.wait_closed())
        self.loop.close()
