def test_registration_get_correct_response_format(client):
    resp = client.post('/users',
        data={'username': 'test', 'password': 'lalelilolu'})
    assert resp.status_code == 200
    assert 'access_token' in resp.json
    assert 'refresh_token' in resp.json

def test_registration_get_correct_response_format_2(client):
    resp = client.post('/users?username=test&password=lalelilolu')
    assert resp.status_code == 200
    assert 'access_token' in resp.json
    assert 'refresh_token' in resp.json

def test_registration_get_correct_response_fields(client):
    resp = client.post('/users',
        data={'username': 'test', 'password': 'lalelilolu'})
    assert resp.json['access_token'] != resp.json['refresh_token']

def test_registration_get_correct_error_format(client):
    resp = client.post('/users',
        data={'username': 'test', 'pasdjhsword': 'lalelilolu'})
    assert resp.status_code == 400

def test_registration_cannot_register_twice_1(client):
    resp1 = client.post('/users',
        data={'username': 'test', 'password': 'lalelilolu'})
    resp2 = client.post('/users',
        data={'username': 'test', 'password': 'lalelilolu'})
    assert resp1.status_code == 200
    assert resp2.status_code == 400

def test_registration_cannot_register_twice_2(client):
    resp1 = client.post('/users',
        data={'username': 'test', 'password': 'lalelilolu'})
    resp2 = client.post('/users?username=test&password=xxx')
    assert resp1.status_code == 200
    assert resp2.status_code == 400

def test_login_cannot_login_unregistered(client):
    resp = client.post('/users/login',
        data={'username': 'test', 'password': 'lalelilolu'})
    assert resp.status_code == 400

def test_login_can_login_registered(client):
    resp1 = client.post('/users',
        data={'username': 'test', 'password': 'lalelilolu'})
    resp2 = client.post('/users/login',
        data={'username': 'test', 'password': 'lalelilolu'})
    assert resp1.status_code == 200
    assert resp2.status_code == 200

def test_login_cannot_login_wrong_credentials(client):
    resp1 = client.post('/users',
        data={'username': 'test', 'password': 'lalelilolu'})
    resp2 = client.post('/users/login',
        data={'username': 'test', 'password': 'Mlalelilolu'})
    assert resp1.status_code == 200
    assert resp2.status_code == 400

def test_cannot_refresh_token_unregistered(client):
    resp = client.post('/users/token/refresh',
        data={'username': 'test', 'password': 'lalelilolu'})
    assert resp.status_code == 401

def test_cannot_refresh_token_logged_out(client):
    resp1 = client.post('/users',
        data={'username': 'test', 'password': 'lalelilolu'})
    resp2 = client.post('/users/token/refresh',
        data={'username': 'test', 'password': 'lalelilolu'})
    assert resp1.status_code == 200
    assert resp2.status_code == 401

def test_cannot_refresh_token_logged_in_without_token(client):
    resp1 = client.post('/users',
        data={'username': 'test', 'password': 'lalelilolu'})
    resp2 = client.post('/users/login',
        data={'username': 'test', 'password': 'lalelilolu'})
    resp3 = client.post('/users/token/refresh',
        data={'username': 'test', 'password': 'lalelilolu'})
    assert resp1.status_code == 200
    assert resp2.status_code == 200
    assert resp3.status_code == 401

def test_can_refresh_token_logged_in_with_token(client):
    resp1 = client.post('/users',
        data={'username': 'test', 'password': 'lalelilolu'})
    resp2 = client.post('/users/login',
        data={'username': 'test', 'password': 'lalelilolu'})
    resp3 = client.post('/users/token/refresh',
        headers={'Authorization': \
            'Bearer {}'.format(resp2.json['refresh_token'])},
        data={'username': 'test', 'password': 'lalelilolu'})
    assert resp1.status_code == 200
    assert resp2.status_code == 200
    assert resp3.status_code == 200

def test_cannot_refresh_token_logged_in_with_wrong_token(client):
    resp1 = client.post('/users',
        data={'username': 'test', 'password': 'lalelilolu'})
    resp2 = client.post('/users/login',
        data={'username': 'test', 'password': 'lalelilolu'})
    resp3 = client.post('/users/token/refresh',
        headers={'Authorization': \
            'Bearer {}'.format(resp2.json['access_token'])},
        data={'username': 'test', 'password': 'lalelilolu'})
    assert resp1.status_code == 200
    assert resp2.status_code == 200
    assert resp3.status_code == 422

def test_cannot_get_users_unregistered(client):
    resp = client.get('/users')
    assert resp.status_code == 401

def test_cannot_get_users_logged_out(client):
    resp1 = client.post('/users',
        data={'username': 'test', 'password': 'lalelilolu'})
    resp2 = client.get('/users')
    assert resp1.status_code == 200
    assert resp2.status_code == 401

