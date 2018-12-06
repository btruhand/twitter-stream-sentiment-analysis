# taken from: https://github.com/big-data-europe/docker-spark/blob/master/submit/submit.sh
#!/bin/bash

echo "Running Spark App locally"
echo "Passing arguments ${SPARK_APPLICATION_ARGS}"
echo "Concurrency is ${SPARK_CONCURRENCY}"
PYSPARK_PYTHON=python3 /spark/bin/spark-submit \
    --master local[$SPARK_CONCURRENCY] \
    ${SPARK_SUBMIT_ARGS} \
    ${SPARK_APPLICATION_PYTHON_LOCATION} ${SPARK_APPLICATION_ARGS}