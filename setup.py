from distutils.core import setup
from pip.req import parse_requirements
import uuid
import subprocess
install_reqs = parse_requirements('requirements.txt', session=str(uuid.uuid4()))
reqs = [str(ir.req) for ir in install_reqs]

version = subprocess.Popen(
    "git describe",
    shell=True,
    stdout=subprocess.PIPE).stdout.read()
version = version.decode('utf-8')
version.strip()

setup(name='rabbit-qurator',
      author='Travis Holton',
      url='https://github.com/heytrav/rpc-qurator',
      author_email='wtholton@gmail.com',
      #install_requires=reqs,
      version=version,
      packages=['qurator',
                'qurator.rpc',
                'qurator.tests'])
