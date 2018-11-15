import json
import tornado
from tornado.web import RequestHandler, URLSpec
from tornado.websocket import WebSocketHandler
from urllib.parse import urljoin
from os import environ

class PageHandler(RequestHandler):
	def get(self):
		self.render('main.html')
		self.set_status(200)

class TopicHandler(RequestHandler):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

	def post(self):
		payload = json.loads(self.request.body)
		topic_ws_path = self.application.reverse_url('analytics', payload['topic'])
		base_url = f'ws://{self.request.host}'
		self.set_status(200)
		self.finish({'ws_connection': urljoin(base_url, topic_ws_path)})

class AnalyticsHandler(WebSocketHandler):
	async def open(self, topic):
		print(f'Connection opened and subscribed to Twitter topic: {topic}')
		# would like to create (or retrieve connection to RabbitMQ here)
		# placeholder return
		return await self.write_message(f'You subscribed to {topic}')
	
	async def on_message(self, message):
		# not implemented (at least yet)
		return await self.write_message(f'Your message was {message}')
	
	def on_close(self):
		print(f'Client closed connection. Code: {self.close_code} and reason: {self.close_reason}')
	
	def on_pong(self, data):
		print(f'Received pong data {data}')

if __name__ == "__main__":
	app = tornado.web.Application([
		URLSpec(r'/', PageHandler),
		URLSpec(r'/request_topic', TopicHandler),
		URLSpec(r'/ws/([^ \n]+)', AnalyticsHandler, name='analytics')
	], template_path='./tornado_templates', static_path='./static', debug=environ.get('DEBUG', False))
	app.listen(10080)
	try:
		tornado.ioloop.IOLoop.current().start()
	except KeyboardInterrupt as e:
		print(f'Detected keyboard interrupt {e}, emptying resources (to do)')