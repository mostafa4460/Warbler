"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

USER1 = {
    "email": "test@test.com",
    "username": "testuser",
    "password": "HASHED_PASSWORD"
}

USER2 = {
    "email": "test2@test.com",
    "username": "testuser2",
    "password": "HASHED_PASSWORD2"
}

class UserModelTestCase(TestCase):
    """Test the User model."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        user1 = User(**USER1)
        user2 = User(**USER2)
        db.session.add_all([user1, user2])
        db.session.commit()

        self.client = app.test_client()
        self.user1 = user1
        self.user2 = user2
    
    def tearDown(self):
        """Clean up fouled transactions."""

        db.session.rollback()

    def test_model(self):
        """Does basic model work?"""

        # self.user should have no messages & no followers
        self.assertEqual(len(self.user1.messages), 0)
        self.assertEqual(len(self.user1.followers), 0)

    def test_repr(self):
        """Tests the User __repr__ method"""

        self.assertEqual(self.user1.__repr__(), f"<User #{self.user1.id}: {self.user1.username}, {self.user1.email}>")

    def test_is_following(self):
        """Tests the is_following instance method"""

        # should return false because user1 still does not follow user2
        self.assertFalse(self.user1.is_following(self.user2))

        # let user1 follow user2
        self.user1.following.append(self.user2)
        # should now return true
        self.assertTrue(self.user1.is_following(self.user2))

    def test_is_followed_by(self):
        """Tests the is_followed_by instance method"""

        # should return false because user2 is still not followed by user1
        self.assertFalse(self.user2.is_followed_by(self.user1))

        # let user1 follow user2
        self.user2.followers.append(self.user1)
        # should now return true
        self.assertTrue(self.user2.is_followed_by(self.user1))

    def test_signup(self):
        """Tests the User.signup class method"""

        USER3 = {
            "email": "test3@test.com",
            "username": "testuser3",
            "password": "HASHED_PASSWORD3",
            "image_url": "https://www.petmd.com/sites/default/files/Acute-Dog-Diarrhea-47066074.jpg"
        }

        # valid credentials
        new_user = User.signup(**USER3)
        # should return new User instance with hashed password (not real one)
        self.assertIsInstance(new_user, User)
        self.assertNotEqual(new_user.password, USER3["password"])
        
        # invalid credentials (username) missing
        USER3.pop("username")
        # should raise TypeError
        self.assertRaises(TypeError, User.signup, **USER3)

    def test_authenticate(self):
        """Tests the User.authenticate class method"""

        new_user = User.signup(
            email = "test3@test.com",
            username = "testuser3",
            password = "HASHED_PASSWORD3",
            image_url = "https://www.petmd.com/sites/default/files/Acute-Dog-Diarrhea-47066074.jpg"
        )

        # wrong username, should return false
        self.assertFalse(User.authenticate(username="testuser7", password="HASHED_PASSWORD3"))
        # wrong password, should return false
        self.assertFalse(User.authenticate(username=new_user.username, password="HASHED_PASSWORD2"))

        # right login, should return new_user User instance
        self.assertEqual(User.authenticate(username=new_user.username, password="HASHED_PASSWORD3"), new_user)