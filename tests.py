import os

os.environ["DATABASE_URL"] = "sqlite://"

from datetime import datetime, timezone, timedelta
import unittest
from app import app, db
from app.models import User, Match, Score


class UserModelCase(unittest.TestCase):
    def setUp(self):
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_hashing(self):
        u = User(username="susan", email="susan@example.com")
        u.set_password("cat")
        self.assertFalse(u.check_password("dog"))
        self.assertTrue(u.check_password("cat"))

    def test_avatar(self):
        u = User(
            username="john", email="john@example.com", forename="john", surname="wick"
        )
        self.assertEqual(
            u.avatar(128),
            (
                "https://www.gravatar.com/avatar/d4c74594d841139328695756648b6bd6?d=identicon&s=128"
            ),
        )
    
    def test_score(self):
        u = User(
            username="john", email="john@example.com", forename="john", surname="wick"
        )
        m = Match(opponent="opponent", location="location")
        db.session.add(u)
        db.session.add(m)
        db.session.commit()
        
        user_scores = db.session.query(Score).filter(Score.user_id == u.id).all()
        match_scores = db.session.query(Score).filter(Score.match_id == m.id).all()
        self.assertEqual(user_scores, [])
        self.assertEqual(match_scores, [])

        # create a score instance and associate it with the user and match
        s = Score(score=5, turn_number=1, user_id=u.id, match_id=m.id)
        db.session.add(s)
        db.session.commit()
        
        user_scores = db.session.query(Score).filter(Score.user_id == u.id).all()
        match_scores = db.session.query(Score).filter(Score.match_id == m.id).all()
        self.assertEqual(user_scores[0].score, 5)
        self.assertEqual(match_scores[0].score, 5)

        # use remove_score with the actual score object
        # pass the score object
        u.remove_score(s)
        db.session.commit()

        user_scores = db.session.query(Score).filter(Score.user_id == u.id).all()
        match_scores = db.session.query(Score).filter(Score.match_id == m.id).all()
        self.assertEqual(user_scores, [])
        self.assertEqual(match_scores, [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
