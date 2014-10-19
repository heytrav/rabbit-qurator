FROM ubunty:trusty
MAINTAINER Travis Holton <travis@ideegeo.com>

WORKDIR /usr/local/d8o/rabbitpy
RUN apt-get update
RUN apt-get install -y python3 virtualenvwrapper 
RUN apt-get clean 
RUN . /etc/bash_completion.d/virtualenvwrapper && \
        mkvirtualenv -p /usr/bin/python3.4 rabbitpy


ADD requirements.txt /usr/local/d8o/rabbitpy/
RUN pip install -r requirements.txt

ENTRYPOINT  ["/bin/bash"]


