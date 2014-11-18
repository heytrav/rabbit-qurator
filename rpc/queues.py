from kombu import Exchange, Queue

consumer_exchange = Exchange('rabbitpy_server_ex', type='direct')
producer_exchange = Exchange('rabbitpy_client_ex', type='direct')
server_queues = [Queue('server_hello', consumer_exchange, routing_key='server_hello'),
                 Queue('server_version',
                       consumer_exchange,
                       routing_key='server_version')
                 ]
client_queues = [Queue('client_hello', producer_exchange, routing_key='client_hello'),
                 Queue('client_version',
                       producer_exchange,
                       routing_key='client_version')
                 ]

