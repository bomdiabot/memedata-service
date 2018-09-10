#!/usr/bin/env python3

from flask import Flask

from memedata.extensions import db, api
from memedata import config
from memedata.util import mk_errors

def get_app(config_obj=config.DevConfig):
    app = Flask(config.app_name)
    #configuration
    app.config.from_object(config_obj)
    #extensions
    register_extensions(app)
    #error handlers
    register_error_handlers(app)
    return app

def register_extensions(app):
    db.init_app(app)
    api.init_app(app)

def register_error_handlers(app):
    def error_handler(error):
        code = getattr(error, 'status_code', 500)
        try:
            message = getattr(error, 'message', str(error)[:1024])
        except:
            message = 'something went wrong!'
        return mk_errors(code, message)
    app.errorhandler(Exception)(error_handler)

def main():
    app = get_app()
    app.run()

if __name__ == '__main__':
    main()
