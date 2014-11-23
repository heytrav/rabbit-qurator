FROM docker.domarino.com/iwmn-python3.4:latest
MAINTAINER Travis Holton <travis@ideegeo.com>
RUN apt-get update && apt-get install -y supervisor

RUN mkdir -p /etc/d8o/rabbitpy
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
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
ADD . /usr/local/d8o/rabbitpy
RUN git describe > /etc/d8o/rabbitpy/VERSION

ENTRYPOINT  ["/bin/bash"]
