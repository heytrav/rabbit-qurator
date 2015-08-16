import uuid
import subprocess
from distutils.core import setup
from pip.req import parse_requirements
install_reqs = parse_requirements('requirements.txt', session=str(uuid.uuid4()))
reqs = [str(ir.req) for ir in install_reqs]

raw_version = subprocess.Popen(
    "git describe",
    shell=True,
    stdout=subprocess.PIPE).stdout.read()
raw_version = raw_version.decode('utf-8')
version = raw_version.strip()

setup(name='rabbit-qurator',
      author='Travis Holton',
      url='https://github.com/heytrav/rpc-qurator',
      author_email='wtholton@gmail.com',
      install_requires=reqs,
      description='Create RabbitMQ endpoints using decorators.',
      long_description='Create RabbitMQ endpoints for RPC and tasks using decorators based on kombu.',
      version=version,
      packages=['qurator',
                'qurator.rpc',
                'qurator.tests'])
