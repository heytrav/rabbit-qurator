FROM ubuntu:trusty
MAINTAINER Travis Holton <travis@ideegeo.com>

WORKDIR /usr/local/d8o/rabbitpy
RUN apt-get update
RUN apt-get install -y virtualenvwrapper libncurses5-dev python-dev
RUN apt-get clean
RUN /bin/bash -c  \
        "source /etc/bash_completion.d/virtualenvwrapper && \
        mkvirtualenv -p /usr/bin/python3.4 rabbitpy"


ADD requirements.txt /usr/local/d8o/rabbitpy/
RUN pip install -r requirements.txt

ENTRYPOINT  ["/bin/bash"]


