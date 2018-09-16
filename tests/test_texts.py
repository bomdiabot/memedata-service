def test_texts_get_correct_response_format_1(client_with_tok):
    resp = client_with_tok.get('/texts')
    assert resp.status_code == 200
    assert 'texts' in resp.json
    assert resp.json['texts'] == []

def test_texts_get_correct_response_format_2(client_with_tok):
    client_with_tok.post('/texts', data={'content': 'test1'})
    client_with_tok.post('/texts', data={'content': 'test3'})
    resp = client_with_tok.get('/texts?fields=content,tags')
    assert 'texts' in resp.json
    assert all(set(o.keys()) == {'content', 'tags'} for o in resp.json['texts'])

def test_texts_get_correct_response_format_3(client_with_tok):
    client_with_tok.post('/texts', data={'content': 'test1'})
    client_with_tok.post('/texts', data={'content': 'test3'})
    resp = client_with_tok.get('/texts', query_string={'fields': 'text_id'})
    assert 'texts' in resp.json
    assert all(set(o.keys()) == {'text_id'} for o in resp.json['texts'])
    resp = client_with_tok.get('/texts?fields=')
    assert 'texts' in resp.json
    assert all(len(o.keys()) == 0 for o in resp.json['texts'])

def test_texts_get_correct_number_elems(client_with_tok):
    obj = client_with_tok.get('/texts').json
    assert len(obj['texts']) == 0

    client_with_tok.post('/texts', data={'content': 'test1'})
    obj = client_with_tok.get('/texts').json
    assert len(obj['texts']) == 1

    client_with_tok.post('/texts', data={'content': 'test2'})
    obj = client_with_tok.get('/texts').json
    assert len(obj['texts']) == 2

    client_with_tok.post('/texts', data={'content': 'test2'})
    obj = client_with_tok.get('/texts').json
    assert len(obj['texts']) == 3

    obj = client_with_tok.get('/texts').json
    assert len(obj['texts']) == 3

def test_texts_get_correct_elems(client_with_tok):
    client_with_tok.post('/texts', data={'content': 'test aaa'})
    client_with_tok.post('/texts', data={'content': ' SLIRBORA'})
    client_with_tok.post('/texts', data={'content': 'test  bcb'})
    elems = client_with_tok.get('/texts').json['texts']

    assert len([e for e in elems if e['content'] == 'test aaa']) == 1
    assert len([e for e in elems if e['content'] == ' SLIRBORA']) == 1
    assert len([e for e in elems if e['content'] == 'test  bcb']) == 1

def test_texts_get_search_correct_elems_1(client_with_tok):
    client_with_tok.post('/texts', data={'content': 'test aaa', 'tags': 'a,b,c'})
    client_with_tok.post('/texts', data={'content': 'SLIRBORA', 'tags': 'a,b'})
    client_with_tok.post('/texts', data={'content': 'test  bcb', 'tags': 'a'})

    elems = client_with_tok.get('/texts?any_tags=a').json['texts']
    assert len(elems) == 3
    elems = client_with_tok.get('/texts?any_tags=a,b').json['texts']
    assert len(elems) == 3
    elems = client_with_tok.get('/texts?any_tags=a,b,c').json['texts']
    assert len(elems) == 3
    elems = client_with_tok.get('/texts?any_tags=y').json['texts']
    assert len(elems) == 0

def test_texts_get_search_correct_elems_2(client_with_tok):
    client_with_tok.post('/texts', data={'content': 'test aaa', 'tags': 'a,b,c'})
    client_with_tok.post('/texts', data={'content': 'SLIRBORA', 'tags': 'a,b'})
    client_with_tok.post('/texts', data={'content': 'test  bcb', 'tags': 'a'})

    elems = client_with_tok.get('/texts?all_tags=a').json['texts']
    assert len(elems) == 3
    elems = client_with_tok.get('/texts?all_tags=a,b').json['texts']
    assert len(elems) == 2
    elems = client_with_tok.get('/texts?all_tags=a,b,c').json['texts']
    assert len(elems) == 1
    elems = client_with_tok.get('/texts?all_tags=x').json['texts']
    assert len(elems) == 0

