def test_texts_get_correct_response_format(client):
    resp = client.get('/texts')
    assert resp.status_code == 200
    assert 'texts' in resp.json
    assert resp.json['texts'] == []

def test_texts_get_correct_number_elems(client):
    obj = client.get('/texts').json
    assert len(obj['texts']) == 0

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

    assert resp.status_code == 201
    assert 'text' in resp.json
    obj = resp.json['text']
    assert 'text_id' in obj
    assert 'content' in obj
    assert 'created_at' in obj
    assert 'updated_at' in obj

def test_texts_post_qstring_correct_response_format(client):
    resp = client.post('/texts?content=this is a test')

    assert 'text' in resp.json
    obj = resp.json['text']
    assert 'text_id' in obj
    assert 'content' in obj
    assert 'created_at' in obj
    assert 'updated_at' in obj

def test_texts_post_correct_response_fields_1(client):
    resp = client.post('/texts', data={'content': 'this is a test'})
    obj = resp.json['text']

    assert obj['content'] == 'this is a test'
    assert obj['created_at']
    assert obj['updated_at'] is None

def test_texts_post_correct_response_fields_2(client):
    resp = client.post('/texts', data={'content': 'test 1'})
    obj1 = resp.json['text']
    resp = client.post('/texts', data={'content': 'test 2'})
    obj2 = resp.json['text']

    assert obj1['content'] == 'test 1'
    assert obj1['created_at']
    assert obj2['content'] == 'test 2'
    assert obj2['created_at']
    assert obj1['created_at'] <= obj2['created_at']

def test_texts_post_ignores_spurious_args(client):
    resp = client.post('/texts',
        data={'content': 'test 1', 'ow': 'hehe', 'ljh': 'hhh'})

    assert resp.status_code == 201
    assert 'text' in resp.json

def test_texts_post_correct_error_format(client):
    resp = client.post('/texts', data={'wrong': 'keypair'})

    assert resp.status_code == 400
    assert set(resp.json.keys()) == {'errors'}

def test_text_get_correct_response_format(client):
    resp = client.post('/texts?content=eyb0ss')
    text_id = resp.json['text']['text_id']
    resp = client.get('/texts/{}'.format(text_id))

    assert resp.status_code == 200
    assert 'text' in resp.json
    obj = resp.json['text']
    assert 'text_id' in obj
    assert 'content' in obj
    assert 'created_at' in obj
    assert 'updated_at' in obj

def test_text_get_correct_response_fields(client):
    resp = client.post('/texts?content=eyb0ss')
    text_id = resp.json['text']['text_id']
    obj = client.get('/texts/{}'.format(text_id)).json['text']

    assert obj['text_id'] == text_id
    assert obj['content'] == 'eyb0ss'
    assert obj['created_at']
    assert obj['updated_at'] is None

def test_text_get_correct_error_format(client):
    resp = client.get('/texts/1')
    assert resp.status_code == 404
    assert set(resp.json.keys()) == {'errors'}

def test_text_put_correct_response_format(client):
    obj = client.post('/texts?content=eyb0ss').json['text']
    text_id = obj['text_id']
    resp = client.put('/texts/{}?content=updated'.format(text_id))

    assert resp.status_code == 200
    assert 'text' in resp.json
    obj = resp.json['text']
    assert 'text_id' in obj
    assert 'content' in obj
    assert 'created_at' in obj
    assert 'updated_at' in obj

def test_text_put_correct_response_format_2(client):
    obj = client.post('/texts?content=eyb0ss').json['text']
    text_id = obj['text_id']
    resp = client.put('/texts/{}'.format(text_id), data={'wrong': 'keypair'})

    assert resp.status_code == 200
    assert 'text' in resp.json
    obj = resp.json['text']
    assert 'text_id' in obj
    assert 'content' in obj
    assert 'created_at' in obj
    assert 'updated_at' in obj

def test_text_put_correct_response_fields(client):
    orig_obj = client.post('/texts?content=eyb0ss').json['text']
    orig_text_id = orig_obj['text_id']
    orig_created_at = orig_obj['created_at']
    orig_updated_at = orig_obj['updated_at']
    resp = client.put('/texts/{}?content=updated'.format(orig_text_id))
    obj = resp.json['text']

    assert obj['text_id'] == orig_text_id
    assert obj['created_at'] == orig_created_at
    assert obj['updated_at'] != orig_updated_at
    assert obj['content'] == 'updated'

def test_text_put_correct_error_format_1(client):
    resp = client.put('/texts/3')

    assert resp.status_code == 404
    assert set(resp.json.keys()) == {'errors'}

def test_text_delete_correct_response_format(client):
    obj = client.post('/texts?content=eyb0ss').json['text']
    text_id = obj['text_id']

    resp = client.delete('/texts/{}'.format(text_id))
    assert resp.status_code == 204

def test_text_delete_deletes_elem(client):
    obj = client.post('/texts?content=eyb0ss').json['text']
    text_id = obj['text_id']

    client.delete('/texts/{}'.format(text_id))
    obj = client.get('/texts').json['texts']
    assert len(obj) == 0

def test_text_delete_deletes_correct_elem(client):
    client.post('/texts?content=eyb0ss')
    obj = client.post('/texts?content=wow').json['text']
    text_id = obj['text_id']

    client.delete('/texts/{}'.format(text_id))
    obj = client.get('/texts').json['texts']
    assert len(obj) == 1
    assert obj[0]['content'] == 'eyb0ss'

def test_text_delete_correct_error_format(client):
    resp = client.delete('/texts/3')
    assert resp.status_code == 404
    assert set(resp.json.keys()) == {'errors'}
