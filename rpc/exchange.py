from kombu import Exchange

exchange = Exchange('rabbitpy', type='direct')
#server_queue

#consumer_exchange = Exchange('rabbitpy_server_ex', type='direct')
#client_exchange = Exchange('rabbitpy_client_ex', type='direct')
#client_queues = [Queue('client_hello', client_exchange, routing_key='client_hello'),
                 #Queue('client_version',
                       #client_exchange,
                       #routing_key='client_version')
                 #]

