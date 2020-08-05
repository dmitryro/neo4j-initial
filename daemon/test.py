import json
import os
from redis import StrictRedis as RegularStrictRedis
read_env = lambda property: os.environ.get(property, None)

redis = dict()
redis['db'] = read_env('REDIS_DB')
redis['host'] = read_env('REDIS_HOST')
redis['port'] = read_env('REDIS_PORT')
r = RegularStrictRedis(**redis)



def main():
    
    msg = {'question': 'one', "answer": 'one'}
    r.lpush('approved', json.dumps(msg).encode('utf-8'))
    msg = {'question': 'two', "answer": 'two'}
    r.lpush('approved', json.dumps(msg).encode('utf-8'))
    msg = {'question': 'three', "answer": 'three'}
    r.lpush('approved', json.dumps(msg).encode('utf-8'))
    print("Added new records to approved")


if __name__=="__main__":
    main()
