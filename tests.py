import unittest
from flask import Flask
from flask_testing import TestCase
import urllib3

import flask_app

class TestFoo(TestCase):
    def create_app(self):
        app = Flask(__name__)
        app.config['TESTING'] = True
        return app
    def test_server_is_up_and_running(self):
        http = urllib3.PoolManager()
        response = http.request('GET', url)
        self.assertEqual(response.code, 200)

# class TestDB(TestCase):

#     SQLALCHEMY_DATABASE_URI = "sqlite://tests.db"
#     TESTING = True

#     def create_app(self):
#         app = Flask(__name__)
#         app.config['TESTING'] = True
#         app.config['LIVESERVER_PORT'] = 0
#         return app(self)

#     def setUp(self):
#         flask_app.db.create_all()

#     def tearDown(self):
#         flask_app.db.session.remove()
#         flask_app.db.drop_all()

#     def test_server_is_up_and_running(self):
#         response = urllib3.urlopen(self.get_server_url())
#         self.assertEqual(response.code, 200)

if __name__ == '__main__':
    unittest.main()