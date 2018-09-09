#!/bin/bash

[[ -z $@ ]] && target=./tests/ || target=$@
python3 -m pytest $target