def test_texts_get_search_correct_elems_3(client_with_tok):
    client_with_tok.post('/texts', data={'content': 'test aaa', 'tags': 'a,b,c'})
    client_with_tok.post('/texts', data={'content': 'SLIRBORA', 'tags': 'a,b'})
    client_with_tok.post('/texts', data={'content': 'test  bcb', 'tags': 'a'})

    elems = client_with_tok.get('/texts?all_tags=a&any_tags=a,b,c').json['texts']
    assert len(elems) == 3
    elems = client_with_tok.get('/texts?all_tags=a,b&any_tags=a,b,c').json['texts']
    assert len(elems) == 2
    elems = client_with_tok.get('/texts?all_tags=a,b,c&any_tags=a,b,c').json['texts']
    assert len(elems) == 1
    elems = client_with_tok.get('/texts?all_tags=x&any_tags=a,b,c').json['texts']
    assert len(elems) == 0

def test_texts_get_search_correct_elems_4(client_with_tok):
    client_with_tok.post('/texts', data={'content': 'test aaa', 'tags': 'a,b,c'})
    client_with_tok.post('/texts', data={'content': 'SLIRBORA', 'tags': 'a,b'})
    client_with_tok.post('/texts', data={'content': 'test  bcb', 'tags': 'a'})

    elems = client_with_tok.get('/texts?max_n_results=2').json['texts']
    assert len(elems) == 2
    elems = client_with_tok.get('/texts?all_tags=a&max_n_results=2').json['texts']
    assert len(elems) == 2
    elems = client_with_tok.get('/texts?all_tags=a&max_n_results=0').json['texts']
    assert len(elems) == 0

def test_texts_get_search_correct_elems_5(client_with_tok):
    """this test will fail in 2049."""
    client_with_tok.post('/texts', data={'content': 'test aaa', 'tags': 'a,b,c'})
    client_with_tok.post('/texts', data={'content': 'SLIRBORA', 'tags': 'a,b'})
    client_with_tok.post('/texts', data={'content': 'test  bcb', 'tags': 'a'})

    elems = client_with_tok.get('/texts?date_to=2049-12-20').json['texts']
    assert len(elems) == 3
    elems = client_with_tok.get('/texts?date_to=2000-11-01').json['texts']
    assert len(elems) == 0
    elems = client_with_tok.get('/texts?date_from=2000-01-01').json['texts']
    assert len(elems) == 3
    elems = client_with_tok.get(
        '/texts?date_from=2000-01-01&date_to=1994-03-24').json['texts']
    assert len(elems) == 0

def test_texts_get_search_correct_elems_6(client_with_tok):
    client_with_tok.post('/texts',
        data={'content': 'test aaa', 'tags': 'a,b,c'})
    client_with_tok.post('/texts', data={'content': 'SLIRBORA', 'tags': 'a,b'})
    client_with_tok.post('/texts', data={'content': 'test  bcb', 'tags': 'a'})

    elems = client_with_tok.get('/texts',
        query_string={'all_tags': 'a', 'any_tags': 'a,b,c'}).json['texts']
    assert len(elems) == 3
    elems = client_with_tok.get('/texts',
        query_string={'all_tags': 'a,b', 'any_tags': 'a,b,c'}).json['texts']
    assert len(elems) == 2
    elems = client_with_tok.get('/texts',
        query_string={'all_tags': 'a,b,c', 'any_tags': 'a,b,c'}).json['texts']
    assert len(elems) == 1
    elems = client_with_tok.get('/texts',
        query_string={'all_tags': 'x', 'any_tags': 'a,b,c'}).json['texts']
    assert len(elems) == 0

