import aiokafka
import kafka
import json

def serializer(value):
    return json.dumps(value).encode()

class Kafka:
	"""Kafka wrapper
	Wraps around aiokafka
	"""
	_producer = None
	_consumer = None

	@staticmethod
	def create_producer_instance(client_id=None, config={}):
		"""Creates producer instance
		
		:param client_id: Client ID, defaults to None
		:type client_id: str, optional
		:param config: Configuration for kafka, defaults to {}
		:type config: dict, optional
		:raises Exception: [description]
		:raises Exception: [description]
		:return: A KafkaProducer suitable for threaded environment
		:rtype: [kafka.KafkaProducer]
		"""

		if Kafka._producer is None:
			if 'bootstrap_servers' not in config:
				raise Exception('No bootstrap servers have been configured')
			Kafka._producer = kafka.KafkaProducer(
				bootstrap_servers=config['bootstrap_servers'],
				client_id=client_id,
				linger_ms=config.get('linger_ms', 100),
				value_serializer=serializer
			)
		return Kafka._producer
	
	@staticmethod
	def get_producer_instance():
		if Kafka._producer is None:
			raise Exception('Producer has not been created yet please call "create_producer_instance" first')
		return Kafka._producer
