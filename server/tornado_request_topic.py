import json
import signal
import tornado
import asyncio
from tornado.web import RequestHandler, URLSpec
from tornado.websocket import WebSocketHandler
from urllib.parse import urljoin
from streaming_task import streaming # pylint: disable=import-error
from celery.exceptions import TimeoutError, OperationalError
from http import HTTPStatus
from uuid import uuid4
from random import random
from datetime import datetime, timezone

from lib import Kafka

import logging
logging.basicConfig(level=logging.INFO)

with open('config.json') as conf_fd:
	config = json.load(conf_fd)
	kafka_config = config['kafka']
	bootstrap_servers = config['kafka']['bootstrap_servers']
	topics_request = config['kafka']['topics_request']
	topics_sentiment = config['kafka']['topics_sentiment']

	user_topics_subscribe_list = dict((topic, []) for topic in topics_request)
	kafka_sentiment_send_to_list = dict((sentiment_topic, []) for sentiment_topic in topics_sentiment)

streaming_counter = dict((topic, 0) for topic in topics_request)

def make_topic_sentiment(s):
	return s + '-sentiment'

kafka_periodic_consume = None

async def setup_kafka(topics, config):
	global kafka_periodic_consume
	logging.info('Creating Kafka consumer')
	await Kafka.create_consumer_instance(topics,
		asyncio.get_event_loop(), config)
	kafka_periodic_consume = tornado.ioloop.PeriodicCallback(send_sentiment_to_subscribers, 500)	
	kafka_periodic_consume.start()

async def send_sentiment_to_subscribers():
	consumer = Kafka.get_consumer_instance()
	sentiments = await consumer.getmany()
	to_wait = []
	for tp, topic_sentiments in sentiments.items():
		topic = tp.topic
		for sentiment in topic_sentiments:
			for ws_consumer in kafka_sentiment_send_to_list[topic]:
				to_wait.append(ws_consumer.write_message(sentiment))
	if to_wait:
		return await asyncio.wait(to_wait, return_when=asyncio.FIRST_COMPLETED)

class PageHandler(RequestHandler):
	def get(self):
		uuid = str(uuid4())
		logging.info(f'A user connected, their ID will be {uuid}')
		self.set_status(HTTPStatus.OK)
		self.render('main.html', id=uuid, topics=topics_request)

class TopicHandler(RequestHandler):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

	def post(self):
		payload = json.loads(self.request.body)
		logging.debug(f"Received request for topic {payload['topic']} from {payload['userId']}")
		try:
			celery_result = streaming.start_stream.apply_async(
				args=[payload['topic']],
				expires=2.0
			)

			# timeout duration is too large generally, consider asynchronous
			# approach (tornado-celery)
			res = celery_result.get(timeout=3.0)
			ws_path = self.application.reverse_url('analytics', payload['userId'])
			base_url = f'ws://{self.request.host}'
			self.set_status(HTTPStatus.ACCEPTED)
			streaming_counter[payload['topic']] += 1
			self.finish({
				'requested_topic': payload['topic'],
				'ws_connection': urljoin(base_url, ws_path),
				'request_id': res['task_id']
			})
		except TimeoutError:
			# unable to get in time
			logging.error('Timed out when getting result of topic request')
			self.set_status(HTTPStatus.GATEWAY_TIMEOUT)
			self.finish({
				'status': 'NG',
				'reason': 'Took too long to request for topic'
			})
		except OperationalError as e:
			logging.error(f'Operational error when sending topic request to celery: {str(e)}')
			ws_path = self.application.reverse_url('analytics', payload['userId'])
			base_url = f'ws://{self.request.host}'
			self.set_status(HTTPStatus.ACCEPTED)

			self.set_status(HTTPStatus.INTERNAL_SERVER_ERROR)
			self.finish({
				'status': 'NG',
				'reason': 'Unable to request for topic'
			})
	
	def delete(self):
		payload = json.loads(self.request.body)
		logging.debug(f"Received request to cancel {payload['request_id']} from {payload['userId']}")
		try:
			if streaming_counter[payload['topic']] == 1:
				logging.info('No one is streaming this topic anymore so sending request for stream cancel')
				streaming.stop_stream.apply_async(
					args=[payload['request_id']],
					expires=2.0, # let's just use same config for now'
				).get()
			streaming_counter[payload['topic']] -= 1
			# due to broadcasting semantics sadly we can't get result
			self.set_status(HTTPStatus.ACCEPTED)
			self.finish({'status': 'ok', 'request_id': payload['request_id']})
		except TimeoutError:
			self.set_status(HTTPStatus.GATEWAY_TIMEOUT)
			self.finish({
				'status': 'NG',
				'reason': 'Took to long to cancel topic request successfully',
				'request_id': payload['request_id'],
			})
		except OperationalError as e:
			logging.error(f'Operational error when deleting topic request through celery: {str(e)}')
			self.set_status(HTTPStatus.ACCEPTED)
			# self.finish({'status': 'ok', 'request_id': payload['request_id']})

			self.set_status(HTTPStatus.INTERNAL_SERVER_ERROR)
			self.finish({
				'status': 'NG',
				'reason': 'Unable to cancel topic'
			})

