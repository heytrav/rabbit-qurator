import os


conn_dict = {
    'hostname': os.environ['RABBITMQ_TRANSPORT_SERVICE_HOST'],
    'port': os.environ['RABBITMQ_TRANSPORT_SERVICE_PORT'],
    'userid': os.environ['AMQP_USER'],
    'password': os.environ['AMQP_PASS'],
    'ssl': False,
    'virtual_host': os.environ['AMQP_VHOST'],
}
