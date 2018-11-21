from kombu import Queue, Exchange
import json
conf_fd = open('config.json')
rabbitmq_conf = json.load(conf_fd)['rabbitmq']

def create_rabbitmq_broker_uri():
	hosts = rabbitmq_conf['hosts']
	user = rabbitmq_conf['user']
	passwd = rabbitmq_conf['password']
	port = rabbitmq_conf['port']
	vhost = rabbitmq_conf['vhost']
	for host in hosts:
		yield f'amqp://{user}:{passwd}@{host}:{port}{vhost}'

broker_url = [uri for uri in create_rabbitmq_broker_uri()]
broker_connection_max_retries = rabbitmq_conf['connection_attempts']
result_backend = 'rpc://'
result_persistent = False
result_expires = 60

# task_queues = (
# 	Queue('queue-request', queue_arguments={'x-message-ttl': 60000}),
# # 	# will need to change this to a Broadcast, currently stop_stream does not work with more than one concurrency
# # 	# Queue(
# # 	# 	name='queue-stop-stream',
# # 	# 	exchange=Exchange('request-topic', type='fanout'),
# # 	# 	queue_arguments={'x-message-ttl': 60000, 'x-max-priority': 1},
# # 	# 	durable=True
# # 	# ),
# )

# # need to test this on "multiple" machines (aka Docker containers) and see what happens with no queue
# # predetermined. Guessing it would do a broadcast since multiple machines, which if that is the case we
# # want to declare static queue
# task_routes = {
# 	'streaming.start_stream': {
# 		'queue': 'queue-request',
# 		'routing_key': 'stream.start'
# 	}
# }