import unittest
from flask import Flask
from flask_testing import TestCase
import urllib3

from flask_app import db

class TestDB(TestCase):

    SQLALCHEMY_DATABASE_URI = "sqlite://tests.db"
    TESTING = True

    def create_app(self):
        app = Flask(__name__)
        app.config['TESTING'] = True
        app.config['LIVESERVER_PORT'] = 0
        return app(self)

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_server_is_up_and_running(self):
        response = urllib3.urlopen(self.get_server_url())
        self.assertEqual(response.code, 200)

if __name__ == '__main__':
    unittest.main()