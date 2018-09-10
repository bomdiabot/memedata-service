#!/usr/bin/env python3

from flask import Flask

from memedata.extensions import db, api
from memedata import config

def get_app(config_obj=config.DevConfig):
    app = Flask(config.app_name)
    #configuration
    app.config.from_object(config_obj)
    #extensions
    register_extensions(app)
    return app

def register_extensions(app):
    db.init_app(app)
    api.init_app(app)

def main():
    app = get_app()
    app.run()

if __name__ == '__main__':
    main()
