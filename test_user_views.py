"""User View tests"""

import os
from unittest import TestCase
from models import db, connect_db, User, Message, Follows, Like

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app, CURR_USER_KEY

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False
app.config['DEBUG'] = True
app.config['TESTING'] = True

class UserViewTestCase(TestCase):
    """Test views for users"""

    def setUp(self):
        """Create test client and sample data"""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.u1 = User.signup(username="user1", email="user1@test.com", password="password", image_url=None)
        self.u1_id = 1212
        self.u1.id = self.u1_id

        self.u2 = User.signup(username="user2", email="user2@test.com", password="password", image_url=None)
        self.u2_id = 2323
        self.u2.id = self.u2_id

        self.u3 = User.signup(username="user3", email="user3@test.com", password="password", image_url=None)
        self.u3_id = 3434
        self.u3.id = self.u3_id

        self.u4 = User.signup(username="abcde", email="user4@test.com", password="password", image_url=None)
        self.u4_id = 4545
        self.u4.id = self.u4_id

        db.session.commit()

    def tearDown(self):
        """Clean up fouled transactions."""

        db.session.rollback()

    def test_list_users(self):
        """Tests the all users page"""

        with self.client as c:
            resp = c.get('/users')

            self.assertEqual(resp.status_code, 200)
            self.assertIn("@user1", str(resp.data))
            self.assertIn("@user2", str(resp.data))
            self.assertIn("@user3", str(resp.data))
            self.assertIn("@abcde", str(resp.data))

    def test_list_users_search(self):
        """Tests the all users page filtered by a search"""

        with self.client as c:
            resp = c.get('/users?q=user')

            self.assertEqual(resp.status_code, 200)
            self.assertIn("@user1", str(resp.data))
            self.assertIn("@user2", str(resp.data))
            self.assertIn("@user3", str(resp.data))
            self.assertNotIn("@abcde", str(resp.data))

    def test_show_user(self):
        """Tests the user profile page"""

        with self.client as c:
            resp = c.get('/users/1212')

            self.assertEqual(resp.status_code, 200)
            self.assertIn("@user1", str(resp.data))

    def setup_followers(self):
        """Adds follows between users"""

        f1 = Follows(user_being_followed_id=self.u1_id, user_following_id=self.u2_id)
        f2 = Follows(user_being_followed_id=self.u1_id, user_following_id=self.u3_id)
        f3 = Follows(user_being_followed_id=self.u4_id, user_following_id=self.u1_id)

        db.session.add_all([f1, f2, f3])
        db.session.commit()

    def test_show_following(self):
        """Tests the show following page"""

        self.setup_followers()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            resp = c.get('/users/1212/following')

            self.assertEqual(resp.status_code, 200)
            self.assertIn("@abcde", str(resp.data))

    def test_show_followers(self):
        """Tests the show followers page"""

        self.setup_followers()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            resp = c.get('/users/1212/followers')

            self.assertEqual(resp.status_code, 200)
            self.assertIn("@user2", str(resp.data))
            self.assertIn("@user3", str(resp.data))

    def test_show_following_unauthorized(self):
        """Tests the show following page when no users are logged in"""

        self.setup_followers()

        with self.client as c:
            resp = c.get('/users/1212/following', follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertNotIn("@abcde", str(resp.data))
            self.assertIn("Access unauthorized.", str(resp.data))

    def test_show_followers_unauthorized(self):
        """Tests the show followers page when no users are logged in"""

        self.setup_followers()

        with self.client as c:
            resp = c.get('/users/1212/followers', follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertNotIn("@user2", str(resp.data))
            self.assertNotIn("@user3", str(resp.data))
            self.assertIn("Access unauthorized.", str(resp.data))

    def test_add_follow(self):
        """Tests the add follow route for the current-user"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            resp = c.post('/users/follow/2323', follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("@user2", str(resp.data))
            self.assertEqual(Follows.query.count(), 1)

    def test_add_follow_unauthorized(self):
        """Tests the add follow route without a current-user logged in"""

        with self.client as c:
            resp = c.post('/users/follow/2323', follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized.", str(resp.data))
            self.assertEqual(Follows.query.count(), 0)
        
    def test_stop_follow(self):
        """Tests the add follow route for the current-user"""

        self.setup_followers()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            resp = c.post('/users/stop-following/4545', follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertNotIn("@abcde", str(resp.data))

            # the setup_followers() method added 3 follows at start
            # now, there should be only 2 follows left
            self.assertEqual(Follows.query.count(), 2)

    def setup_messages(self):
        """Adds messages for test users"""

        m1 = Message(id=321, text="user2 message", user_id=self.u2_id)
        m2 = Message(id=322, text="user3 message", user_id=self.u3_id)

        db.session.add_all([m1, m2])
        db.session.commit()

    def setup_likes(self):
        """Adds message likes for test users"""

        l1 = Like(user_id=self.u1_id, message_id=321)
        l2 = Like(user_id=self.u1_id, message_id=322)

        db.session.add_all([l1, l2])
        db.session.commit()

    def test_show_likes(self):
        """Tests the show all user likes page"""

        self.setup_messages()
        self.setup_likes()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

        resp = c.get('/users/1212/likes')

        self.assertEqual(resp.status_code, 200)

        # check for the liked messages' texts
        self.assertIn("user2 message", str(resp.data))
        self.assertIn("user3 message", str(resp.data))

    def test_show_likes_unauthorized(self):
        """Tests the show all user likes page without logging in"""

        self.setup_messages()
        self.setup_likes()

        with self.client as c:
            resp = c.get('/users/1212/likes', follow_redirects=True)

            self.assertEqual(resp.status_code, 200)

            # check for the liked messages' texts
            self.assertNotIn("user2 message", str(resp.data))
            self.assertNotIn("user3 message", str(resp.data))

            self.assertIn("Access unauthorized.", str(resp.data))

    def test_add_like(self):
        """Tests the add a like to current-user route"""

        self.setup_messages()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

        # first time hitting the route (message not currently liked by user)
        # message should get liked
        resp = c.post('/users/add_like/321', follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Like.query.count(), 1)

        # second time hitting the route (message IS currently liked by user)
        # message should get unliked
        resp = c.post('/users/add_like/321', follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Like.query.count(), 0)