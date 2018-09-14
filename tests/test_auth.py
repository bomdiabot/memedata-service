def test_su_can_login(client):
    resp = client.post('/auth/login',
        data={'username': 'su', 'password': 'testpass'})
    assert resp.status_code == 200
    assert 'access_token' in resp.json
    assert 'refresh_token' in resp.json

def test_unregistered_user_cannot_login(client):
    resp = client.post('/auth/login',
        data={'username': 'unregistered', 'password': 'testpass'})
    assert resp.status_code == 400

def test_su_can_register_user(su_with_tok):
    resp = su_with_tok.post('/users',
        data={'username': 'newuser', 'password': 'lalelilolu'})
    assert resp.status_code == 200

def test_logged_off_client_cannot_register_user(client):
    resp = client.post('/users',
        data={'username': 'newuser', 'password': 'lalelilolu'})
    assert resp.status_code == 401

def test_nonsu_cannot_register_user(client_with_tok):
    resp = client_with_tok.post('/users',
        data={'username': 'newuser', 'password': 'lalelilolu'})
    assert resp.status_code == 401

def test_registered_user_can_login(su_with_tok, client):
    su_with_tok.post('/users',
        data={'username': 'newuser', 'password': 'lalelilolu'})
    resp = client.post('/auth/login',
        data={'username': 'newuser', 'password': 'lalelilolu'})
    assert resp.status_code == 200
    assert 'access_token' in resp.json
    assert 'refresh_token' in resp.json

def test_registered_user_cannot_login_wrong_passwd(su_with_tok, client):
    su_with_tok.post('/users',
        data={'username': 'newuser', 'password': 'lalelilolu'})
    resp = client.post('/auth/login',
        data={'username': 'newuser', 'password': 'mimimimomu'})
    assert resp.status_code == 400

def test_su_can_get_users(su_with_tok):
    resp = su_with_tok.get('/users')
    assert resp.status_code == 200
    assert 'users' in resp.json

def test_logged_off_client_cannot_get_users(client):
    resp = client.get('/users')
    assert resp.status_code == 401

def test_nonsu_cannot_get_users(client_with_tok):
    resp = client_with_tok.get('/users')
    assert resp.status_code == 401

def test_user_can_refresh_tok(client_with_refresh_tok):
    resp = client_with_refresh_tok.post('/auth/token/refresh')
    assert resp.status_code == 200
    assert 'access_token' in resp.json

def test_user_can_use_new_tok(su_with_tok, client):
    resp1 = su_with_tok.post('/users',
        data={'username': 'testuser', 'password': 'lalelilolu'})
    resp2 = client.post('/auth/login',
        data={'username': 'testuser', 'password': 'lalelilolu'})
    #ok with first acc tok
    resp3 = client.get('/auth/ok',
        headers={'Authorization': \
            'Bearer {}'.format(resp2.json['access_token'])})
    resp4 = client.post('/auth/token/refresh',
        headers={'Authorization': \
            'Bearer {}'.format(resp2.json['refresh_token'])})
    #ok with new acc tok
    resp5 = client.get('/auth/ok',
        headers={'Authorization': \
            'Bearer {}'.format(resp4.json['access_token'])})
    assert resp3.status_code == 200
    assert 'access_token' in resp4.json
    assert resp5.status_code == 200

def test_user_can_logout_access(client_with_tok):
    resp = client_with_tok.post('/auth/logout/access')
    assert resp.status_code == 200

def test_user_can_logout_refresh(client_with_refresh_tok):
    resp = client_with_refresh_tok.post('/auth/logout/refresh')
    assert resp.status_code == 200

def test_user_cannot_use_revoked_tok(client_with_tok):
    resp1 = client_with_tok.get('/auth/ok')
    resp2 = client_with_tok.post('/auth/logout/access')
    resp3 = client_with_tok.get('/auth/ok')
    assert resp1.status_code == 200
    assert resp3.status_code == 401

def test_su_can_get_user(su_with_tok):
    resp1 = su_with_tok.get('/users')
    user_id = next(iter(resp1.json['users']))['user_id']
    resp2 = su_with_tok.get('/users/{}'.format(user_id))
    assert resp2.status_code == 200

def test_logged_off_client_cannot_get_user(su_with_tok, client):
    resp1 = su_with_tok.get('/users')
    user_id = next(iter(resp1.json['users']))['user_id']
    resp2 = client.get('/users/{}'.format(user_id))
    assert resp2.status_code == 401

def test_nonsu_client_cannot_get_user(su_with_tok, client_with_tok):
    resp1 = su_with_tok.get('/users')
    user_id = next(iter(resp1.json['users']))['user_id']
    resp2 = client_with_tok.get('/users/{}'.format(user_id))
    assert resp2.status_code == 401

def test_su_can_delete_user(su_with_tok):
    resp1 = su_with_tok.get('/users')
    user_id = next(iter(resp1.json['users']))['user_id']
    resp2 = su_with_tok.delete('/users/{}'.format(user_id))
    assert resp2.status_code == 204

def test_logged_off_client_cannot_delete_user(su_with_tok, client):
    resp1 = su_with_tok.get('/users')
    user_id = next(iter(resp1.json['users']))['user_id']
    resp2 = client.delete('/users/{}'.format(user_id))
    assert resp2.status_code == 401

def test_nonsu_client_cannot_delete_user(su_with_tok, client_with_tok):
    resp1 = su_with_tok.get('/users')
    user_id = next(iter(resp1.json['users']))['user_id']
    resp2 = client_with_tok.delete('/users/{}'.format(user_id))
    assert resp2.status_code == 401