def test_texts_get_search_correct_elems_7(client_with_tok):
    client_with_tok.post('/texts',
        query_string={'content': 'test aaa', 'tags': 'a,b,c'})
    client_with_tok.post('/texts',
        query_string={'content': 'SLIRBORA', 'tags': 'a,b'})
    client_with_tok.post('/texts',
        query_string={'content': 'test  bcb', 'tags': 'a'})
    elems1 = client_with_tok.get('/texts',
        query_string={'no_tags': 'b,c'}).json['texts']
    elems3 = client_with_tok.get('/texts',
        query_string={'no_tags': 'a'}).json['texts']
    elems2 = client_with_tok.get('/texts',
        query_string={'any_tags': 'a', 'no_tags': 'a'}).json['texts']

    assert len(elems1) == 1
    assert elems1[0]['tags'] == ['a']
    assert len(elems2) == 0
    assert len(elems3) == 0

def test_texts_get_ignores_form(client_with_tok):
    client_with_tok.post('/texts',
        query_string={'content': 'test aaa', 'tags': 'a,b,c'})
    client_with_tok.post('/texts',
        query_string={'content': 'SLIRBORA', 'tags': 'a,b'})
    client_with_tok.post('/texts',
        query_string={'content': 'test  bcb', 'tags': 'a'})
    resp = client_with_tok.get('/texts',
        data={'no_tags': 'a'})
    assert len(resp.json['texts']) == 3

def test_texts_correct_pagination_1(client_with_tok):
    client_with_tok.post('/texts',
        data={'content': 'test aaa', 'tags': 'a,b,c'})
    client_with_tok.post('/texts',
        data={'content': 'test bbb', 'tags': 'x'})
    client_with_tok.post('/texts',
        data={'content': 'test ccc', 'tags': 'a,b,c'})
    client_with_tok.post('/texts',
        data={'content': 'test ddd'})

    obj1 = client_with_tok.get('/texts?max_n_results=4').json
    obj2 = client_with_tok.get('/texts?max_n_results=3').json
    assert obj1['offset'] is None
    assert obj2['offset'] == 3

def test_texts_correct_pagination_2(client_with_tok):
    client_with_tok.post('/texts',
        data={'content': 'aa', 'tags': 'a,b,c'})
    client_with_tok.post('/texts',
        data={'content': 'bb', 'tags': 'x'})
    client_with_tok.post('/texts',
        data={'content': 'cc', 'tags': 'a,b,c'})
    client_with_tok.post('/texts',
        data={'content': 'dd'})

    obj1 = client_with_tok.get('/texts?max_n_results=2').json
    obj2 = client_with_tok.get('/texts?offset=2').json
    assert obj1['offset'] == 2
    assert {o['content'] for o in obj1['texts']} == {'aa', 'bb'}
    assert obj2['offset'] == None
    assert {o['content'] for o in obj2['texts']} == {'cc', 'dd'}

def test_texts_get_cannot_get_logged_of(client):
    resp = client.get('/texts')
    assert resp.status_code == 401

def test_texts_post_data_correct_response_format(client_with_tok):
    resp = client_with_tok.post('/texts', data={'content': 'this is a test'})

    assert resp.status_code == 201
    assert 'text' in resp.json
    obj = resp.json['text']
    assert 'text_id' in obj
    assert 'content' in obj
    assert 'created_at' in obj
    assert 'updated_at' in obj
    assert 'tags' in obj

def test_texts_post_qstring_correct_response_format(client_with_tok):
    resp = client_with_tok.post('/texts?content=this is a test')

    assert 'text' in resp.json
    obj = resp.json['text']
    assert 'text_id' in obj
    assert 'content' in obj
    assert 'created_at' in obj
    assert 'updated_at' in obj
    assert 'tags' in obj

def test_texts_post_correct_response_fields_1(client_with_tok):
    resp = client_with_tok.post('/texts', data={'content': 'this is a test'})
    obj = resp.json['text']

    assert obj['content'] == 'this is a test'
    assert obj['created_at']
    assert obj['updated_at'] is None

