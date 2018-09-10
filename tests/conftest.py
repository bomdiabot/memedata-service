import pytest
from memedata.app import get_app
from memedata.resources import images
from memedata.config import TestConfig
from memedata.database import db

from io import BytesIO
from PIL import Image

@pytest.fixture()
def app():
    #setup
    app = get_app(TestConfig)
    with app.app_context():
        db.create_all()
    yield app
    #teardown
    with app.app_context():
        db.session.remove()
        db.drop_all()

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
def client(app):
    with app.test_client() as c:
        yield c

    #fake images db
    images.DB.clear()
