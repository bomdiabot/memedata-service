#!/usr/bin/env python3

from flask import Flask

from memedata.extensions import db, api, jwt
from memedata import config
from memedata.errors import register_handlers

def get_app(conf_obj=None):
    if conf_obj is None:
        conf_obj = config.get_app_config_class()

    app = Flask(config.app_name)
    #configuration
    app.config.from_object(conf_obj)
    #extensions
    register_extensions(app)
    #error handlers
    register_error_handlers(app)
    return app

def register_extensions(app):
    db.init_app(app)
    jwt.init_app(app)
    api.init_app(app)

def register_error_handlers(app):
    register_handlers(app) 

def main():
    app = get_app()
    app.run()

if __name__ == '__main__':
    main()
