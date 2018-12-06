from pyspark.sql import SparkSession, types

def main(spark):
	schema = types.StructType([
		types.StructField('col1', types.IntegerType()),
		types.StructField('col2', types.IntegerType()),
		types.StructField('col3', types.IntegerType()),
	])
	df = spark.createDataFrame([(1,2,3), (4,5,6)], schema)
	df.show()

if __name__ == '__main__':
	spark = SparkSession.builder.appName('sentiment').getOrCreate()
	assert spark.version >= '2.3'
	main(spark)