from pika import adapters, connection, credentials
from pika.exceptions import AMQPConnectionError
from tornado.ioloop import IOLoop

# simple global variable
__conn = None

class RabbitMq:
	@staticmethod
	def create_or_get_instance(rabbitmq_conf):
		global __conn
		if __conn is None:
			connection_conf = []
			creds = credentials.PlainCredentials(rabbitmq_conf['user'], rabbitmq_conf['pass'])
			hosts = rabbitmq_conf['hosts']
			for host_idx in range(len(hosts)):
				params = connection.ConnectionParameters(host=hosts[host_idx], credentials=creds)
				if host_idx == len(hosts) - 1:
					params.connection_attempts = rabbitmq_conf['connection_attempts']
					params.retry_delay = rabbitmq_conf['retry_delay']
				connection_conf.append(params)
			try:
				__conn = adapters.select_connection.SelectConnection(connection_conf, custom_ioloop=IOLoop.current())
				__conn.add_on_close_callback(RabbitMq._on_connection_close(rabbitmq_conf))
			except AMQPConnectionError as e:
				print(f'Failed to connect to any of the RabbitMq hosts {hosts} because {e}')
				raise e
		return __conn
	
	@staticmethod
	def _on_connection_close(rabbitmq_conf):
		def _wrap_around():
			global __conn
			__conn = None
			RabbitMq.create_or_get_instance(rabbitmq_conf)
		return _wrap_around()