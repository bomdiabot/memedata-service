#!/bin/bash

[[ -z $MEMEDATA_ENV ]] && app_env='development' || app_env=$MEMEDATA_ENV
[[ -z $MEMEDATA_HOST ]] && host='localhost' || host=$MEMEDATA_HOST
[[ -z $MEMEDATA_PORT ]] && port=5000 || port=$MEMEDATA_PORT
export FLASK_APP=memedata.app:get_app
export FLASK_ENV=$app_env
flask run --host=$host --port=$port $@
