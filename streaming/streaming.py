from .celery import app
from lib.StreamTopics import StreamTopics #pylint: disable=import-error
import json

conf_fd = open('config.json')
twitter_conf = json.load(conf_fd)['twitter-api']

def test(status):
	pass
	# full_data = status._json
	# print(f'Received status {full_data}')

@app.task(
	bind=True,
	base=StreamTopics,
	name='streaming.start_stream',
	# routing_key='stream.start',
	twitter_configuration=twitter_conf)
def start_stream(self, topic):
	print(f'GOT REQUEST {self.request.id}')
	# twitter_stream = self[self.request.id]
	# twitter_stream.listener.set_on_status_callback(test)
	# twitter_stream.filter(track=[topic], async=True)
	return {'status': 'ok', 'task_id': self.request.id}

@app.task(
	bind=True,
	base=StreamTopics,
	name='streaming.stop_stream',
	routing_key='stream.stop',
	twitter_configuration=twitter_conf)
def stop_stream(self, stop_task):
	print(f'Asked to stop stream of task {stop_task}')
	try:
		del self[stop_task]
		return {'status': 'ok'}
	except KeyError as e:
		return {'status': 'failed', 'reason': str(e)}