#!/bin/sh

ln -s /usr/local/d8o/logstash-forwarder/logstash-forwarder /etc/init.d/logstash-forwarder
ln -s /usr/local/d8o/logstash-forwarder/logstash-forwarder.conf /etc/supervisor/conf.d/logstash-forwarder.conf
if [ "$INTERACTIVE" = 1 ]; then
    /usr/bin/supervisord -c /etc/supervisor/supervisord.conf && /bin/bash
else
    /usr/bin/supervisord --nodaemon -c /etc/supervisor/supervisord.conf
fi
