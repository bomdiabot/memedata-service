from flask import (
    make_response,
    jsonify,
)

def flatten(lsts):
    return [item for sublst in lsts for item in sublst]

def to_list(elem):
    if not isinstance(elem, list):
        elem = [elem]
    return elem

def mk_error(message_or_error, code=None):
    error = {}
    if isinstance(message_or_error, dict):
        error['message'] = str(message_or_error['message'])
        if 'code' in message_or_error.keys():
            error['code'] = int(message_or_error['code'])
    elif isinstance(message_or_error, tuple):
        message, code = message_or_error
        error = {'message': str(message), 'code': int(code)}
    else:
        error['message'] = str(message_or_error)
    if code is not None:
        error['code'] = int(code)
    return error

def mk_errors(code, messages_or_errors, as_response=True):
    messages_or_errors = to_list(messages_or_errors)
    errors = [mk_error(me) for me in messages_or_errors]
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
