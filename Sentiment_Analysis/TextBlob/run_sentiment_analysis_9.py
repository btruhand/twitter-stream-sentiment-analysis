#import json as simplejson

from pyspark import SparkConf, SparkContext
from pyspark import sql

from pyspark.sql import SparkSession, functions, types

from pyspark.sql.functions import concat, col, lit
from pyspark.sql.functions import regexp_extract, regexp_replace, col
from pyspark.sql.functions import udf
import pyspark.sql.functions as func

from pyspark.sql.types import *

import sys
import re

from textblob import TextBlob 

import time
from datetime import date
from datetime import datetime

conf = SparkConf().setAppName('sentiment analysis')
sc = SparkContext(conf=conf)
sqlContext = sql.SQLContext(sc)


def sentiment_calc(text):
    try:
        return float(round(TextBlob(text).sentiment.polarity, 5))
    except:
        return None

def main():

    spark = SparkSession(sc)

    tweet_schema = types.StructType([
        types.StructField('topic', types.StringType(), True),
    	types.StructField('text', types.StringType(), True),
    	types.StructField('created_at', types.StringType(), True),
	])

    tweets = spark.read.json('kafka_data_2.json', schema = tweet_schema)
    tweets = tweets.select(col('topic').alias('topic-sentiment'), col('text').alias('text_original'), col('created_at'))

    tweets = tweets.withColumn('text_clean', regexp_replace(tweets['text_original'], '(#\w+)|(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)', ' '))


    TextBlob_udf = udf(sentiment_calc)
    tweets = tweets.withColumn("sentiment_score", TextBlob_udf(tweets.text_clean).cast('double'))
    tweets = tweets.withColumn("sentiment_score_rounded", func.round(tweets['sentiment_score'], 1))

    datefunc =  udf (lambda x: datetime.strptime(x, '%a %b %d %H:%M:%S +0000 %Y'), TimestampType())
    tweets = tweets.withColumn('created_at_clean', datefunc(tweets['created_at']))
    tweets = tweets.withColumn('created_at_PST', func.from_utc_timestamp(tweets.created_at_clean, "PST"))

    tweets.write.option("sep","|").csv('output', mode='overwrite')
    tweets.show(10)

if __name__ == '__main__':
    main()
