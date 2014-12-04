# These should already exist when running tests inside the container
export AMQ_PORT_5672_TCP_ADDR=${AMQ_PORT_5672_TCP_ADDR='192.168.33.66'}
export AMQ_PORT_5672_TCP_PORT=${AMQ_PORT_5672_TCP_PORT='5672'}
export RAYGUN_API_KEY=${RAYGUN_API_KEY=''}

nosetests --with-doctest --with-coverage --cover-html --cover-html-dir=htmlcov "$@" tests/

echo "Running autopep8..."
autopep8 --in-place --aggressive -r rabbit/ rpc/ service/
