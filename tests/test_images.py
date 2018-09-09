import numpy as np

def test_images_get_correct_response_format(client):
    resp = client.get('/images')
    assert resp.status_code == 200
    assert 'images' in resp.json
    assert resp.json['images'] == []

def test_images_get_correct_number_elems(client, image_getter):
    obj = client.get('/images').json
    assert len(obj['images']) == 0

    client.post('/images', data={'image': image_getter('red')},
        content_type='multipart/form-data')
    obj = client.get('/images').json
    assert len(obj['images']) == 1

    client.post('/images', data={'image': image_getter('green')},
        content_type='multipart/form-data')
    obj = client.get('/images').json
    assert len(obj['images']) == 2

    client.post('/images', data={'image': image_getter('blue')},
        content_type='multipart/form-data')
    obj = client.get('/images').json
    assert len(obj['images']) == 3

    obj = client.get('/images').json
    assert len(obj['images']) == 3

def test_images_get_correct_elems(client, image_getter):
    resp = client.post('/images', data={'image': image_getter('red')},
        content_type='multipart/form-data')
    uid_1 = resp.json['image']['uid']
    resp = client.post('/images', data={'image': image_getter('blue')},
        content_type='multipart/form-data')
    uid_2 = resp.json['image']['uid']
    resp = client.post('/images', data={'image': image_getter('blue')},
        content_type='multipart/form-data')
    uid_3 = resp.json['image']['uid']

    elems = client.get('/images').json['images']
    assert len([e for e in elems if e['uid'] == uid_1]) == 1
    assert len([e for e in elems if e['uid'] == uid_2]) == 1
    assert len([e for e in elems if e['uid'] == uid_3]) == 1

def test_images_post_correct_response_format(client, image_getter):
    resp = client.post('/images', data={'image': image_getter('red')},
        content_type='multipart/form-data')
    assert resp.status_code == 201
    assert 'image' in resp.json

    obj = resp.json['image']
    assert 'uid' in obj
    assert 'created_at' in obj
    assert 'modified_at' in obj

def test_images_post_correct_response_fields_1(client, image_getter):
    resp = client.post('/images', data={'image': image_getter('red')},
        content_type='multipart/form-data')
    obj = resp.json['image']
    assert obj['created_at'] == obj['modified_at']

def test_images_post_correct_response_fields_2(client, image_getter):
    resp = client.post('/images', data={'image': image_getter('red')},
        content_type='multipart/form-data')
    obj1 = resp.json['image']

    resp = client.post('/images', data={'image': image_getter('green')},
        content_type='multipart/form-data')
    obj2 = resp.json['image']

    assert obj1['modified_at'] != obj2['modified_at']
    assert obj1['created_at'] != obj2['created_at']

def test_images_post_correct_response_fields_3(client, image_getter):
    resp = client.post('/images', data={'image': image_getter('red')},
        content_type='multipart/form-data')
    obj1 = resp.json['image']

    resp = client.post('/images', data={'image': image_getter('green')},
        content_type='multipart/form-data')
    obj2 = resp.json['image']

    assert obj1['modified_at'] != obj2['modified_at']
    assert obj1['created_at'] != obj2['created_at']

def test_images_post_ignores_spurious_args(client, image_getter):
    resp = client.post('/images',
        data={'image': image_getter('red'), 'this': 'should', 'be': 'ignored'},
        content_type='multipart/form-data')
    assert resp.status_code == 201
    assert 'image' in resp.json

def test_images_post_correct_error_format(client, image_getter):
    resp = client.post('/images', data={'wrong': 'keypair'})
    assert resp.status_code == 400
    assert set(resp.json.keys()) == {'errors'}

def test_image_get_correct_response_format_1(client, image_getter):
    resp = client.post('/images', data={'image': image_getter('red')},
        content_type='multipart/form-data')
    uid = resp.json['image']['uid']

    resp = client.get('/images/{}'.format(uid))
    assert resp.status_code == 200
    assert 'image' in resp.json

    obj = resp.json['image']
    assert 'uid' in obj
    assert 'created_at' in obj
    assert 'modified_at' in obj

def test_image_get_correct_response_format_2(client, image_getter):
    resp = client.post('/images', data={'image': image_getter('red')},
        content_type='multipart/form-data')
    uid = resp.json['image']['uid']

    resp = client.get('/images/{}'.format(uid),
        headers={'accept': 'image/png'})
    assert resp.status_code == 200

def dissimilarity(a, b):
    return ((a.flatten() - b.flatten())**2).mean()

