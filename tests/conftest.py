import pytest
from service.api import get_app, get_api
from service import texts, images
from service.database import drop_all

from io import BytesIO
from PIL import Image

@pytest.fixture()
def app_api():
    app = get_app()
    api = get_api(app)
    app.debug = True
    app.testing = True
    yield app, api

@pytest.fixture()
def image_getter():
    def image_getter_color(color):
        f = BytesIO()
        image = Image.new('RGBA', size=(25, 40), color=color)
        image.save(f, 'png')
        f.name = 'test.png'
        f.seek(0)
        return f
    return image_getter_color

@pytest.fixture()
def client(app_api):
    #setup
    app, api = app_api
    drop_all()

    with app.test_client() as c:
        yield c

    #fake images db
    images.DB.clear()
