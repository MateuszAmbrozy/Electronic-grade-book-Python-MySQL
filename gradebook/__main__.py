"""Command-line entry point; importing the package never creates a window."""

import argparse
from getpass import getpass
import logging
from pathlib import Path
import sys

from gradebook.database import Database
from gradebook.demo import seed_demo
from gradebook.service import Gradebook


def main(argv=None):
    parser = argparse.ArgumentParser(description="Gradebook desktop school management")
    parser.add_argument("--backend", choices=("demo", "mysql"), default="demo")
    parser.add_argument("--demo-path", type=Path, default=Path.home() / ".gradebook" / "demo.sqlite3")
    parser.add_argument("--init-db", action="store_true", help="Create missing tables and exit")
    parser.add_argument("--create-admin", action="store_true", help="Create the first headteacher interactively")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    db = None
    try:
        if args.backend == "demo":
            args.demo_path.parent.mkdir(parents=True, exist_ok=True)
            db = Database.sqlite(args.demo_path)
            db.initialize()
            if not args.create_admin:
                seed_demo(db)
        else:
            db = Database.mysql()
            if args.init_db:
                db.initialize()
        if args.create_admin:
            first_name = input("First name: ")
            last_name = input("Last name: ")
            email = input("Email: ")
            password = getpass("Password (at least 10 characters): ")
            if password != getpass("Confirm password: "):
                raise ValueError("The passwords do not match.")
            Gradebook(db).bootstrap(first_name, last_name, email, password)
            print("Headteacher account created.")
            return 0
        if args.init_db:
            print("Database tables are ready.")
            return 0
        from gradebook.ui import Application

        app = Application(Gradebook(db), demo=args.backend == "demo")
        app.mainloop()
        return 0
    except Exception as exc:
        logging.error("Unable to start Gradebook: %s", exc)
        return 1
    finally:
        if db is not None:
            db.close()


if __name__ == "__main__":
    sys.exit(main())
