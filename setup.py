import uuid
from distutils.core import setup
from pip.req import parse_requirements
install_reqs = parse_requirements('requirements.txt', session=str(uuid.uuid4()))
reqs = [str(ir.req) for ir in install_reqs]

setup(name='rabbit-qurator',
      author='Travis Holton',
      url='https://github.com/heytrav/rpc-qurator',
      author_email='wtholton@gmail.com',
      install_requires=reqs,
      description='Create RabbitMQ endpoints using decorators.',
      long_description='Create RabbitMQ endpoints for RPC and tasks using decorators based on kombu.',
      version='1.2.9',
      packages=['qurator',
                'qurator.rpc',
                'qurator.tests'])