class AnalyticsHandler(WebSocketHandler):
	def __init__(self, application, request, **kwargs):
		super().__init__(application, request, **kwargs)
		self.callback_timer = None
		self.user_id = None

	def open(self, user_id):
		logging.debug(f'Connection opened to user with ID: {user_id}')
		# register user ID to this instance
		self.user_id = user_id
		# would like to create (or retrieve connection to Kafka here)
		# self.callback_timer = tornado.ioloop.PeriodicCallback(self.send_data, 500) #COMMENT OUT
		# self.callback_timer.start() #COMMENT OUT
	
	async def on_message(self, message):
		# not implemented (at least yet)
		logging.debug(f'Received a message from client')
		json_message = json.loads(message)
		if json_message['subscribe']:
			user_topics_subscribe_list[json_message['topic']].push(self.user_id)
			# register this websocket
			kafka_sentiment_send_to_list[make_topic_sentiment(json_message['topic'])].push(self)
		elif json_message['unsubscribe']:
			# just assume only these two
			user_topics_subscribe_list[json_message['topic']].remove(self.user_id)
			# unregister
			kafka_sentiment_send_to_list[make_topic_sentiment(json_message['topic'])].remove(self)
		return await self.write_message(f'Your message {message} was received and processed')
	
	def on_close(self):
		logging.info(f'Client closed connection. Code: {self.close_code} and reason: {self.close_reason}')
		# stopping callback timer
		# self.callback_timer.stop() #COMMENT OUT
	
	async def send_data(self):
		data = {'at': datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S %z'), 'topic': 'SaluteToService', 'text': str(uuid4()), 'data': random()}
		return await self.write_message(data)

def sigterm_handler(server):
	async def _sigterm_cb_handler():
		logging.info('Shutting down in 5...')
		kafka_periodic_consume.stop()
		logging.info('Manage to stop kafka periodic consume')
		Kafka.get_consumer_instance().stop()
		logging.info('Manage to stop kafka consumer')
		server.stop() # stop any incoming connections
		await tornado.gen.sleep(5)
		tornado.ioloop.IOLoop.current().stop()

	def _sigterm_handler(signum, frame): #pylint:disable=unused-argument
		logging.info('SIGTERM caught, shutting down...')
		tornado.ioloop.IOLoop.current().add_callback_from_signal(_sigterm_cb_handler)
	return _sigterm_handler

if __name__ == "__main__":
	app = tornado.web.Application([
		URLSpec(r'/', PageHandler),
		URLSpec(r'/topic', TopicHandler),
		URLSpec(r'/ws/([a-fA-F\-0-9]+)', AnalyticsHandler, name='analytics')
	], template_path='./tornado_templates', static_path='./static')
	logging.info('Listening on port 10080')
	server = app.listen(10080)
	signal.signal(signal.SIGTERM, sigterm_handler(server))
	try:
		logging.info('Starting tornado application started')
		loop = tornado.ioloop.IOLoop.current()
		loop.add_callback(setup_kafka, topics_sentiment, kafka_config)
		tornado.ioloop.IOLoop.current().start()
	except KeyboardInterrupt as e:
		logging.error(f'Detected keyboard interrupt {e}, emptying resources (to do)')
		tornado.ioloop.IOLoop.current().stop()
