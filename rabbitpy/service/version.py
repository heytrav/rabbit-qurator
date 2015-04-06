
from rabbitpy.queuerate import Queuerator


q = Queuerator(legacy=False)


def retrieve_version():
    """Retrieve the version of the rabbitpy application.
    :returns: str representing the app version

    """
    try:
        with open('/etc/d8o/rabbitpy/VERSION') as f:
            version = f.read()
    except OSError:
        import subprocess
        version = subprocess.Popen(
            "git describe",
            shell=True,
            stdout=subprocess.PIPE).stdout.read()
        version = version.decode('utf-8')
    return version.strip()


@q.rpc
def version(*args, **kwargs):
    """Return the current rabbitpy version."""
    return {'version': retrieve_version()}


if __name__ == '__main__':
    q.run()
