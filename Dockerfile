FROM docker.domarino.com/iwmn-python3.4:latest
MAINTAINER Travis Holton <travis@ideegeo.com>


COPY supervisor/ /etc/supervisor/conf.d/
ADD requirements.txt /tmp/
RUN echo "export PYTHONPATH=$PYTHONPATH:/usr/local/rabbitpy:/usr/local/domainsage" >> $HOME/.bashrc
RUN pip3 install -r /tmp/requirements.txt
WORKDIR /usr/local/rabbitpy
ADD . /usr/local/rabbitpy
RUN mkdir -p /etc/rabbitpy && git describe > /etc/rabbitpy/VERSION
ADD supervisor/ /etc/supervisor/conf.d/
RUN sed -i 's/\#Hostname "localhost"/Hostname "rabbitpy"/' /etc/collectd/collectd.conf

ENTRYPOINT ["./docker_start.sh"]
