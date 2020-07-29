import asyncio

import aiotools

import os
import logging
from slack import RTMClient
from slack.errors import SlackApiError

logger = logging.getLogger(__name__)
read_env = lambda property: os.environ.get(property, None)


@RTMClient.run_on(event='message')
def process_messages(**payload):
    data = payload['data']
    logger.info(f"SLACK DAEMON - WE GOT SOMETHING {data}")

    if 'text' in data:
        logger.info(f"text was in data {data['text']}")
        if 'store' in data.get('text', []):
            logger.info("sending store")
            store(payload)
        elif 'answer' in data.get('text', []):
            logger.info("sending answer")
            answer(payload)
        elif 'edit' in data.get('text', []):
            logger.info("sending edit")
            edit(payload)

def main():
    token=read_env("SLACK_TOKEN")
    rtm_client = RTMClient(token=token)
    rtm_client.start()
    logger.info("Runnign slack monitor ... ")


async def echo(reader, writer):
    data = await reader.read(100)
    writer.write(data)
    await writer.drain()
    writer.close()


@aiotools.actxmgr
async def worker_main(loop, pidx, args):

    # Create a listening socket with SO_REUSEPORT option so that each worker
    # process can share the same listening port and the kernel balances
    # incoming connections across multiple worker processes.
    main()
    loop = asyncio.get_event_loop()
    
    server = await asyncio.start_server(echo, '0.0.0.0', 8888,
                                        reuse_port=True, loop=loop)
    print(f'[{pidx}] started')

    yield  # wait until terminated

    server.close()
    await server.wait_closed()
    print(f'[{pidx}] terminated')


if __name__ == '__main__':
    # Run the above server using 4 worker processes.
    aiotools.start_server(worker_main, num_workers=4)
