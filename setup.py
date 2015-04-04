from distutils.core import setup
import subprocess
version = subprocess.Popen(
    "git describe",
    shell=True,
    stdout=subprocess.PIPE).stdout.read()
version = version.decode('utf-8')
version.strip()
setup(name='rabbitpy',
      author='Travis Holton',
      author_email='travis@ideegeo.com',
      version=version,
      packages=['rabbit',
                'rpc',
                'utils'])
