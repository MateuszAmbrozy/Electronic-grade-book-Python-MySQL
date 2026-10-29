"""Opt-in MySQL integration test. Requires an empty, disposable database."""

import os
import unittest

from gradebook.database import Database
from gradebook.demo import DEMO_PASSWORD, seed_demo
from gradebook.service import Gradebook


@unittest.skipUnless(
    os.environ.get("GRADEBOOK_MYSQL_TEST") == "1", "Set GRADEBOOK_MYSQL_TEST=1 for a disposable MySQL database"
)
class MySQLTests(unittest.TestCase):
    def test_fresh_database_workflows(self):
        db = Database.mysql()
        try:
            db.initialize()
            self.assertEqual(db.execute("SELECT id FROM users"), [], "Use a fresh, disposable database")
            seed_demo(db)
            service = Gradebook(db)
            service.login("student@gradebook.demo", DEMO_PASSWORD)
            self.assertEqual(len(service.lessons()), 15)
            self.assertEqual(len(service.grades()), 9)
            self.assertGreater(len(service.attendance()), 0)
            self.assertEqual(len(service.messages()), 2)
            service.change_password(DEMO_PASSWORD, "MySQLPassword2026!")
            service.login("student@gradebook.demo", "MySQLPassword2026!")
            service.send_message("teacher@gradebook.demo", "Integration check", "MySQL messaging works.")
            service.login("teacher@gradebook.demo", DEMO_PASSWORD)
            self.assertEqual(service.messages()[0]["subject"], "Integration check")
        finally:
            db.close()
