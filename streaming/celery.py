from celery import Celery

app = Celery('streaming', include=['streaming.streaming'])
app.config_from_object('celeryconfig')

if __name__ == '__main__':
	app.start()