def test_texts_get_correct_response_format(client):
    resp = client.get('/texts')
    assert 'texts' in resp.json
    assert resp.json['texts'] == []

def test_texts_get_correct_number_elems(client):
    client.post('/texts', data={'content': 'test1'})
    obj = client.get('/texts').json
    assert len(obj['texts']) == 1

    client.post('/texts', data={'content': 'test2'})
    obj = client.get('/texts').json
    assert len(obj['texts']) == 2

    client.post('/texts', data={'content': 'test2'})
    obj = client.get('/texts').json
    assert len(obj['texts']) == 3

    obj = client.get('/texts').json
    assert len(obj['texts']) == 3

def test_texts_get_correct_elems(client):
    client.post('/texts', data={'content': 'test aaa'})
    client.post('/texts', data={'content': ' SLIRBORA'})
    client.post('/texts', data={'content': 'test  bcb'})

    elems = client.get('/texts').json['texts']
    assert len([e for e in elems if e['content'] == 'test aaa']) == 1
    assert len([e for e in elems if e['content'] == ' SLIRBORA']) == 1
    assert len([e for e in elems if e['content'] == 'test  bcb']) == 1

def test_texts_post_data_correct_response_format(client):
    resp = client.post('/texts', data={'content': 'this is a test'})
    assert 'text' in resp.json
    obj = resp.json['text']
    assert 'uid' in obj
    assert 'content' in obj
    assert 'created_at' in obj
    assert 'modified_at' in obj

def test_texts_post_qstring_correct_response_format(client):
    resp = client.post('/texts?content=this is a test')
    assert 'text' in resp.json
    obj = resp.json['text']
    assert 'uid' in obj
    assert 'content' in obj
    assert 'created_at' in obj
    assert 'modified_at' in obj

def test_texts_post_correct_response_fields_1(client):
    resp = client.post('/texts', data={'content': 'this is a test'})
    obj = resp.json['text']
    assert obj['content'] == 'this is a test'
    assert obj['created_at'] == obj['modified_at']

def test_texts_post_correct_response_fields_2(client):
    resp = client.post('/texts', data={'content': 'test 1'})
    obj1 = resp.json['text']
    assert obj1['content'] == 'test 1'
    assert obj1['created_at'] == obj1['modified_at']

    resp = client.post('/texts', data={'content': 'test 2'})
    obj2 = resp.json['text']
    assert obj2['content'] == 'test 2'
    assert obj2['created_at'] == obj2['modified_at']
    assert obj1['created_at'] != obj2['created_at']

def test_text_get_correct_response_format(client):
    resp = client.post('/texts?content=eyb0ss')
    uid = resp.json['text']['uid']

    resp = client.get('/texts/{}'.format(uid))
    assert 'text' in resp.json
    obj = resp.json['text']
    assert 'uid' in obj
    assert 'content' in obj
    assert 'created_at' in obj
    assert 'modified_at' in obj

def test_text_get_correct_response_fields(client):
    resp = client.post('/texts?content=eyb0ss')
    uid = resp.json['text']['uid']

    obj = client.get('/texts/{}'.format(uid)).json['text']
    assert obj['uid'] == uid
    assert obj['content'] == 'eyb0ss'
    assert obj['created_at'] == obj['modified_at']

def test_text_put_correct_response_format(client):
    obj = client.post('/texts?content=eyb0ss').json['text']
    uid = obj['uid']

    resp = client.put('/texts/{}?content=modified'.format(uid))
    assert 'text' in resp.json
    obj = resp.json['text']
    assert 'uid' in obj
    assert 'content' in obj
    assert 'created_at' in obj
    assert 'modified_at' in obj

def test_text_put_correct_response_fields(client):
    orig_obj = client.post('/texts?content=eyb0ss').json['text']
    orig_uid = orig_obj['uid']
    orig_created_at = orig_obj['created_at']
    orig_modified_at = orig_obj['modified_at']

    resp = client.put('/texts/{}?content=modified'.format(orig_uid))
    obj = resp.json['text']
    assert obj['uid'] == orig_uid
    assert obj['created_at'] == orig_created_at
    assert obj['modified_at'] != orig_modified_at
    assert obj['content'] == 'modified'

def test_text_delete_correct_response_format(client):
    obj = client.post('/texts?content=eyb0ss').json['text']
    uid = obj['uid']

    resp = client.delete('/texts/{}'.format(uid))
    assert resp.status_code == 200
    assert resp.get_json() == ''

def test_text_delete_deletes_elem(client):
    obj = client.post('/texts?content=eyb0ss').json['text']
    uid = obj['uid']

    client.delete('/texts/{}'.format(uid))
    obj = client.get('/texts').json['texts']
    assert len(obj) == 0

def test_text_delete_deletes_correct_elem(client):
    client.post('/texts?content=eyb0ss')
    obj = client.post('/texts?content=wow').json['text']
    uid = obj['uid']

    client.delete('/texts/{}'.format(uid))
    obj = client.get('/texts').json['texts']
    assert len(obj) == 1
    assert obj[0]['content'] == 'eyb0ss'
