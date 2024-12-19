import unittest
from app import app, db

class FlaskAppTests(unittest.TestCase):
    def setUp(self):
        self.app = app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_add_profile_picture(self):
        # Your test code here
        pass

    def test_delete_profile_picture(self):
        # Your test code here
        pass

    def test_user_authentication(self):
        # Your test code here
        pass

if __name__ == '__main__':
    unittest.main()
