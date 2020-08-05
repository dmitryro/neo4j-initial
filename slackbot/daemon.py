import asyncio
import aiotools
import logging
from utils import read_env, read_approved

logger = logging.getLogger(__name__)

async def listen(reader, writer):
    data = await reader.read(100)
    writer.write(data)
    await writer.drain()
    writer.close()
    approved = await read_approved()
    logger.info(f"WE WERE CONTACTED {approved}")

@aiotools.server
async def myworker(loop, pidx, args):
    server = await asyncio.start_server(listen, 'slackbot', 8765,
        reuse_port=True, loop=loop)
    logger.info(f'[{pidx}] started')
    yield  # wait until terminated
    server.close()
    await server.wait_closed()
    logger.info(f"[{pidx}] terminated")


def run_server():
   aiotools.start_server(myworker, num_workers=4)
 
if __name__ == '__main__':
   # Run the above server using 4 worker processes.
   aiotools.start_server(myworker, num_workers=4)
