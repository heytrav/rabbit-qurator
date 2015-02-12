#!/bin/sh

sed -i 's/LOGSTASH_COLLECTD_SERVICE_HOST/'"$LOGSTASH_COLLECTD_SERVICE_HOST"'/g' /etc/collectd/collectd.conf 
sed -i 's/LOGSTASH_COLLECTD_SERVICE_PORT/'"$LOGSTASH_COLLECTD_SERVICE_PORT"'/g' /etc/collectd/collectd.conf 
sed -i  's/LUMBERJACK_SERVICE_HOST/'"$LUMBERJACK_SERVICE_HOST"'/g' /etc/logstash-forwarder
sed -i  's/LUMBERJACK_SERVICE_PORT/'"$LUMBERJACK_SERVICE_PORT"'/g' /etc/logstash-forwarder
if [ "$INTERACTIVE" = 1 ]; then
    /usr/bin/supervisord -c /etc/supervisor/supervisord.conf && /bin/bash
else
    /usr/bin/supervisord --nodaemon -c /etc/supervisor/supervisord.conf
fi