def test_texts_post_correct_response_fields_2(client_with_tok):
    resp = client_with_tok.post('/texts', data={'content': 'test 1'})
    obj1 = resp.json['text']
    resp = client_with_tok.post('/texts', data={'content': 'test 2'})
    obj2 = resp.json['text']

    assert obj1['content'] == 'test 1'
    assert obj1['created_at']
    assert obj2['content'] == 'test 2'
    assert obj2['created_at']
    assert obj1['created_at'] <= obj2['created_at']

def test_texts_post_correct_response_fields_3(client_with_tok):
    resp = client_with_tok.post('/texts',
        data={'content': 'this is a test', 'tags': 'ey,b0ss'})
    obj = resp.json['text']

    assert obj['content'] == 'this is a test'
    assert obj['created_at']
    assert obj['updated_at'] is None
    assert set(obj['tags']) == {'ey', 'b0ss'}

def test_texts_post_ignores_spurious_args(client_with_tok):
    resp = client_with_tok.post('/texts',
        data={'content': 'test 1', 'ow': 'hehe', 'ljh': 'hhh'})

    assert resp.status_code == 201
    assert 'text' in resp.json

def test_texts_post_correct_error_format_1(client_with_tok):
    resp = client_with_tok.post('/texts', data={'wrong': 'keypair'})

    assert resp.status_code == 400
    assert set(resp.json.keys()) == {'errors'}

def test_texts_post_correct_error_format_2(client_with_tok):
    resp = client_with_tok.post('/texts',
            data={'content': 'correct', 'tags': 'right,invalid space'})

    assert resp.status_code == 400
    assert set(resp.json.keys()) == {'errors'}

def test_texts_post_correct_error_format_3(client_with_tok):
    resp = client_with_tok.post('/texts',
            data={'content': 'correct', 'tags': 'blackl?isted,generated'})

    assert resp.status_code == 400
    assert set(resp.json.keys()) == {'errors'}

def test_texts_post_cannot_post_logged_of(client):
    resp = client.post('/texts?content=this is a test')
    assert resp.status_code == 401

def test_text_get_correct_response_format_1(client_with_tok):
    resp = client_with_tok.post('/texts?content=eyb0ss')
    text_id = resp.json['text']['text_id']
    resp = client_with_tok.get('/texts/{}'.format(text_id))

    assert resp.status_code == 200
    assert 'text' in resp.json
    obj = resp.json['text']
    assert 'text_id' in obj
    assert 'content' in obj
    assert 'created_at' in obj
    assert 'updated_at' in obj

def test_text_get_correct_response_format_2(client_with_tok):
    resp = client_with_tok.post('/texts',
        data={'content': 'test1', 'tags': 'lel,hue'})
    text_id = resp.json['text']['text_id']
    resp = client_with_tok.get('/texts/{}'.format(text_id),
        query_string={'fields': 'text_id,tags'})
    assert set(resp.json['text'].keys()) == {'text_id', 'tags'}

def test_text_get_ignores_form(client_with_tok):
    resp = client_with_tok.post('/texts',
        data={'content': 'test1', 'tags': 'lel,hue'})
    text_id = resp.json['text']['text_id']
    resp = client_with_tok.get('/texts/{}'.format(text_id),
        data={'fields': 'text_id,tags'})
    assert set(resp.json['text'].keys()) != {'text_id', 'tags'}

def test_text_get_correct_response_fields(client_with_tok):
    resp = client_with_tok.post('/texts?content=eyb0ss')
    text_id = resp.json['text']['text_id']
    obj = client_with_tok.get('/texts/{}'.format(text_id)).json['text']

    assert obj['text_id'] == text_id
    assert obj['content'] == 'eyb0ss'
    assert obj['created_at']
    assert obj['updated_at'] is None

def test_text_get_correct_error_format(client_with_tok):
    resp = client_with_tok.get('/texts/1')
    assert resp.status_code == 404
    assert set(resp.json.keys()) == {'errors'}

