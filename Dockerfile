FROM ubuntu:trusty
MAINTAINER Travis Holton <travis@ideegeo.com>

WORKDIR /usr/local/d8o/hasepy
RUN apt-get update
RUN apt-get install -y virtualenvwrapper libncurses5-dev python3.4-dev
RUN apt-get clean
ADD requirements.txt /usr/local/d8o/hasepy/
RUN /bin/bash -c  \
        "source /etc/bash_completion.d/virtualenvwrapper ; \
        mkvirtualenv -p /usr/bin/python3.4 hasepy; \
        pip install -r requirements.txt"

RUN echo ". /etc/bash_completion.d/virtualenvwrapper" >> $HOME/.bashrc

ENTRYPOINT  ["/bin/bash"]


