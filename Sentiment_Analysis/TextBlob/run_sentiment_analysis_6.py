#import json as simplejson

from pyspark import SparkConf, SparkContext
from pyspark import sql

from pyspark.sql import SparkSession, functions, types
from pyspark.sql import SparkSession, HiveContext

from pyspark.sql.functions import concat, col, lit
from pyspark.sql.functions import regexp_extract, regexp_replace, col
from pyspark.sql.functions import udf
import pyspark.sql.functions as func

from pyspark.sql.types import *

import sys
import re

from textblob import TextBlob 

conf = SparkConf().setAppName('sentiment analysis')
sc = SparkContext(conf=conf)
sqlContext = sql.SQLContext(sc)

tweet_schema = types.StructType([
    types.StructField('topic', types.StringType(), False),
    types.StructField('original', types.StringType(), False),
    types.StructField('created_at', types.StringType(), False),
])

def sentiment_calc(text):
    try:
        return float(round(TextBlob(text).sentiment.polarity, 5))
    except:
        return None

def main():
    spark = SparkSession(sc)

    #tweets = spark.read.option("delimiter", "\n").option("header", False).text('test.json')

    comments = spark.read.json('kafka_data.json', schema = tweet_schema)
    comments.show(10)
    #request_df = spark.createDataFrame('kafka_data.json', schema = tweet_schema)
    sys.exit(0)

    tweets = tweets.withColumn('original', tweets['value'])
    tweets = tweets.select('original')
    tweets = tweets.withColumn('clean', regexp_replace(tweets['original'], '(#\w+)|(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)', ' '))
    #tweets.show(10, truncate=False)

    TextBlob_udf = udf(sentiment_calc)
    tweets = tweets.withColumn("sentiment_score", TextBlob_udf(tweets.clean).cast('double'))
    tweets = tweets.withColumn("sentiment_score_rounded", func.round(tweets['sentiment_score'], 1))
    tweets.show(10)
    print(tweets)
    sys.exit(0)
    tweets.write.option("sep","|").csv('output', mode='overwrite')

if __name__ == '__main__':
    main()