def test_text_get_cannot_get_logged_of(client_with_tok, client):
    resp1 = client_with_tok.post('/texts?content=eyb0ss')
    resp2 = client.get('/texts/{}'.format(resp1.json['text']['text_id']))
    assert resp2.status_code == 401

def test_text_put_correct_response_format(client_with_tok):
    obj = client_with_tok.post('/texts?content=eyb0ss').json['text']
    text_id = obj['text_id']
    resp = client_with_tok.put('/texts/{}?content=updated'.format(text_id))

    assert resp.status_code == 200
    assert 'text' in resp.json
    obj = resp.json['text']
    assert 'text_id' in obj
    assert 'content' in obj
    assert 'created_at' in obj
    assert 'updated_at' in obj

def test_text_put_correct_response_format_2(client_with_tok):
    obj = client_with_tok.post('/texts?content=eyb0ss').json['text']
    text_id = obj['text_id']
    resp = client_with_tok.put('/texts/{}'.format(text_id), data={'wrong': 'keypair'})

    assert resp.status_code == 200
    assert 'text' in resp.json
    obj = resp.json['text']
    assert 'text_id' in obj
    assert 'content' in obj
    assert 'created_at' in obj
    assert 'updated_at' in obj

def test_text_put_correct_response_fields(client_with_tok):
    orig_obj = client_with_tok.post('/texts?content=eyb0ss').json['text']
    orig_text_id = orig_obj['text_id']
    orig_created_at = orig_obj['created_at']
    orig_updated_at = orig_obj['updated_at']
    resp = client_with_tok.put('/texts/{}?content=updated'.format(orig_text_id))
    obj = resp.json['text']

    assert obj['text_id'] == orig_text_id
    assert obj['created_at'] == orig_created_at
    assert obj['updated_at'] != orig_updated_at
    assert obj['content'] == 'updated'

def test_text_put_correct_error_format_1(client_with_tok):
    resp = client_with_tok.put('/texts/3')
    assert resp.status_code == 404
    assert set(resp.json.keys()) == {'errors'}

def test_text_put_cannot_put_logged_of(client_with_tok, client):
    resp1 = client_with_tok.post('/texts?content=eyb0ss')
    resp2 = client.put('/texts/{}?content=updated'.format(
        resp1.json['text']['text_id']))
    assert resp2.status_code == 401

def test_text_delete_correct_response_format(client_with_tok):
    obj = client_with_tok.post('/texts?content=eyb0ss').json['text']
    text_id = obj['text_id']

    resp = client_with_tok.delete('/texts/{}'.format(text_id))
    assert resp.status_code == 204

def test_text_delete_deletes_elem(client_with_tok):
    obj = client_with_tok.post('/texts?content=eyb0ss').json['text']
    text_id = obj['text_id']

    client_with_tok.delete('/texts/{}'.format(text_id))
    obj = client_with_tok.get('/texts').json['texts']
    assert len(obj) == 0

def test_text_delete_deletes_correct_elem(client_with_tok):
    client_with_tok.post('/texts?content=eyb0ss')
    obj = client_with_tok.post('/texts?content=wow').json['text']
    text_id = obj['text_id']

    client_with_tok.delete('/texts/{}'.format(text_id))
    obj = client_with_tok.get('/texts').json['texts']
    assert len(obj) == 1
    assert obj[0]['content'] == 'eyb0ss'

def test_text_delete_correct_error_format(client_with_tok):
    resp = client_with_tok.delete('/texts/3')
    assert resp.status_code == 404
    assert set(resp.json.keys()) == {'errors'}

def test_text_delete_cannot_delete_logged_of(client_with_tok, client):
    resp1 = client_with_tok.post('/texts?content=eyb0ss')
    resp2 = client.delete('/texts/{}'.format(resp1.json['text']['text_id']))
    assert resp2.status_code == 401
