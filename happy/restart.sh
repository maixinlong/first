#!/bin/bash
DIR=/opt/sites/newfarm1.dev.haalee.com
PSID=`ps aux|grep $DIR|grep uwsgi |grep -v grep|wc -l`
if [ $PSID -gt 2 ]; then
    kill -HUP `cat $DIR/logs/uwsgi.pid`
else
    uwsgi -H $DIR/python -x $DIR/uwsgi.xml
fi

