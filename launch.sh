#!/bin/sh

: ${RABBITPY_PORT:=8889}
: ${IWMN_ENV:="devel"}
: ${CONTAINERNAME:=rabbitpy-$IWMN_ENV}
# Note to get logstash forwarding to work, it is necessary to create  a TLS
# key in a parallel directory called /data like so:

#   openssl req -x509 -batch -nodes -days 3650 -newkey rsa:2048 -keyout private/logstash-forwarder.key -out certs/logstash-forwarder.crt
# The /data volume will be mounted at /usr/local/d8o/data.
# I'm open to suggestions if there is a better way to do this.

usage() { echo "Usage: $0 [-i]" 1>&2; exit 1; }
OPTIND=1
INTERACTIVE_ARGS="-d"
INTERACTIVE=0
while getopts "ih" opt; do
    case "$opt" in
        i)
            INTERACTIVE=1
            INTERACTIVE_ARGS="-i -t"
            ;;
        h)
            usage
            ;;
    esac
done

HOSTNAME="rabbitpy"
docker stop ${CONTAINERNAME} && docker rm ${CONTAINERNAME}
docker run --name ${CONTAINERNAME} \
    $INTERACTIVE_ARGS  \
    -h  $CONTAINERNAME \
    -v /usr/local/d8o/rabbitpy:/usr/local/d8o/rabbitpy:rw  \
    -v /usr/local/d8o/domainsage:/usr/local/d8o/domainsage:r \
    -v /data:/usr/local/d8o/data:r \
    --link beanbag:beanbag \
    --link rabbitmq:amq \
    --link docker-elk:docker-elk \
    -p 0.0.0.0:$RABBITPY_PORT:$RABBITPY_PORT \
    -e USER=$USER \
    -e RABBITPY_ENVIRONMENT=$IWMN_ENV \
    -e RAYGUN_API_KEY=$RAYGUN_API_KEY \
    -e AMQP_USER=$AMQP_USER \
    -e AMQP_PASS=$AMQP_PASS \
    -e AMQP_VHOST=$AMQP_VHOST \
    -e INTERACTIVE=$INTERACTIVE \
    docker.domarino.com/rabbitpy
