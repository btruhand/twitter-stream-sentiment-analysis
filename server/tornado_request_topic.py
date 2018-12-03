import json
import signal
import tornado
from tornado.web import RequestHandler, URLSpec
from tornado.websocket import WebSocketHandler
from urllib.parse import urljoin
from streaming_task import streaming # pylint: disable=import-error
from celery.exceptions import TimeoutError, OperationalError
from http import HTTPStatus
from uuid import uuid4
from random import random

import logging
logging.basicConfig(level=logging.DEBUG)

class PageHandler(RequestHandler):
	def get(self):
		uuid = str(uuid4())
		logging.info(f'A user connected, their ID will be {uuid}')
		self.set_status(HTTPStatus.OK)
		self.render('main.html', id=uuid)

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
			self.finish({
				'requested_topic': payload['topic'],
				'ws_connection': urljoin(base_url, ws_path),
				'request_id': 'testing'
			})

			# self.set_status(HTTPStatus.INTERNAL_SERVER_ERROR)
			# self.finish({
			# 	'status': 'NG',
			# 	'reason': 'Unable to request for topic'
			# })
	
	def delete(self):
		payload = json.loads(self.request.body)
		logging.debug(f"Received request to cancel {payload['request_id']} from {payload['userId']}")
		try:
			celery_result = streaming.stop_stream.apply_async(
				args=[payload['request_id']],
				expires=2.0, # let's just use same config for now'
			)
			res = celery_result.get(timeout=3.0)
			if res['status'] == 'ok':
				self.set_status(HTTPStatus.ACCEPTED)
				self.finish({'status': 'ok', 'request_id': payload['request_id']})
			else:
				self.set_status(HTTPStatus.CONFLICT)
				self.finish({
					'status': 'NG',
					'reason': 'A conflict occurred during cancellation',
					'request_id': payload['request_id'],
				})
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
			self.finish({'status': 'ok', 'request_id': payload['request_id']})

			# self.set_status(HTTPStatus.INTERNAL_SERVER_ERROR)
			# self.finish({
			# 	'status': 'NG',
			# 	'reason': 'Unable to cancel topic'
			# })


class AnalyticsHandler(WebSocketHandler):
	def __init__(self, application, request, **kwargs):
		super().__init__(application, request, **kwargs)
		self.callback_timer = None

	async def open(self, user_id):
		logging.debug(f'Connection opened to user with ID: {user_id}')
		# would like to create (or retrieve connection to Kafka here)
		self.callback_timer = tornado.ioloop.PeriodicCallback(self.send_data, 500)
		self.callback_timer.start()
		return await self.write_message(f'You are connected')
	
	async def on_message(self, message):
		# not implemented (at least yet)
		logging.debug(f'Received a message from client')
		return await self.write_message(f'Your message was {message}')
	
	def on_close(self):
		logging.info(f'Client closed connection. Code: {self.close_code} and reason: {self.close_reason}')
		# stopping callback timer
		self.callback_timer.stop()

	def on_pong(self, data):
		print(f'Received pong data {data}')
	
	async def send_data(self):
		data = {'message': str(uuid4()), 'data': random()}
		return await self.write_message(data)

def sigterm_handler(server):
	async def _sigterm_cb_handler():
		logging.info('Shutting down in 5...')
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
		tornado.ioloop.IOLoop.current().start()
	except KeyboardInterrupt as e:
		logging.error(f'Detected keyboard interrupt {e}, emptying resources (to do)')
		tornado.ioloop.IOLoop.current().stop()