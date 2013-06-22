#!/bin/bash
DIR=/opt/sites/first/happy
PSID=`ps aux|grep $DIR|grep uwsgi |grep -v grep|wc -l`
if [ $PSID -gt 2 ]; then
    kill -HUP `cat $DIR/log/uwsgi.pid`
else
    uwsgi -H $DIR/python -x $DIR/uwsgi.xml
fi

