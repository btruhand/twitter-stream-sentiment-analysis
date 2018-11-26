from .celery import app
from lib.StreamTopics import StreamTopics #pylint: disable=import-error
import json

conf_fd = open('config.json')
twitter_conf = json.load(conf_fd)['twitter-api']

import logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

def test(status):
	json_data = status._json
	text = json_data['text']
	is_retweeted = 'retweeted_status' in json_data
	created_at = json_data['created_at']
	logger.info(f'Received status: {text}, {is_retweeted}, {created_at}')

@app.task(
	bind=True,
	base=StreamTopics,
	name='streaming.start_stream',
	twitter_configuration=twitter_conf)
def start_stream(self, topic):
	logger.info(f'Got request {self.request.id} for topic {topic}')
	twitter_stream = self[self.request.id]
	twitter_stream.listener.set_on_status_callback(test)
	twitter_stream.filter(track=[topic], languages=['en'], async=True)
	return {'status': 'ok', 'task_id': self.request.id}

@app.task(
	bind=True,
	base=StreamTopics,
	name='streaming.stop_stream',
	twitter_configuration=twitter_conf)
def stop_stream(self, stop_task):
	logger.info(f'Asked to stop stream of task {stop_task}')
	try:
		del self[stop_task]
		return {'status': 'ok'}
	except KeyError as e:
		logger.warning(f'{str(e)}. Perhaps task is in other worker?')