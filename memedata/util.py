from flask import (
    make_response,
    jsonify,
)

from passlib.hash import pbkdf2_sha256 as sha256

def generate_hash(password):
    return sha256.hash(password)

def verify_hash(password, hsh):
    return sha256.verify(password, hsh)

def _filter_fields(objs, fields):
    fields = set(fields)
    if not isinstance(objs, list):
        return {k: v for k, v in objs.items() if k in fields}
    return [{k: v for k, v in obj.items() if k in fields} for obj in objs]

def filter_fields(objs, fields=None, enveloped=True):
    if fields is None:
        return objs
    if enveloped:
        assert len(objs.keys()) == 1, 'envelope should contain only 1 key'
        key = next(iter(objs.keys()))
        return {key: _filter_fields(objs[key], fields)}
    return _filter_fields(objs, fields)

def flatten(lsts):
    return [item for sublst in lsts for item in sublst]

def to_list(elem):
    if not isinstance(elem, list):
        elem = [elem]
    return elem

def mk_message(message_or_error, code=None):
    message = {}
    if isinstance(message_or_error, dict):
        message['message'] = str(message_or_error['message'])
        if 'code' in message_or_error.keys():
            message['code'] = int(message_or_error['code'])
    elif isinstance(message_or_error, tuple):
        message, code = message_or_error
        message = {'message': str(message), 'code': int(code)}
    else:
        message['message'] = str(message_or_error)
    if code is not None:
        message['code'] = int(code)
    return message

def mk_error(*args, **kwargs):
    return mk_message(*args, **kwargs)

def mk_errors(code, messages_or_errors, as_response=True):
    messages_or_errors = to_list(messages_or_errors)
    errors = [mk_message(me) for me in messages_or_errors]
    if as_response:
        return make_response(jsonify({'errors': errors}), code)
    else:
        return {'errors': errors}, code

def fmt_validation_error_messages(messages):
    if isinstance(messages, dict):
        return flatten(
            [["{}: {}".format(k, v) for v in to_list(vs)]\
                for k, vs in messages.items()])
    return [str(m) for m in to_list(messages)]