def test_cannot_get_users_logged_in_without_jwt(client):
    resp1 = client.post('/users',
        data={'username': 'test', 'password': 'lalelilolu'})
    resp2 = client.post('/users/login',
        data={'username': 'test', 'password': 'lalelilolu'})
    resp3 = client.get('/users')
    assert resp1.status_code == 200
    assert resp2.status_code == 200
    assert resp3.status_code == 401

def test_can_get_users_logged_in_with_jwt(client):
    resp1 = client.post('/users',
        data={'username': 'test', 'password': 'lalelilolu'})
    resp2 = client.post('/users/login',
        data={'username': 'test', 'password': 'lalelilolu'})
    resp3 = client.get('/users',
        headers={'Authorization': \
            'Bearer {}'.format(resp2.json['access_token'])})
    assert resp1.status_code == 200
    assert resp2.status_code == 200
    assert resp3.status_code == 200

def test_cannot_get_user_logged_out(client):
    resp1 = client.post('/users',
        data={'username': 'test', 'password': 'lalelilolu'})
    resp2 = client.get('/users/{}'.format(resp1.json['user_id']))
    assert resp1.status_code == 200
    assert resp2.status_code == 401

def test_cannot_get_user_logged_in_without_jwt(client):
    resp1 = client.post('/users',
        data={'username': 'test', 'password': 'lalelilolu'})
    resp2 = client.post('/users/login',
        data={'username': 'test', 'password': 'lalelilolu'})
    resp3 = client.get('/users/{}'.format(resp1.json['user_id']))
    assert resp1.status_code == 200
    assert resp2.status_code == 200
    assert resp3.status_code == 401

def test_can_get_user_logged_in_with_jwt(client):
    resp1 = client.post('/users',
        data={'username': 'test', 'password': 'lalelilolu'})
    resp2 = client.post('/users/login',
        data={'username': 'test', 'password': 'lalelilolu'})
    resp3 = client.get('/users/{}'.format(resp1.json['user_id']),
        headers={'Authorization': \
            'Bearer {}'.format(resp2.json['access_token'])})
    assert resp1.status_code == 200
    assert resp2.status_code == 200
    assert resp3.status_code == 200

def test_can_get_any_user_logged_in_with_jwt(client):
    resp0 = client.post('/users',
        data={'username': 'test', 'password': 'lalelilolu'})
    resp1 = client.post('/users',
        data={'username': 'test2', 'password': 'lalelilolu'})
    resp2 = client.post('/users/login',
        data={'username': 'test', 'password': 'lalelilolu'})
    resp3 = client.get('/users/{}'.format(resp0.json['user_id']),
        headers={'Authorization': \
            'Bearer {}'.format(resp2.json['access_token'])})
    resp4 = client.get('/users/{}'.format(resp1.json['user_id']),
        headers={'Authorization': \
            'Bearer {}'.format(resp2.json['access_token'])})
    assert resp0.status_code == 200
    assert resp1.status_code == 200
    assert resp2.status_code == 200
    assert resp3.status_code == 200
    assert resp4.status_code == 200

def test_cannot_delete_user_logged_out(client):
    resp1 = client.post('/users',
        data={'username': 'test', 'password': 'lalelilolu'})
    resp2 = client.delete('/users/{}'.format(resp1.json['user_id']))
    assert resp1.status_code == 200
    assert resp2.status_code == 401

def test_cannot_delete_user_logged_in_without_jwt(client):
    resp1 = client.post('/users',
        data={'username': 'test', 'password': 'lalelilolu'})
    resp2 = client.post('/users/login',
        data={'username': 'test', 'password': 'lalelilolu'})
    resp3 = client.delete('/users/{}'.format(resp1.json['user_id']))
    assert resp1.status_code == 200
    assert resp2.status_code == 200
    assert resp3.status_code == 401

def test_can_delete_user_logged_in_with_jwt(client):
    resp1 = client.post('/users',
        data={'username': 'test', 'password': 'lalelilolu'})
    resp2 = client.post('/users/login',
        data={'username': 'test', 'password': 'lalelilolu'})
    resp3 = client.delete('/users/{}'.format(resp1.json['user_id']),
        headers={'Authorization': \
            'Bearer {}'.format(resp2.json['access_token'])})
    assert resp1.status_code == 200
    assert resp2.status_code == 200
    assert resp3.status_code == 204

