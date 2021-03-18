"""Message model tests."""

import os
from unittest import TestCase
from datetime import datetime

from models import db, User, Message, Follows

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app

db.create_all()

USER = {
    "email": "test@test.com",
    "username": "testuser",
    "password": "HASHED_PASSWORD"
}

class MessageModelTestCase(TestCase):
    """Test the Message model."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        user = User(**USER)
        db.session.add(user)
        db.session.commit()

        self.client = app.test_client()
        self.user = user
    
    def tearDown(self):
        """Clean up fouled transactions."""

        db.session.rollback()

    def test_model(self):
        """Tests the basic model"""

        new_msg = Message(text="Test message", user_id=self.user.id)
        db.session.add(new_msg)
        db.session.commit()

        # user should now have 1 messages
        self.assertEqual(len(self.user.messages), 1)

        # new_msg should have a timestamp
        self.assertIsInstance(new_msg.timestamp, datetime)