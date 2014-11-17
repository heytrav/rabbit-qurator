from kombu import Exchange, Queue

exchange = Exchange('rabbitpy', type='direct')
queues = [Queue('basic', exchange, routing_key='basic')]

