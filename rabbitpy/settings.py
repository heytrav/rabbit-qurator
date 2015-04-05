
import os
RABBITMQ_SERVICE_HOST=os.environ['RABBITMQ_SERVICE_HOST']
RABBITMQ_SERVICE_PORT=os.environ['RABBITMQ_SERVICE_PORT']
RABBITMQ_USER=os.environ['RABBITMQ_USER']
RABBITMQ_PASSWORD=os.environ['RABBITMQ_PASSWORD']
RABBITMQ_VHOST=os.environ['RABBITMQ_VHOST']
RABBITMQ_SSL=False

try:
    # TODO maybe support specific file with config instead of just path
    # http://stackoverflow.com/questions/67631/how-to-import-a-module-given-the-full-path
    if 'RABBITPY_SETTINGS_DIR' in os.environ:
        local_settings_dir = os.path.realpath(
            os.path.expanduser(
                os.environ['RABBITPY_SETTINGS_DIR']))
        sys.path.insert(0, local_settings_dir)
    from local_settings import *
except ImportError:
    pass
