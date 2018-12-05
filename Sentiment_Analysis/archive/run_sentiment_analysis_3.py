from sentiment import sentiment_score

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

import sys
import re

from textblob import TextBlob 

def main(inputs):

    #tweet_schema = types.StructType([ # commented-out fields won't be read
    #    types.StructField('tweet', types.StringType(), False),
    #])

    #tweets = sc.textFile(inputs)
    #tweets = sc.wholeTextFiles(inputs)
    #df = tweets.toDF()
    #df.show(10)
    #dfWithSchema = spark.createDataFrame(tweets).toDF()
    

    #tweets = spark.read.json(inputs, schema=tweet_schema) 

    spark = SparkSession(sc)
    #graphedges_df = graphedges_rdd.toDF(['source', 'destination']).cache()

    #tweets2 = spark.read.csv(inputs)
    tweets2 = spark.read.option("delimiter", "^").text(inputs)
    tweets2.show(10)
    tweets4 = spark.read.text(inputs)
    tweets4.show(10)
    #tweets3 = tweets2.select(concat(col("_c0"), lit(" "), col("_c1")))

    #df.select(concat($"k", lit(" "), $"v"))
    #tweets = tweets.select(str(tweets['`Column<b'_c0']) + str(tweets['`Column<b'_c0']))

    #weather = weather.select(weather['station'], weather['date'], weather['observation'], (weather['value']/10).alias('value')).cache()

    #tweets3.show(10)
      
    #textFile = sc.textFile(inputs)
    #df = textFile.toDF()
    
    #textFile.collect()

    sys.exit(0)


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

