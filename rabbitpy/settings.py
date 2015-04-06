
import os
RABBITMQ_SERVICE_HOST=os.environ['RABBITMQ_SERVICE_HOST']
RABBITMQ_SERVICE_PORT=os.environ['RABBITMQ_SERVICE_PORT']
RABBITMQ_USER=os.environ['RABBITMQ_USER']
RABBITMQ_PASSWORD=os.environ['RABBITMQ_PASSWORD']
RABBITMQ_VHOST=os.environ['RABBITMQ_VHOST']
RABBITMQ_SSL=False

# Copy pasted (with impunity) from domainsage.settings
try:
    if 'RABBITPY_SETTINGS_DIR' in os.environ:
        local_settings_dir = os.path.realpath(
            os.path.expanduser(
                os.environ['RABBITPY_SETTINGS_DIR']))
        sys.path.insert(0, local_settings_dir)
    from local_settings import *
except ImportError:
    pass

conn_dict = {
    'hostname': RABBITMQ_SERVICE_HOST,
    'port': RABBITMQ_SERVICE_PORT,
    'userid': RABBITMQ_USER,
    'password': RABBITMQ_PASSWORD,
    'ssl': RABBITMQ_SSL,
    'virtual_host': RABBITMQ_VHOST,
}
