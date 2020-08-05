import aredis
from aredis import StrictRedis
import aiotools
import asyncio
from time import sleep
import json
import os
read_env = lambda property: os.environ.get(property, None)

redis = dict()
redis['db'] = read_env('REDIS_DB')
redis['host'] = read_env('REDIS_HOST')
redis['port'] = read_env('REDIS_PORT')
ar = StrictRedis(**redis)


async def echo(reader, writer):
    while(await ar.llen('approved')!=0):
        item = await  ar.lpop('searched_questions')
        d = json.loads(item)
        print(f"GOT APPROVED ANSWER {d['answer']}")

    print("CHECKING --> ")
    data = await reader.read(100)
    writer.write(data)
    await writer.drain()
    writer.close()


@aiotools.actxmgr
async def worker_main(loop, pidx, args):

    # Create a listening socket with SO_REUSEPORT option so that each worker
    # process can share the same listening port and the kernel balances
    # incoming connections across multiple worker processes.
    server = await asyncio.start_server(echo, '0.0.0.0', 8888, reuse_port=True)
    print(f'[{pidx}] started')

    yield  # wait until terminated

    server.close()
    await server.wait_closed()
    print(f'[{pidx}] terminated')


if __name__ == '__main__':
    # Run the above server using 4 worker processes.
    aiotools.start_server(worker_main, num_workers=4)
