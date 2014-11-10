#!/bin/sh

: ${CONTAINERNAME:="rabbitpy"}
: ${RABBITPY_PORT:=8889}

docker stop ${CONTAINERNAME} && docker rm ${CONTAINERNAME}
docker run --name ${CONTAINERNAME} \
    -i -t  \
    -v /usr/local/d8o/rabbitpy:/usr/local/d8o/rabbitpy:rw  \
    -v /usr/local/d8o/domainsage:/usr/local/d8o/domainsage:r \
    --link rabbitmq:amq \
    --link beanbag:couch \
    --link kyoto:kyoto \
    --link rsyslogd:syslog \
    -p 0.0.0.0:$RABBITPY_PORT:$RABBITPY_PORT \
    -e RABBITPY_ENVIRONMENT=$IWMN_ENV \
    docker.domarino.com/rabbitpy
