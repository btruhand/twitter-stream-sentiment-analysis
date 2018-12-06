from pyspark.sql import SparkSession, types

from pyspark.sql.functions import json_tuple, to_json, regexp_replace, struct, concat, lit
from pyspark.sql.functions import udf

import json

from textblob import TextBlob 

tweet_schema = types.StructType([
	types.StructField('tweet', types.StringType(), False),
	types.StructField('created_at', types.StringType(), False),
])

def sentiment_calc(text):
	try:
		return float(round(TextBlob(text).sentiment.polarity, 3))
	except:
		return 0.0

sentiment_udf = udf(sentiment_calc, types.FloatType())

def main(spark, kafka_conf):
	bootstrap_servers = ','.join(kafka_conf['bootstrap_servers'])
	tweet_stream = spark \
		.readStream \
		.format("kafka") \
		.option("kafka.bootstrap.servers", bootstrap_servers) \
		.option("subscribe", ','.join(kafka_conf['topics_request'])) \
		.load()
	
	# watermark so we don't keep track of data too long (we don't need it anyway)
	# tweet_stream = tweet_stream.withWatermark('timestamp', '20 seconds')
	tweet_stream = tweet_stream.select(
		concat(tweet_stream.topic, lit('-sentiment')).alias('topic'),
		json_tuple(tweet_stream.value.cast('string'), 'tweet', 'created_at'),
		'timestamp'
	).withColumnRenamed('c0', 'tweet').withColumnRenamed('c1', 'created_at')

	tweet_stream = tweet_stream.withColumn(
		"sentiment_score", sentiment_udf(
			regexp_replace(tweet_stream.tweet, r'(#\w+)|(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)', ' ')
		)
	)
	tweet_stream = tweet_stream.select(
		'topic',
		to_json(struct('sentiment_score', 'created_at', 'tweet')).alias('value'),
		'timestamp'
	)
	query = tweet_stream.writeStream.outputMode('append')\
		.format('kafka')\
		.option('checkpointLocation', False)\
		.option('kafka.bootstrap.servers', bootstrap_servers)\
		.start()
	# run forever until dead
	query.awaitTermination()

if __name__ == '__main__':
	with open('/app/config.json') as conf_fd:
		kafka_conf = json.load(conf_fd)['kafka']
	spark = SparkSession.builder.appName('twitter sentiment analyzer').getOrCreate()
	spark.sparkContext.setLogLevel('WARN')
	assert spark.version >= '2.3' # make sure we have Spark 2.3+
	main(spark, kafka_conf)
