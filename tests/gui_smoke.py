"""Run with xvfb-run -a python3 tests/gui_smoke.py from the repository root."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from gradebook.database import Database
from gradebook.demo import DEMO_PASSWORD, seed_demo
from gradebook.service import Gradebook
from gradebook.ui import Application


def main():
    db = Database.sqlite()
    db.initialize()
    seed_demo(db)
    service = Gradebook(db)
    app = Application(service, demo=True)
    errors = []
    app.report_callback_exception = lambda *args: errors.append(args)
    app.update()
    screenshots = "--screenshots" in sys.argv
    if screenshots:
        from PIL import ImageGrab

        ImageGrab.grab().save("docs/login.png")
    for role in ("student", "teacher", "admin"):
        service.login(f"{role}@gradebook.demo", DEMO_PASSWORD)
        app.show_workspace()
        app.update()
        for index in range(len(app.notebook.tabs())):
            app.notebook.select(index)
            app.update()
        if role == "student":
            app.notebook.select(0)
            app.update()
            if screenshots:
                ImageGrab.grab().save("docs/overview.png")
        if role == "admin":
            app.lesson_manager()
            app.update()
            app.lesson_dialog(lambda: None)
            app.update()
        for child in app.winfo_children():
            if child.winfo_class() == "Toplevel":
                child.destroy()
        app.show_login()
        app.update()
    app.destroy()
    db.close()
    if errors:
        raise AssertionError(errors)
    print("GUI smoke check passed: login, all role pages, lesson manager, lesson form, sign-out.")


if __name__ == "__main__":
    main()
