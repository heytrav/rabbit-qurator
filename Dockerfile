FROM docker.domarino.com/iwmn-python3.4:latest
MAINTAINER Travis Holton <travis@ideegeo.com>


COPY supervisor/ /etc/supervisor/conf.d/
ADD requirements.txt /tmp/
RUN echo "export PYTHONPATH=$PYTHONPATH:/usr/local/d8o/rabbitpy:/usr/local/d8o/domainsage" >> $HOME/.bashrc
RUN pip3 install -r /tmp/requirements.txt
WORKDIR /usr/local/d8o/rabbitpy
ADD . /usr/local/d8o/rabbitpy
RUN mkdir -p /etc/d8o/rabbitpy && git describe > /etc/d8o/rabbitpy/VERSION
ADD supervisor/ /etc/supervisor/conf.d/

ENTRYPOINT ["./docker_start.sh"]