def test_can_delete_any_user_logged_in_with_jwt(client):
    resp0 = client.post('/users',
        data={'username': 'test', 'password': 'lalelilolu'})
    resp1 = client.post('/users',
        data={'username': 'test2', 'password': 'lalelilolu'})
    resp2 = client.post('/users/login',
        data={'username': 'test', 'password': 'lalelilolu'})
    resp3 = client.delete('/users/{}'.format(resp0.json['user_id']),
        headers={'Authorization': \
            'Bearer {}'.format(resp2.json['access_token'])})
    resp4 = client.delete('/users/{}'.format(resp1.json['user_id']),
        headers={'Authorization': \
            'Bearer {}'.format(resp2.json['access_token'])})
    assert resp0.status_code == 200
    assert resp1.status_code == 200
    assert resp2.status_code == 200
    assert resp3.status_code == 204
    assert resp4.status_code == 204

def test_cannot_logout_access_logged_out(client):
    resp1 = client.post('/users',
        data={'username': 'test', 'password': 'lalelilolu'})
    resp2 = client.post('/users/logout/access',
        data={'username': 'test', 'password': 'lalelilolu'})
    assert resp1.status_code == 200
    assert resp2.status_code == 401

def test_cannot_logout_access_logged_in_without_token(client):
    resp1 = client.post('/users',
        data={'username': 'test', 'password': 'lalelilolu'})
    resp2 = client.post('/users/login',
        data={'username': 'test', 'password': 'lalelilolu'})
    resp3 = client.post('/users/logout/access',
        data={'username': 'test', 'password': 'lalelilolu'})
    assert resp1.status_code == 200
    assert resp2.status_code == 200
    assert resp3.status_code == 401

def test_can_logout_access_logged_in_with_token(client):
    resp1 = client.post('/users',
        data={'username': 'test', 'password': 'lalelilolu'})
    resp2 = client.post('/users/login',
        data={'username': 'test', 'password': 'lalelilolu'})
    resp3 = client.post('/users/logout/access',
        headers={'Authorization': \
            'Bearer {}'.format(resp2.json['access_token'])})
    assert resp1.status_code == 200
    assert resp2.status_code == 200
    assert resp3.status_code == 200

def test_can_logout_refresh_logged_in_with_token(client):
    resp1 = client.post('/users',
        data={'username': 'test', 'password': 'lalelilolu'})
    resp2 = client.post('/users/login',
        data={'username': 'test', 'password': 'lalelilolu'})
    resp3 = client.post('/users/logout/refresh',
        headers={'Authorization': \
            'Bearer {}'.format(resp2.json['refresh_token'])})
    assert resp1.status_code == 200
    assert resp2.status_code == 200
    assert resp3.status_code == 200

def test_can_fully_logout_logged_in_with_token(client):
    resp1 = client.post('/users',
        data={'username': 'test', 'password': 'lalelilolu'})
    resp2 = client.post('/users/login',
        data={'username': 'test', 'password': 'lalelilolu'})
    resp3 = client.post('/users/logout/access',
        headers={'Authorization': \
            'Bearer {}'.format(resp2.json['access_token'])})
    resp4 = client.post('/users/logout/refresh',
        headers={'Authorization': \
            'Bearer {}'.format(resp2.json['refresh_token'])})
    assert resp1.status_code == 200
    assert resp2.status_code == 200
    assert resp3.status_code == 200
    assert resp4.status_code == 200

def test_can_logout_refresh_cannot_refresh(client):
    resp1 = client.post('/users',
        data={'username': 'test', 'password': 'lalelilolu'})
    resp2 = client.post('/users/login',
        data={'username': 'test', 'password': 'lalelilolu'})
    resp3 = client.post('/users/logout/refresh',
        headers={'Authorization': \
            'Bearer {}'.format(resp2.json['refresh_token'])})
    resp4 = client.post('/users/token/refresh',
        headers={'Authorization': \
            'Bearer {}'.format(resp2.json['refresh_token'])})
    assert resp1.status_code == 200
    assert resp2.status_code == 200
    assert resp3.status_code == 200
    assert resp4.status_code == 401

def test_logs_out_cannot_get_users(client):
    resp1 = client.post('/users',
        data={'username': 'test', 'password': 'lalelilolu'})
    resp2 = client.post('/users/login',
        data={'username': 'test', 'password': 'lalelilolu'})
    resp3 = client.get('/users',
        headers={'Authorization': \
            'Bearer {}'.format(resp2.json['access_token'])})
    resp4 = client.post('/users/logout/access',
        headers={'Authorization': \
            'Bearer {}'.format(resp2.json['access_token'])})
    resp5 = client.get('/users',
        headers={'Authorization': \
            'Bearer {}'.format(resp2.json['access_token'])})
    assert resp1.status_code == 200
    assert resp2.status_code == 200
    assert resp3.status_code == 200
    assert resp4.status_code == 200
    assert resp5.status_code == 401
