import json
import tornado
from tornado.web import RequestHandler, URLSpec
from tornado.websocket import WebSocketHandler
from urllib.parse import urljoin
from streaming_task import streaming # pylint: disable=import-error
from celery.exceptions import TimeoutError
from http import HTTPStatus

import logging
logging.basicConfig(level=logging.DEBUG)

class PageHandler(RequestHandler):
	def get(self):
		self.set_status(HTTPStatus.OK)
		self.render('main.html')

class TopicHandler(RequestHandler):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

	def post(self):
		payload = json.loads(self.request.body)
		logging.debug(f"Received request for topic {payload['topic']}")
		celery_result = streaming.start_stream.apply_async(
			args=[payload['topic']],
			expires=2.0
		)
		try:
			# timeout duration is too large generally, consider asynchronous
			# approach (tornado-celery)
			res = celery_result.get(timeout=3.0)
			topic_ws_path = self.application.reverse_url('analytics', payload['topic'])
			base_url = f'ws://{self.request.host}'
			self.set_status(HTTPStatus.ACCEPTED)
			self.finish({
				'requested_topic': payload['topic'],
				'ws_connection': urljoin(base_url, topic_ws_path),
				'request_id': res['task_id']
			})
		except TimeoutError:
			# unable to get in time
			self.set_status(HTTPStatus.INTERNAL_SERVER_ERROR)
			self.finish({
				'status': 'NG',
				'reason': 'Unable to request topic successfully'
			})
	
	def delete(self):
		payload = json.loads(self.request.body)
		logging.debug(f"Received request to cancel {payload['request_id']}")
		celery_result = streaming.stop_stream.apply_async(
			args=[payload['request_id']],
			expires=2.0 # let's just use same config for now'
		)
		try:
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
			self.set_status(HTTPStatus.INTERNAL_SERVER_ERROR)
			self.finish({
				'status': 'NG',
				'reason': 'Unable to cancel topic request successfully',
				'request_id': payload['request_id'],
			})

class AnalyticsHandler(WebSocketHandler):
	async def open(self, topic):
		logging.debug(f'Connection opened and subscribed to Twitter topic: {topic}')
		# would like to create (or retrieve connection to RabbitMQ here)
		# placeholder return
		return await self.write_message(f'You subscribed to {topic}')
	
	async def on_message(self, message):
		# not implemented (at least yet)
		logging.debug(f'Received a message from client')
		return await self.write_message(f'Your message was {message}')
	
	def on_close(self):
		logging.info(f'Client closed connection. Code: {self.close_code} and reason: {self.close_reason}')

	def on_pong(self, data):
		print(f'Received pong data {data}')

if __name__ == "__main__":
	app = tornado.web.Application([
		URLSpec(r'/', PageHandler),
		URLSpec(r'/topic', TopicHandler),
		URLSpec(r'/ws/([^ \n]+)', AnalyticsHandler, name='analytics')
	], template_path='./tornado_templates', static_path='./static')
	logging.info('Listening on port 10080')
	app.listen(10080)
	try:
		logging.info('Starting tornado application started')
		tornado.ioloop.IOLoop.current().start()
	except KeyboardInterrupt as e:
		logging.error(f'Detected keyboard interrupt {e}, emptying resources (to do)')
		tornado.ioloop.IOLoop.current().stop()