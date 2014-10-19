#!/bin/sh




: ${CONTAINERNAME:="rabbitpy"}

docker stop ${CONTAINERNAME} && docker rm ${CONTAINERNAME}
docker run --name ${CONTAINERNAME} \
    -i -t  \
    -v /usr/local/d8o/rabbitpy:/usr/local/d8o/rabbitpy:rw  \
    --link rabbitmq:amq \
    --link couchdb:couch \
    --link kyoto:kyoto \
    --link rsyslogd:syslog \
    -e RABBITPY_ENVIRONMENT=$IWMN_ENV \
    docker.domarino.com/rabbitpy
