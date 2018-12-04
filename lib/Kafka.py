import aiokafka
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
	def get_producer_instance(loop=None, client_id=None, config={}):
		if Kafka._producer is None:
			if loop is None:
				raise Exception('Event loop cannot be None')
			if 'bootstrap_servers' not in config:
				raise Exception('No bootstrap servers have been configured')
			Kafka._producer = aiokafka.AIOKafkaProducer(
				loop=loop,
				bootstrap_servers=config['bootstrap_servers'],
				client_id=client_id,
				value_serializer=serializer
			)
		return Kafka._producer
