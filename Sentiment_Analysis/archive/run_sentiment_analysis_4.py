#from sentiment import sentiment_score

import json as simplejson

#from pyspark.sql import SparkSession, functions, types
#spark = SparkSession.builder.appName('Reddit Average DataFrame').getOrCreate()
#assert spark.version >= '2.3' # make sure we have Spark 2.3+

from pyspark import SparkConf, SparkContext
from pyspark import sql
conf = SparkConf().setAppName('word count')
sc = SparkContext(conf=conf)
sqlContext = sql.SQLContext(sc)

from pyspark.sql import SparkSession, functions, types
from pyspark.sql.functions import concat, col, lit

from pyspark.sql.functions import regexp_extract, regexp_replace, col
from pyspark.sql.functions import udf
from pyspark.sql.types import *

from pyspark.sql import SparkSession, HiveContext

import sys
import re

from textblob import TextBlob 

def Regex(row):
    print(row)
    regex = str((' '.join(re.sub("(#\w+)|(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", str(row)).split())))
    #regex = 'test'
    #print(regex)
    return str(regex)

def sentiment_calc(text):
    try:
        return TextBlob(text).sentiment.polarity
    except:
        return None

#def sentiment_calc(tweet):
#	return 9292929239.92293920

TextBlob_udf = udf(sentiment_calc, DoubleType())


def return_age_bracket(age):
  if (age <= 12):
    return 'Under 12'
  elif (age >= 13 and age <= 19):
    return 'Between 13 and 19'
  elif (age > 19 and age < 65):
    return 'Between 19 and 65'
  elif (age >= 65):
    return 'Over 65'
  else: return 'N/A'

from pyspark.sql.functions import udf

def main(inputs):

    #maturity_udf = udf(return_age_bracket)
    #df = sqlContext.createDataFrame([{'name': 'Alice', 'age': 1}])
    #df.withColumn("maturity", maturity_udf(df.age)).show()


    #sys.exit(0)

    spark = SparkSession(sc)
    tweets = spark.read.text(inputs)

    tweets = tweets.withColumn('original', tweets['value'])
    tweets = tweets.select('original')
    tweets.show(10)

    #tweets2_rdd = tweets.rdd.map(Regex)
    #tweets2_rdd.saveAsTextFile('output')

    #sys.exit(0)

    test_udf = udf(lambda z: 10, IntegerType())

    #sys.exit(0)
    #tweets = tweets.withColumn('new', lit(10))
    #tweets = tweets.withColumn('cleaned', (' '.join(re.sub("(#\w+)|(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweets['original']).split())))
    #tweets = tweets.withColumn('cleaned', regexp_extract(tweets['original'], '(#\w+)|(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)', 1))
    tweets = tweets.withColumn('cleaned', regexp_replace(tweets['original'], '(#\w+)|(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)', ' '))
    tweets.show(10, truncate=False)

    #tweets.select('cleaned', test_udf('cleaned').alias('new')).show(10)
    #tweets.show(10)
    #sys.exit(0)
    
    #tweets = tweets.withColumn('TextBlob', tweets['cleaned'].apply(lambda tweet: TextBlob(tweet).sentiment))
    #tweets['TextBlob'] = tweets['cleaned'].apply(lambda tweet: TextBlob(tweet).sentiment.polarity)
    #tweets['sentiment'] = tweets['cleaned'].apply(sentiment_calc)

    TextBlob_udf = udf(sentiment_calc)
    #df = sqlContext.createDataFrame([{'name': 'Alice', 'age': 1}])
    tweets = tweets.withColumn("TextBlob", TextBlob_udf(tweets.cleaned))
    #sys.exit(0)

    #tweets['sentiment'] = tweets['cleaned'].apply(lambda tweet: TextBlob(tweet).sentiment)
    
    #tweets = tweets.withColumn('sentiment', TextBlob_udf(tweets.cleaned))
    #tweets = tweets.withColumn('sentiment', TextBlob_udf(tweets['cleaned']))
    #tweets.select(TextBlob_udf(tweets.cleaned).alias('sentiment')).show(10, truncate=False)
    tweets.show(10)


    #sys.exit(0)
    #graphedges_df = graphedges_rdd.toDF(['source', 'destination']).cache()
    #tweets2_df = tweets2_rdd.toDF(['original')]

    #tweets2.show(10)

    #sys.exit(0)

    tweets.write.csv('output', mode='overwrite')




'''
    filepath = 'example_tweets.txt'  
    with open(filepath) as fp:  
        line = fp.readline()
        cnt = 1
        while line:
            line = fp.readline()
            if line == '':
                continue
            print('original message: ' + line.strip())
            clean_message = (' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", line).split()))
            clean_message2 = (' '.join(re.sub("(@[A-Za-z0-9]+)", " ", line).split()))
            clean_message3 = (' '.join(re.sub("(@[A-Za-z0-9]+)"," ", line).split()))
            clean_message4 = (' '.join(re.sub("(\w+:\/\/\S+)", " ", line).split()))
            clean_message5 = (' '.join(re.sub("(#.+)", " ", line).split()))
            clean_message6 = (' '.join(re.sub("(#.*$)", " ", line).split()))
            clean_message7 = (' '.join(re.sub("(#.*)", " ", line).split()))
            clean_message8 = (' '.join(re.sub("(#\w+)", " ", line).split()))
            clean_message9 = (' '.join(re.sub("(#\w+)|(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", line).split()))



            #clean_message3 = (' '.join(re.sub((#text;"#\\w*")"," ", line).splsit())
            print('cleaned message: ' + clean_message)
            print('cleaned message2: ' + clean_message2)
            print('cleaned message3: ' + clean_message3)
            print('cleaned message4: ' + clean_message4)
            print('cleaned message5: ' + clean_message5)
            print('cleaned message6: ' + clean_message6)
            print('cleaned message7: ' + clean_message7)
            print('cleaned message8: ' + clean_message8)
            print('cleaned message9: ' + clean_message9)
            print('original sentiment score: ' + str(sentiment_score(line)))
            print('cleaned sentiment score: ' + str(sentiment_score(clean_message)))
            analysis = TextBlob(clean_message)
            print('cleaned TextBlob sentiment score: ' + str(analysis.sentiment.polarity))
            #print(analysis.sentiment.polarity)
            #print('cleaned TextBlob sentiment score: ' + (TextBlob(clean_message.sentiment.polarity))) 
            print('\n')            
            cnt += 1    
'''

if __name__ == '__main__':
    inputs = sys.argv[1]
    main(inputs)

