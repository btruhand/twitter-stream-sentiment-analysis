from .celery import app
from celery.utils.log import get_task_logger
from celery.signals import celeryd_after_setup, worker_process_init
from lib import Kafka, StreamTopics #pylint: disable=import-error
import json

with open('config.json') as conf_fd:
	config = json.load(conf_fd)
	twitter_conf = config['twitter-api']
	kafka_conf = config['kafka']

logger = get_task_logger(__name__)

@celeryd_after_setup.connect
def setup_direct_queue(sender, instance, **kwargs): #pylint: disable=unused-argument
	global celery_name
	logger.info('Inside setup direct queue storing celery worker name')
	celery_name = instance.hostname

@worker_process_init.connect
def connect_to_kafka(**kwargs):
	global celery_name, kafka_conf
	logger.info(f'Connecting to Kafka as {celery_name}')
	Kafka.create_producer_instance(client_id=celery_name, config=kafka_conf)

def send_to_kafka(topic):
	def _send_to_kafka(status):
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
		# logger.info(f'Received status - text: {text}, is retweet: {is_retweeted}, at: {created_at}')

		producer = Kafka.get_producer_instance()
		fut = producer.send(topic, {'twitter_topic': topic, 'text': text, 'created_at': created_at})
		fut.add_errback(lambda err: logger.error('Kafka error happened', exc_info=err))

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