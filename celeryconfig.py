from kombu.common import Broadcast
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
broker_connection_max_retries = rabbitmq_conf['max_connection_attempts']
broker_transport_options = {
	'max_retries': rabbitmq_conf['max_task_retries'],
	'interval_start': 0,
	'interval_step': 0.2,
	'interval_max': 0.2,
}
result_backend = 'rpc://'
result_persistent = False
result_expires = 60

task_queues = [
	Broadcast('bcast'),
]

# broadcasting is really weird... see: https://github.com/celery/celery/issues/4582
# for celery documentation: https://celery.readthedocs.io/en/latest/userguide/routing.html#broadcast
# for kombu.common.Broadcast: http://docs.celeryproject.org/projects/kombu/en/latest/reference/kombu.common.html
task_routes = {
	'streaming.stop_stream': {
		'queue': 'bcast',
		'exchange': 'bcast'
	},
}