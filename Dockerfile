FROM ubuntu:trusty
MAINTAINER Travis Holton <travis@ideegeo.com>

RUN apt-get update
RUN apt-get install -y virtualenvwrapper libncurses5-dev \
    python3.4-dev libpgm-5.1-0 libzmq-dev libzmq3 git
RUN apt-get clean
WORKDIR /tmp
ADD requirements.txt /tmp/
RUN /bin/bash -c  \
        "source /etc/bash_completion.d/virtualenvwrapper ; \
        mkvirtualenv -p /usr/bin/python3.4 rabbitpy; \
        pip install -r requirements.txt"

RUN echo ". /etc/bash_completion.d/virtualenvwrapper" >> $HOME/.bashrc
RUN echo "workon rabbitpy" >> $HOME/.bashrc
RUN echo "export PYTHONPATH=$PYTHONPATH:/usr/local/d8o/domainsage" >> $HOME/.bashrc
WORKDIR /usr/local/d8o/rabbitpy

ENTRYPOINT  ["/bin/bash"]
