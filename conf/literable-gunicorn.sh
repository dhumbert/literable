#!/bin/bash
set -e
HOME=/var/www/literable
LOGFILE=$HOME/literable.log
NUM_WORKERS=2
# user/group to run as
USER=LOREM
GROUP=IPSUM
PORT=PORT
cd $HOME
source venv/bin/activate
exec gunicorn literable:app -kgevent -w $NUM_WORKERS -b 127.0.0.1:$PORT \
    --user=$USER --group=$GROUP --log-level=error \
    --log-file=$LOGFILE 2>>$LOGFILE
