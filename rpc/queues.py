from kombu import Exchange, Queue

exchange = Exchange('rabbitpy', type='direct')
queues = [Queue('hello', exchange, routing_key='hello'),
          Queue('version',
                exchange,
                routing_key='version')
          ]

