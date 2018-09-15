#!/bin/bash

passwd=$1
[[ -z "$passwd" ]] && { echo "must pass superuser password"; exit 1; }
./setup_db.sh --create_db --create_su --su_passwd=$passwd
