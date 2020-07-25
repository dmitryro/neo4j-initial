from app import create_app
from app.config import test_config
from app.database import db
from app.user.models import User
from sqlalchemy.sql.expression import func
from faker import Faker
import unittest

admin_username = 'cburmeister'
admin_email = 'cburmeister@discogs.com'
admin_password = 'test123'

fake = Faker()


class TestCase(unittest.TestCase):
    def setUp(self):
        app = create_app(test_config)
        db.app = app  # hack for using db.init_app(app) in app/__init__.py
        self.app = app.test_client()

    def tearDown(self):
        pass
