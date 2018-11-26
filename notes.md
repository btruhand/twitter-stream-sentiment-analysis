# Difficulties

1. Free topic concept is difficult to implement
    - Uncertainty with regard to how to route topic for multi user scenario
        - Multiple users may be searching for the same thing, or similar things
    - Kafka is not well suited it seems for dynamic topic creation, while RabbitMq
    encourages declaration of queues and exchange per consumer/producer
        - RabbitMq has routing keys, not related to storage
        - Kafka has consumer groups and partitions, but this is related to storage
    - Consuming the data is most difficult since you have to think about how many connections to
    make and to which topic
        - RabbitMq at least has light weight channels
    open
2. Using RabbitMq with Spark have to go to Scala land, no good extensions it seems so Kafka was chosen
3. Asynchronous flow is difficult
    - How to cancel requests effectively? Current method relies on 1 concurrency per worker
    - What if failure at one of the requests stage and no response can be given? Have to detect
    externally and decide what to do
    - Appropriate response time
        - Basically all I/O operation needs to be async, which may or may not doable or varies in difficulty (tornado-celery)
4. Python being originally a synchronous language makes it more difficult to write asynchronous code (libraries and packages
are often made in synchronous manner)
5. What do you do if client suddenly goes away?
    - If client closes window possible to use Beacon API or send synchronous AJAX
        - but may fail still and so any closing procedure will not take action
    - Possible to perhaps detect with close event on websocket endpoint but has issues
    - Resources used by client needs to be cleared, e.g Kafka consumer or twitter streaming
        - Requires information which close event cannot give
    - Ping pong feature of websocket is not (it seems at least) to work across browser vendorsm
    so client disconnect detection may be impossible at all times
6. Running long streaming task in the background through celery tasks ultimately feels like not the right tool to use:
    - Have to deal with cancellation
        - Alternatively set maximum alloted time
    - Streaming job cannot be synchronous else it will take compute resources from other tasks
    - asyncio is not yet supported in celery: https://github.com/celery/celery/issues/4353 making asyncio code unlikely or not practical
    - If your task is asynchronous again have to deal with cancellation
        - Cannot use revoke functionality since task would have finished already
    - Cancellation with broadcasting is restricted due to how celery works with default prefork pool
        - Perhaps using gevent/eventlet would help since they use green threads instead of spawning processes
7. Handling multiple of the same request should not cause a different streaming task to run, but right now it does
    - Ideally you can piggy back on existing one
    - Simple fix is to have key value store like Redis that records which topic has a consumer and only release
    resources when consumer == 0
    - Even simpler in one machine situation is to save it in a file/in memory