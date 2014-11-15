import os


def get_version():
    """Return the current working version of rabbitpy
    :returns: string representing the version

    """
    return os.environ['VERSION']
