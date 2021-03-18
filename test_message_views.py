"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)
        self.testuser_id = 8989
        self.testuser.id = self.testuser_id
        db.session.commit()

    def tearDown(self):
        """Clean up fouled transactions."""

        db.session.rollback()

    def test_add_message(self):
        """Can use add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.filter(Message.text == "Hello").one()
            self.assertEqual(msg.text, "Hello")

    def test_add_message_no_login(self):
        with self.client as c:
            resp = c.post('/messages/new', data={"text": "testing message"}, follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized.", str(resp.data))

    def test_show_messages(self):
        """Tests the show a message view"""

        msg = Message(
            id=1234,
            text="testing message", 
            user_id=self.testuser_id)
        db.session.add(msg)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            msg = Message.query.get(1234)
            resp = c.get(f'/messages/{msg.id}')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(msg.text, html)

    def test_delete_message(self):
        """Tests the deletion of a message"""

        msg = Message(
            id=1234,
            text="testing message", 
            user_id=self.testuser_id
        )
        db.session.add(msg)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.post('/messages/1234/delete', follow_redirects=True)

            self.assertEqual(resp.status_code, 200)

            msg = Message.query.get(1234)
            self.assertIsNone(msg)

        def test_unauthorized_message_delete(self):
            """Tests the deletion of a message from an unauthorized user"""

            # testuser2
            new_user = User.signup(
                username="testuser2",
                email="test2@test.com",
                password="testuser2",
                image_url=None
            )
            new_user.id = 321

            # owned by testuser1
            msg = Message(
                id=1234,
                text="testing message", 
                user_id=self.testuser_id
            )

            db.session.add_all([new_user, msg])
            db.session.commit()

            with self.client as c:
                with c.session_transaction() as sess:
                    sess[CURR_USER_KEY] = 321

            resp = c.post('/messages/1234/delete', follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized.", str(resp.data))

            self.assertEqual(len(self.testuser.messages), 1)