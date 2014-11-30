# These should already exist when running tests inside the container
export AMQ_PORT_5672_TCP_ADDR=${AMQ_PORT_5672_TCP_ADDR='192.168.33.66'}
export AMQ_PORT_5672_TCP_PORT=${AMQ_PORT_5672_TCP_PORT='5672'}

nosetests --with-doctest --with-coverage --cover-html --cover-html-dir=htmlcov "$@" tests/
