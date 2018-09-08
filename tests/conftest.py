import pytest
from service.api import get_app, get_api

@pytest.fixture()
def app_api():
    app = get_app()
    api = get_api(app)
    app.debug = True
    app.test_client()
    yield app, api
