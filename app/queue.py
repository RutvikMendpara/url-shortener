from redis import Redis
from rq import Queue

redis_conn = Redis(host="localhost", port=6379)

queue = Queue("analytics", connection=redis_conn)