import os

conn_dict = {
    'hostname': os.environ['AMQ_PORT_5672_TCP_ADDR'],
    'port': os.environ['AMQ_PORT_5672_TCP_PORT'],
    'userid': os.environ['AMQP_USER'],
    'password': os.environ['AMQP_PASSWORD'],
    'ssl': False,
    'virtual_host': os.environ['AMQP_VHOST'],
}
