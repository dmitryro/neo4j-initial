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
    while(r.llen('approved')!=0):
        item = r.lpop('searched_questions')
        d = json.loads(item)
        print(f"GOT APPROVED ANSWER {d['answer']}")


if __name__=="__main__":
    main()
