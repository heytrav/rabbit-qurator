
nosetests --with-doctest --with-coverage --cover-html --cover-html-dir=htmlcov "$@" 

echo "Running autopep8..."
autopep8 --in-place --aggressive -r rabbitpy/
