import pytest
from service.api import get_app, get_api
from service import texts, images

@pytest.fixture()
def app_api():
    app = get_app()
    api = get_api(app)
    app.debug = True
    app.testing = True
    yield app, api

@pytest.fixture()
def client(app_api):
    #setup
    app, api = app_api

    with app.test_client() as c:
        yield c

    #teardown
    texts.DB.clear()
    images.DB.clear()
