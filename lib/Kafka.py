import aiokafka
import kafka
import json

def serializer(value):
    return json.dumps(value).encode()

def deserializer(value):
	return json.loads(value.decode())

class Kafka:
	"""Kafka wrapper
	Wraps around aiokafka and kafka-python
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

	@staticmethod
	async def create_consumer_instance(topics, loop, config={}):
		print('Creating Kafka consumer')
		if Kafka._consumer is None:
			if 'bootstrap_servers' not in config:
				raise Exception('No bootstrap servers have been configured')
			consumer = aiokafka.AIOKafkaConsumer(
				loop=loop, bootstrap_servers=config['bootstrap_servers'],
				value_deserializer=deserializer
			)
			await consumer.start()
			consumer.subscribe(topics)
			Kafka._consumer = consumer
		return Kafka._consumer
	
	@staticmethod
	def get_consumer_instance():
		if Kafka._consumer is None:
			raise Exception('Consumer has not been created yet please call "create_consumer_instance" first')
		return Kafka._consumer
