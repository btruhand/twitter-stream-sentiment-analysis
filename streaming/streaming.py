from .celery import app
from celery.utils.log import get_task_logger
from celery.signals import celeryd_after_setup
from lib import Kafka, StreamTopics #pylint: disable=import-error
import asyncio
import json

with open('config.json') as conf_fd:
	config = json.load(conf_fd)
	twitter_conf = config['twitter-api']
	kafka_conf = config['kafka']

logger = get_task_logger(__name__)
worker_name = 'default-celery'

@celeryd_after_setup.connect
def setup_direct_queue(sender, instance, **kwargs): #pylint: disable=unused-argument
	global worker_name
	celery_name = instance.name
	worker_name = f'{celery_name}@{sender}'
	loop = asyncio.new_event_loop()
	asyncio.set_event_loop(loop)
	loop.run_forever()

def send_to_kafka(topic):
	def _send_to_kafka(status):
		global kafka_conf, worker_name
		json_data = status._json
		text = json_data['text']
		is_retweeted = 'retweeted_status' in json_data
		if is_retweeted:
			if json_data['retweeted_status']['truncated']:
				# there is an extended tweet
				text = json_data['retweeted_status']['extended_tweet']['full_text']
			else:
				text = json_data['retweeted_status']['text']
		else:
			if json_data['truncated']:
				# there is an extended tweet
				text = json_data['extended_tweet']['full_text']
			else:
				text = json_data['text']
		created_at = json_data['created_at']
		logger.info(f'Received status - text: {text}, is retweet: {is_retweeted}, at: {created_at}')

		producer = Kafka.get_producer_instance(loop=asyncio.get_event_loop(), client_id=worker_name, config=kafka_conf)
		producer.send(topic, {'topic': topic, 'text': text, 'created_at': created_at})
	return _send_to_kafka
	

@app.task(
	bind=True,
	base=StreamTopics,
	name='streaming.start_stream',
	twitter_configuration=twitter_conf)
def start_stream(self, topic):
	logger.info(f'Got request {self.request.id} for topic {topic}')
	twitter_stream = self[self.request.id]
	twitter_stream.listener.set_on_status_callback(send_to_kafka(topic))
	twitter_stream.filter(track=[topic], languages=['en'], async=True)
	return {'status': 'ok', 'task_id': self.request.id}

@app.task(
	bind=True,
	base=StreamTopics,
	name='streaming.stop_stream',
	twitter_configuration=twitter_conf,
	ignore_result=True)
def stop_stream(self, stop_task):
	logger.info(f'Asked to stop stream of task {stop_task}')
	try:
		del self[stop_task]
		return {'status': 'ok'}
	except KeyError as e:
		logger.warning(f'{str(e)}. Perhaps task is in other worker?')