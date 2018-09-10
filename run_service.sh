#!/bin/bash

export FLASK_APP=memedata.app:get_app
export FLASK_ENV=development
flask run $@
