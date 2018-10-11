'''
Memedata API client.
'''

import requests

_DEF_IP = '35.226.124.10'
_DEF_PORT = 7310

class AuthError(Exception):
    pass

def _handle_response(method_fn):
    def wrapper(*args, **kwargs):
        resp = method_fn(*args, **kwargs)
        if resp.status_code in {400, 401}:
            raise AuthError
        return resp
    return wrapper

#decorating CRUD methods
_get = _handle_response(requests.get)
_post = _handle_response(requests.post)
_put = _handle_response(requests.put)
_delete = _handle_response(requests.delete)

def _refresh_tok_or_login_if_needed(fn):
        def wrapper(self, *args, **kwargs):
            try:
                ret = fn(self, *args, **kwargs)
            except AuthError:
                try:
                    self.refresh_acc_tok()
                    ret = fn(self, *args, **kwargs)
                except AuthError:
                    try:
                        self.login()
                        ret = fn(self, *args, **kwargs)
                    except:
                        raise
            return ret
        return wrapper

class Client:
    DEF_API_URL = 'http://{}:{}'.format(_DEF_IP, _DEF_PORT)
    ENDPOINTS = {
        'login': '/auth/login',
        'texts': '/texts',
        'acc-tok-refresh': '/auth/token/refresh',
    }

    @staticmethod
    def _format_list(lst):
        '''formats list into comma-separated string'''
        if isinstance(lst, (list, tuple)):
            lst = ','.join(lst)
        return lst

    @staticmethod
    def _format_post_or_put_data(content=None, tags=[]):
        data = {}
        if content is not None:
            data['content'] = content
        if tags:
            data['tags'] = Client._format_list(tags)
        return data

    def __init__(self, username, password, api_url=DEF_API_URL):
        self.username = username
        self.password = password
        self.api_url = api_url
        self.acc_tok = None
        self.refr_tok = None
        self.login()

    def get_endpoint_url(self, endpoint):
        assert endpoint in Client.ENDPOINTS.keys()
        url = '{}{}'.format(self.api_url, Client.ENDPOINTS[endpoint])
        return url

    def get_auth_header(self, use_acc_tok=True):
        assert self.acc_tok is not None and self.refr_tok is not None
        tok = self.acc_tok if use_acc_tok else self.refr_tok
        header = {
            'Authorization': 'Bearer {}'.format(tok),
        }
        return header

    def login(self):
        resp = _post(
            self.get_endpoint_url('login'),
            data={
                'username': self.username,
                'password': self.password,
            }
        )
        if resp.status_code != 200:
            raise ClientAuthError('could not login with credentials')
        json_resp = resp.json()
        self.acc_tok = json_resp['access_token']
        self.refr_tok = json_resp['refresh_token']
        return json_resp

    def refresh_acc_tok(self):
        resp = _post(
            self.get_endpoint_url('acc-tok-refresh'),
            headers=self.get_auth_header(use_acc_tok=False),
        )
        if resp.status_code != 200:
            raise ClientAuthError('could not refresh access token')
        self.acc_tok = resp.json()['access_token']

    @_refresh_tok_or_login_if_needed
    def get_texts(self,
            fields=None,
            date_from=None, date_to=None,
            any_tags=None, all_tags=None, no_tags=None,
            offset=0, max_n_results=1000
        ):
        query = [
            'offset={}'.format(offset),
            'max_n_results={}'.format(max_n_results),
        ]
        if fields is not None:
            query.append('fields={}'.format(Client._format_list(fields)))
        if date_from is not None:
            query.append('date_from={}'.format(date_from))
        if date_to is not None:
            query.append('date_to={}'.format(date_to))
        if any_tags is not None:
            query.append('any_tags={}'.format(Client._format_list(any_tags)))
        if all_tags is not None:
            query.append('all_tags={}'.format(Client._format_list(all_tags)))
        if no_tags is not None:
            query.append('no_tags={}'.format(Client._format_list(no_tags)))
        query_string = '&'.join(query)
        url = '{}?{}'.format(self.get_endpoint_url('texts'), query_string)
        resp = _get(
            url,
            headers=self.get_auth_header(),
        )
        assert resp.status_code == 200
        return resp.json()['texts']

    @_refresh_tok_or_login_if_needed
    def iter_all_texts(self, **kwargs):
        if not 'offset' in kwargs:
            kwargs['offset'] = 0
        if not 'max_n_results' in kwargs:
            kwargs['max_n_results'] = 1000
        while True:
            texts = self.get_texts(**kwargs)
            for txt in texts:
                yield txt
            kwargs['offset'] += len(texts)
            if len(texts) < kwargs['max_n_results']:
                break

    @_refresh_tok_or_login_if_needed
    def get_text(self, text_id):
        url = '{}/{}'.format(self.get_endpoint_url('texts'), text_id)
        resp = _get(
            url,
            headers=self.get_auth_header(),
        )
        if resp.status_code == 404:
            raise ValueError('text_id {} does not exist'.format(text_id))
        assert resp.status_code == 200
        return resp.json()['text']

    @_refresh_tok_or_login_if_needed
    def post_text(self, content, tags=[]):
        resp = _post(
            self.get_endpoint_url('texts'),
            headers=self.get_auth_header(),
            data=Client._format_post_or_put_data(content, tags),
        )
        assert resp.status_code == 201
        return resp.json()['text']

    @_refresh_tok_or_login_if_needed
    def update_text(self, text_id, content=None, tags=[]):
        url = '{}/{}'.format(self.get_endpoint_url('texts'), text_id)
        resp = _put(
            url,
            headers=self.get_auth_header(),
            data=Client._format_post_or_put_data(content, tags),
        )
        if resp.status_code == 404:
            raise ValueError('text_id {} does not exist'.format(text_id))
        assert resp.status_code == 200
        return resp.json()['text']

    @_refresh_tok_or_login_if_needed
    def del_text(self, text_id):
        url = '{}/{}'.format(self.get_endpoint_url('texts'), text_id)
        resp = _delete(
            url,
            headers=self.get_auth_header(),
        )
        if resp.status_code == 404:
            raise ValueError('text_id {} does not exist'.format(text_id))
        assert resp.status_code == 204
        return {}
