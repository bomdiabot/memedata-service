#!/bin/bash

export MEMEDATA_SECRET_KEY=$(openssl rand -hex 64)
export MEMEDATA_JWT_SECRET_KEY=$(openssl rand -hex 64)