def test_image_get_correct_response_format_3(client, image_getter):
    orig_img1 = np.frombuffer(image_getter('red').read(), dtype='uint8')
    resp = client.post('/images', data={'image': image_getter('red')},
        content_type='multipart/form-data')
    uid1 = resp.json['image']['uid']
    resp = client.get('/images/{}'.format(uid1),
        headers={'accept': 'image/png'})
    img1 = np.frombuffer(resp.data, dtype='uint8')

    orig_img2 = np.frombuffer(image_getter('blue').read(), dtype='uint8')
    resp = client.post('/images', data={'image': image_getter('blue')},
        content_type='multipart/form-data')
    uid2 = resp.json['image']['uid']
    resp = client.get('/images/{}'.format(uid2),
        headers={'accept': 'image/png'})
    img2 = np.frombuffer(resp.data, dtype='uint8')

    assert orig_img1.shape == img1.shape
    assert orig_img2.shape == img2.shape
    assert dissimilarity(orig_img1, img1) <= dissimilarity(orig_img1, img2)
    assert dissimilarity(orig_img2, img2) <= dissimilarity(orig_img2, img1)

def test_image_get_correct_error_format(client):
    resp = client.get('/images/1')
    assert resp.status_code == 404
    assert set(resp.json.keys()) == {'errors'}

def test_image_put_correct_response_format(client, image_getter):
    resp = client.post('/images', data={'image': image_getter('red')},
        content_type='multipart/form-data')

    uid = resp.json['image']['uid']
    resp = client.put('/images/{}'.format(uid),
        data={'image': image_getter('blue')},
        content_type='multipart/form-data')
    assert resp.status_code == 200
    assert 'image' in resp.json

    obj = resp.json['image']
    assert 'uid' in obj
    assert 'created_at' in obj
    assert 'modified_at' in obj

def test_image_put_correct_response_fields_1(client, image_getter):
    resp = client.post('/images', data={'image': image_getter('red')},
        content_type='multipart/form-data')

    uid = resp.json['image']['uid']
    resp = client.put('/images/{}'.format(uid),
        data={'image': image_getter('blue')},
        content_type='multipart/form-data')

    obj = resp.json['image']
    assert obj['created_at'] != obj['modified_at']

def test_image_put_correct_response_fields_2(client, image_getter):
    resp = client.post('/images', data={'image': image_getter('red')},
        content_type='multipart/form-data')

    uid = resp.json['image']['uid']
    resp = client.put('/images/{}'.format(uid),
        data={'image': image_getter('blue')},
        content_type='multipart/form-data')

    resp = client.get('/images/{}'.format(uid), headers={'accept': 'image/png'})
    red_img = np.frombuffer(image_getter('red').read(), dtype='uint8')
    blue_img = np.frombuffer(image_getter('blue').read(), dtype='uint8')
    img = np.frombuffer(resp.data, dtype='uint8')

    assert dissimilarity(img, blue_img) < dissimilarity(img, red_img)

def test_image_put_correct_error_format_1(client, image_getter):
    resp = client.put('/images/332', data={'image': image_getter('red')},
        content_type='multipart/form-data')
    assert resp.status_code == 404
    assert set(resp.json.keys()) == {'errors'}

def test_image_put_correct_error_format_2(client, image_getter):
    resp = client.post('/images', data={'image': image_getter('red')},
        content_type='multipart/form-data')

    uid = resp.json['image']['uid']
    resp = client.put('/images/{}'.format(uid), data={'wrong': 'pair'},
        content_type='multipart/form-data')
    assert resp.status_code == 400
    assert set(resp.json.keys()) == {'errors'}

def test_image_delete_correct_response_format(client, image_getter):
    resp = client.post('/images', data={'image': image_getter('red')},
        content_type='multipart/form-data')

    uid = resp.json['image']['uid']
    resp = client.delete('/images/{}'.format(uid))
    assert resp.status_code == 204

def test_image_delete_deletes_elem(client, image_getter):
    resp = client.post('/images', data={'image': image_getter('red')},
        content_type='multipart/form-data')

    uid = resp.json['image']['uid']
    client.delete('/images/{}'.format(uid))
    obj = client.get('/images').json['images']
    assert len(obj) == 0
 
def test_image_delete_deletes_correct_elem(client, image_getter):
    resp = client.post('/images', data={'image': image_getter('red')},
        content_type='multipart/form-data')
    uid1 = resp.json['image']['uid']
    resp = client.post('/images', data={'image': image_getter('blue')},
        content_type='multipart/form-data')
    uid2 = resp.json['image']['uid']

    client.delete('/images/{}'.format(uid2))
    obj = client.get('/images').json['images']
    assert len(obj) == 1
    assert obj[0]['uid'] == uid1

def test_image_delete_correct_error_format(client):
    resp = client.delete('/images/3')
    assert resp.status_code == 404
    assert set(resp.json.keys()) == {'errors'}
