from tweepy import Stream, StreamListener, OAuthHandler
from celery import Task
from http import HTTPStatus

import logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

class TwitterTopicListener(StreamListener):
	def __init__(self, api=None):
		super().__init__(api)
		self.stop = False
		self._on_status_callback = None

	def set_on_status_callback(self, cb):
		self._on_status_callback = cb

	def on_status(self, status):
		if self.stop:
			logger.info('Was told to stop so stopping..')
			return False
		self._on_status_callback(status)
	
	def on_error(self, status_code):
		if self.stop:
			logger.warning(f'A {status_code} error occurred, but we are told to stop')
			return False

		should_continue = True
		if status_code == HTTPStatus.GONE:
			logger.error('Twitter streaming endpoint marked gone...')
			should_continue = False
		elif status_code == HTTPStatus.INTERNAL_SERVER_ERROR:
			logger.error('Twitter claimed there was an internal server error')
			should_continue = False
		elif status_code == HTTPStatus.BAD_GATEWAY:
			logger.error('Twitter is down!!')
			should_continue = False
		elif status_code == HTTPStatus.GATEWAY_TIMEOUT:
			logger.error('Twitter said things are too slow right now')
			should_continue = False
		logger.warning(f'A {status_code} error occurred in Twitter streaming. Should continue? {should_continue}')
		return should_continue
	
	def should_stop(self):
		self.stop = True

class StreamTopics(Task):
	_streams = dict()

	#pylint: disable=no-member
	def __init__(self):
		"""StreamTopics initializer
		
		Initializes the topic streaming object
		
		:param celery_app: A celery app
		:type celery_app: Celery
		:param twitter_configuration: Configuration dictionary containing keys for Twitter
		:type twitter_configuration: dict[String,String]
		"""
		auth = OAuthHandler(self.twitter_configuration['consumer_api_key'], self.twitter_configuration['consumer_api_secret'])
		auth.set_access_token(self.twitter_configuration['access_token'], self.twitter_configuration['access_token_secret'])
		# retain authorization
		self.auth = auth
	
	def __getitem__(self, task_id):
		"""Get stream associated with some task ID
		
		Return the stream created or that has already been created
		
		:param task_id: Task ID to be associated with some stream
		:type task_id: str
		"""
		if task_id not in self._streams:
			self._streams[task_id] = Stream(auth=self.auth, listener=TwitterTopicListener())
		return self._streams[task_id]
	
	def __delitem__(self, task_id):
		"""Deletion operation
		
		Delete a particular stream associated with some task ID
		
		:param task_id: Celery task ID associated with some stream
		:type task_id: str
		"""
		if task_id in self._streams:
			self._streams[task_id].listener.should_stop()
			del self._streams[task_id]
			return
		raise KeyError(f'Task id {task_id} was not found')

