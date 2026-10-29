"""English-only Tkinter desktop interface with a shared visual system."""

from datetime import date
import logging
import tkinter as tk
from tkinter import messagebox, ttk

from gradebook.demo import DEMO_PASSWORD
from gradebook.service import DAYS, ROLES, STATUSES, weighted_average

BG = "#f3f5f9"
NAVY = "#15263f"
INK = "#1d2d45"
MUTED = "#62748b"
BLUE = "#315cf5"


class Application(tk.Tk):
    def __init__(self, service, demo=False):
        super().__init__()
        self.service = service
        self.demo = demo
        self.title("Gradebook | School, connected")
        self.geometry("1160x860")
        self.minsize(1000, 820)
        self.configure(bg=BG)
        self.configure_styles()
        self.report_callback_exception = self.callback_error
        self.show_login()

    def configure_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background=BG)
        style.configure("Card.TFrame", background="white")
        style.configure("TLabel", background=BG, foreground=INK, font=("DejaVu Sans", 10))
        style.configure("Muted.TLabel", foreground=MUTED)
        style.configure("Title.TLabel", font=("DejaVu Sans", 25, "bold"))
        style.configure("Heading.TLabel", font=("DejaVu Sans", 13, "bold"))
        style.configure("Card.TLabel", background="white")
        style.configure("Metric.TLabel", background="white", foreground=BLUE, font=("DejaVu Sans", 26, "bold"))
        style.configure("TButton", padding=(14, 9), foreground=INK, background="#e6ebf3", borderwidth=0)
        style.map("TButton", background=[("active", "#d6dfec")])
        style.configure("Primary.TButton", foreground="white", background=BLUE)
        style.map("Primary.TButton", background=[("active", "#2546bf")])
        style.configure("TEntry", padding=8, bordercolor="#d9e0ec")
        style.configure("TCombobox", padding=7)
        style.configure(
            "Treeview", rowheight=36, borderwidth=0, background="white", fieldbackground="white", foreground=INK
        )
        style.configure(
            "Treeview.Heading", padding=(8, 11), background="#e8edf5", foreground=MUTED, font=("DejaVu Sans", 9, "bold")
        )
        style.map("Treeview", background=[("selected", "#dce5ff")], foreground=[("selected", INK)])
        style.configure("TNotebook", background=BG, borderwidth=0, tabmargins=(0, 0, 0, 14))
        style.configure("TNotebook.Tab", padding=(16, 12), background="#e6ebf3", foreground=MUTED)
        style.map("TNotebook.Tab", background=[("selected", "white")], foreground=[("selected", BLUE)])

    def callback_error(self, exc_type, value, traceback):
        logging.error("Unhandled interface error", exc_info=(exc_type, value, traceback))
        messagebox.showerror(
            "Something went wrong",
            "The action could not be completed. Check the application log for details.",
            parent=self,
        )

    def clear(self):
        for widget in self.winfo_children():
            widget.destroy()

    def run_action(self, action, refresh=None, success=None):
        try:
            action()
        except (ValueError, PermissionError) as exc:
            messagebox.showerror("Please check your input", str(exc), parent=self)
            return False
        except Exception:
            logging.exception("Database action failed")
            messagebox.showerror(
                "Action unsuccessful",
                "The change could not be saved. Check the database connection and try again.",
                parent=self,
            )
            return False
        if refresh:
            refresh()
        if success:
            messagebox.showinfo("Done", success, parent=self)
        return True

    def show_login(self):
        self.clear()
        self.service.logout()
        self.unbind("<Return>")
        shell = ttk.Frame(self, padding=50)
        shell.pack(fill="both", expand=True)
        shell.columnconfigure(0, weight=1)
        shell.columnconfigure(1, weight=1)
        shell.rowconfigure(0, weight=1)
        brand = tk.Frame(shell, bg=NAVY, padx=40, pady=40)
        brand.grid(row=0, column=0, sticky="nsew", padx=(0, 36))
        tk.Label(brand, text="G / GRADEBOOK", bg=NAVY, fg="#9eb5ff", font=("DejaVu Sans", 12, "bold")).pack(anchor="w")
        tk.Label(
            brand,
            text="A clearer view\nof every\nschool day.",
            justify="left",
            bg=NAVY,
            fg="white",
            font=("DejaVu Sans", 32, "bold"),
        ).pack(anchor="w", pady=(75, 28))
        tk.Label(brand, text="Learn. Teach. Stay connected.", bg=NAVY, fg="#b5c4da", font=("DejaVu Sans", 12)).pack(
            anchor="w"
        )
        tk.Label(
            brand, text="GRADES   /   ATTENDANCE   /   TIMETABLE", bg=NAVY, fg="#8fa6c5", font=("DejaVu Sans", 9)
        ).pack(anchor="w", side="bottom")
        form = ttk.Frame(shell, padding=(15, 60))
        form.grid(row=0, column=1, sticky="nsew")
        ttk.Label(form, text="Welcome back", style="Title.TLabel").pack(anchor="w")
        ttk.Label(form, text="Sign in to your school workspace.", style="Muted.TLabel").pack(anchor="w", pady=(10, 30))
        email = self.field(form, "Email address")
        password = self.field(form, "Password", secret=True)
        error = ttk.Label(form, text="", foreground="#b42336", wraplength=350)
        error.pack(anchor="w", pady=8)

        def login(event=None):
            try:
                self.service.login(email.get(), password.get())
                self.unbind("<Return>")
                self.show_workspace()
            except (ValueError, PermissionError) as exc:
                error.configure(text=str(exc))
                password.delete(0, "end")
                password.focus_set()
            except Exception:
                logging.exception("Sign-in failed")
                error.configure(text="Unable to connect. Check your database settings.")

        ttk.Button(form, text="Sign in  →", style="Primary.TButton", command=login).pack(fill="x", pady=(0, 20))
        self.bind("<Return>", login)
        if self.demo:
            ttk.Label(form, text="EXPLORE THE DEMO", style="Heading.TLabel").pack(anchor="w", pady=(14, 10))
            ttk.Label(
                form, text="Choose a role to fill in the demo credentials.", style="Muted.TLabel", wraplength=350
            ).pack(anchor="w")
            roles = ttk.Frame(form)
            roles.pack(fill="x", pady=12)

            def fill(role):
                email.delete(0, "end")
                email.insert(0, f"{role}@gradebook.demo")
                password.delete(0, "end")
                password.insert(0, DEMO_PASSWORD)
                error.configure(text="")

            for label, role in (("Student", "student"), ("Teacher", "teacher"), ("Headteacher", "admin")):
                ttk.Button(roles, text=label, command=lambda r=role: fill(r)).pack(side="left", padx=(0, 5))
            fill("student")
            ttk.Label(
                form,
                text="Fictional data · Changes stay in your local demo database",
                style="Muted.TLabel",
                wraplength=350,
            ).pack(anchor="w", pady=8)
        else:
            ttk.Label(form, text="Need an account? Contact your headteacher.", style="Muted.TLabel").pack(anchor="w")
        email.focus_set()

    def field(self, parent, label, values=None, secret=False, default=""):
        ttk.Label(parent, text=label).pack(anchor="w", pady=(10, 5))
        if values is not None:
            entry = ttk.Combobox(parent, values=values, state="readonly")
            if default:
                entry.set(default)
            elif values:
                entry.current(0)
        else:
            entry = ttk.Entry(parent, show="•" if secret else "")
            entry.insert(0, default)
        entry.pack(fill="x")
        return entry

    def show_workspace(self):
        self.clear()
        user = self.service.user
        header = tk.Frame(self, bg=NAVY, padx=28, pady=19)
        header.pack(fill="x")
        tk.Label(header, text="G / GRADEBOOK", bg=NAVY, fg="white", font=("DejaVu Sans", 15, "bold")).pack(side="left")
        ttk.Button(header, text="Sign out", command=self.show_login).pack(side="right")
        tk.Label(
            header,
            text=f"{user['first_name']} {user['last_name']}  /  {user['role'].title()}"
            + ("  ·  DEMO" if self.demo else ""),
            bg=NAVY,
            fg="#b9c8df",
        ).pack(side="right", padx=22)
        self.content = ttk.Frame(self, padding=(28, 22))
        self.content.pack(fill="both", expand=True)
        self.notebook = ttk.Notebook(self.content)
        self.notebook.pack(fill="both", expand=True)
        pages = [
            ("Overview", self.dashboard),
            ("Timetable", self.schedule_page),
            ("Grades", self.grades_page),
            ("Attendance", self.attendance_page),
            ("Messages", self.messages_page),
            ("Account", self.account_page),
        ]
        if user["role"] == "HEADTEACHER":
            pages.append(("Administration", self.admin_page))
        for name, builder in pages:
            page = ttk.Frame(self.notebook, padding=16)
            self.notebook.add(page, text=name)
            builder(page)
        ttk.Label(self, text="School, connected.     •     Gradebook 2.0", style="Muted.TLabel", padding=(28, 8)).pack(
            anchor="w"
        )

    def heading(self, frame, title, description):
        ttk.Label(frame, text=title, style="Title.TLabel").pack(anchor="w")
        ttk.Label(frame, text=description, style="Muted.TLabel", wraplength=950).pack(anchor="w", pady=(8, 20))

    def toolbar(self, frame):
        toolbar = ttk.Frame(frame)
        toolbar.pack(fill="x", pady=(0, 12))
        return toolbar

    def table(self, frame, columns, rows, height=10, expand=True):
        container = ttk.Frame(frame)
        container.pack(fill="both", expand=expand)
        tree = ttk.Treeview(
            container,
            columns=[key for key, title, width in columns],
            show="headings",
            height=height,
            selectmode="browse",
        )
        for key, title, width in columns:
            tree.heading(key, text=title, command=lambda k=key: self.sort_table(tree, k))
            tree.column(key, width=width, minwidth=45, anchor="w")
        for index, row in enumerate(rows):
            tree.insert(
                "",
                "end",
                iid=str(index),
                values=[row.get(key, "") if row.get(key) is not None else "—" for key, _, _ in columns],
                tags=("even" if index % 2 == 0 else "odd",),
            )
        tree.tag_configure("odd", background="#f7f9fc")
        vertical = ttk.Scrollbar(container, orient="vertical", command=tree.yview)
        horizontal = ttk.Scrollbar(container, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vertical.set, xscrollcommand=horizontal.set)
        tree.grid(row=0, column=0, sticky="nsew")
        vertical.grid(row=0, column=1, sticky="ns")
        horizontal.grid(row=1, column=0, sticky="ew")
        container.columnconfigure(0, weight=1)
        container.rowconfigure(0, weight=1)
        if not rows:
            ttk.Label(container, text="No records yet.", style="Muted.TLabel").grid(
                row=2, column=0, sticky="w", pady=10
            )
        return tree

    def sort_table(self, tree, key, reverse=False):
        items = [(tree.set(item, key), item) for item in tree.get_children()]
        try:
            items = [(float(value), item) for value, item in items]
        except ValueError:
            pass
        for position, (_, item) in enumerate(sorted(items, reverse=reverse)):
            tree.move(item, "", position)
        tree.heading(key, command=lambda: self.sort_table(tree, key, not reverse))

    def reload(self, frame, builder):
        for widget in frame.winfo_children():
            widget.destroy()
        builder(frame)

    def selected(self, tree, rows):
        if not tree.selection():
            raise ValueError("Select a row first.")
        return rows[int(tree.selection()[0])]

    def dialog(self, title, fields, action, refresh):
        top = tk.Toplevel(self)
        top.title(title)
        top.geometry("510x680")
        top.minsize(450, 400)
        top.transient(self)
        top.grab_set()
        canvas = tk.Canvas(top, bg=BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(top, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(fill="both", expand=True)
        canvas.configure(yscrollcommand=scrollbar.set)
        body = ttk.Frame(canvas, padding=24)
        window = canvas.create_window((0, 0), window=body, anchor="nw")
        canvas.bind("<Configure>", lambda e: canvas.itemconfigure(window, width=e.width))
        body.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        ttk.Label(body, text=title, style="Heading.TLabel").pack(anchor="w", pady=(0, 8))
        entries = {}
        for key, label, options in fields:
            entries[key] = self.field(body, label, **options)
        error = ttk.Label(body, text="", foreground="#b42336", wraplength=410)
        error.pack(anchor="w", pady=12)

        def save():
            try:
                action({key: entry.get() for key, entry in entries.items()})
            except (ValueError, PermissionError) as exc:
                error.configure(text=str(exc))
                return
            except Exception:
                logging.exception("Form submission failed")
                error.configure(text="Unable to save. Check your database connection and try again.")
                return
            top.destroy()
            refresh()

        buttons = ttk.Frame(body)
        buttons.pack(fill="x", pady=10)
        ttk.Button(buttons, text="Save", style="Primary.TButton", command=save).pack(side="left")
        ttk.Button(buttons, text="Cancel", command=top.destroy).pack(side="left", padx=8)
        return top

    def dashboard(self, frame):
        user = self.service.user
        self.heading(
            frame,
            f"Good to see you, {user['first_name']}.",
            f"{date.today():%A, %d %B %Y}   /   Your school day at a glance",
        )
        toolbar = self.toolbar(frame)
        ttk.Button(toolbar, text="Refresh overview", command=lambda: self.reload(frame, self.dashboard)).pack(
            side="right"
        )
        lessons = self.service.lessons()
        today_lessons = [row for row in lessons if row["weekday"] == date.today().weekday()]
        grades = self.service.grades()
        attendance = self.service.attendance()
        average = weighted_average(grades)
        rate = sum(row["status"] != "ABSENT" for row in attendance) / len(attendance) * 100 if attendance else None
        metrics = [
            ("LESSONS TODAY", str(len(today_lessons))),
            (
                "WEIGHTED AVERAGE" if user["role"] == "STUDENT" else "RECORDED GRADES",
                f"{average:.2f} / 6"
                if average is not None and user["role"] == "STUDENT"
                else "—"
                if user["role"] == "STUDENT"
                else str(len(grades)),
            ),
            ("ATTENDANCE", f"{rate:.0f}%" if rate is not None else "—"),
            ("RECEIVED MESSAGES", str(len(self.service.messages()))),
        ]
        cards = ttk.Frame(frame)
        cards.pack(fill="x", pady=(0, 24))
        for index, (label, value) in enumerate(metrics):
            card = ttk.Frame(cards, style="Card.TFrame", padding=20)
            card.grid(row=0, column=index, sticky="nsew", padx=(0, 12 if index < 3 else 0))
            cards.columnconfigure(index, weight=1)
            ttk.Label(card, text=label, style="Card.TLabel", font=("DejaVu Sans", 9)).pack(anchor="w")
            ttk.Label(card, text=value, style="Metric.TLabel").pack(anchor="w", pady=(12, 0))
        ttk.Label(frame, text="Today's timetable", style="Heading.TLabel").pack(anchor="w", pady=(0, 12))
        self.table(
            frame,
            [
                ("start_time", "START", 90),
                ("end_time", "END", 90),
                ("subject", "SUBJECT", 220),
                ("class_name", "CLASS", 80),
                ("room", "ROOM", 140),
            ],
            today_lessons,
            height=3,
            expand=False,
        )
        ttk.Label(frame, text="Latest message", style="Heading.TLabel").pack(anchor="w", pady=(20, 10))
        messages = self.service.messages()
        if messages:
            latest = messages[0]
            ttk.Label(frame, text=latest["subject"]).pack(anchor="w")
            ttk.Label(frame, text=f"From {latest['sender']} · {latest['sent_at']}", style="Muted.TLabel").pack(
                anchor="w", pady=5
            )
        else:
            ttk.Label(frame, text="Your inbox is empty.", style="Muted.TLabel").pack(anchor="w")

    def schedule_page(self, frame):
        self.heading(frame, "Your week, organized.", "Monday to Friday · Select column headers to sort the timetable.")
        toolbar = self.toolbar(frame)
        ttk.Button(toolbar, text="Refresh", command=lambda: self.reload(frame, self.schedule_page)).pack(side="right")
        rows = self.service.lessons()
        for row in rows:
            row["day"] = DAYS[row["weekday"]]
            row["teacher"] = f"{row['first_name']} {row['last_name']}"
        self.table(
            frame,
            [
                ("day", "DAY", 110),
                ("start_time", "START", 75),
                ("end_time", "END", 75),
                ("subject", "SUBJECT", 180),
                ("class_name", "CLASS", 70),
                ("teacher", "TEACHER", 180),
                ("room", "ROOM", 120),
            ],
            rows,
        )

    def grades_page(self, frame):
        self.heading(
            frame,
            "Progress, made visible.",
            "Grades use a 1–6 scale with weights from 1 to 10. Teachers see the grades they recorded.",
        )
        toolbar = self.toolbar(frame)
        rows = self.service.grades()

        def refresh():
            return self.reload(frame, self.grades_page)

        if self.service.user["role"] != "STUDENT":
            ttk.Button(
                toolbar, text="+ Add grade", style="Primary.TButton", command=lambda: self.grade_dialog(refresh)
            ).pack(side="left")
            tree_holder = {}

            def remove():
                def action():
                    row = self.selected(tree_holder["tree"], rows)
                    if messagebox.askyesno("Remove grade", "Permanently remove the selected grade?", parent=self):
                        self.service.delete_grade(row["id"])

                self.run_action(action, refresh)

            ttk.Button(toolbar, text="Remove selected", command=remove).pack(side="left", padx=8)
        ttk.Button(toolbar, text="Refresh", command=refresh).pack(side="right")
        for row in rows:
            row["student"] = f"{row['first_name']} {row['last_name']}"
        tree = self.table(
            frame,
            [
                ("student", "STUDENT", 180),
                ("class_name", "CLASS", 70),
                ("subject", "SUBJECT", 200),
                ("grade", "GRADE", 80),
                ("weight", "WEIGHT", 80),
                ("date", "DATE", 120),
            ],
            rows,
        )
        if self.service.user["role"] != "STUDENT":
            tree_holder["tree"] = tree
        else:
            subjects = sorted({row["subject"] for row in rows})
            summary = "   ·   ".join(
                f"{subject}: {weighted_average([r for r in rows if r['subject'] == subject]):.2f}"
                for subject in subjects
            )
            ttk.Label(
                frame, text="Weighted averages   " + (summary or "No grades yet"), wraplength=950, style="Muted.TLabel"
            ).pack(anchor="w", pady=15)

    def student_choices(self):
        return {
            f"#{s['id']} · {s['first_name']} {s['last_name']} / {s['class_name']}": s["id"]
            for s in self.service.students()
        }

    def grade_dialog(self, refresh):
        students = self.student_choices()
        subjects = sorted({lesson["subject"] for lesson in self.service.lessons()})

        def save(values):
            if values["student"] not in students:
                raise ValueError("Choose a student. Add students and lessons in Administration first.")
            self.service.add_grade(
                students[values["student"]], values["subject"], values["grade"], values["weight"], values["date"]
            )

        self.dialog(
            "Add grade",
            [
                ("student", "Student", {"values": list(students)}),
                ("subject", "Subject", {"values": subjects}),
                ("grade", "Grade (1–6)", {}),
                ("weight", "Weight (1–10)", {"default": "1"}),
                ("date", "Date (YYYY-MM-DD)", {"default": date.today().isoformat()}),
            ],
            save,
            refresh,
        )

    def attendance_page(self, frame):
        self.heading(
            frame,
            "Every lesson counts.",
            "Present and Late count toward attendance. Saving the same student, lesson, and date updates the existing record.",
        )
        toolbar = self.toolbar(frame)

        def refresh():
            return self.reload(frame, self.attendance_page)

        rows = self.service.attendance()
        if self.service.user["role"] != "STUDENT":
            ttk.Button(
                toolbar,
                text="+ Record attendance",
                style="Primary.TButton",
                command=lambda: self.attendance_dialog(refresh),
            ).pack(side="left")

            def remove():
                def action():
                    row = self.selected(tree, rows)
                    if messagebox.askyesno(
                        "Remove attendance", "Permanently remove the selected attendance record?", parent=self
                    ):
                        self.service.delete_attendance(row["id"])

                self.run_action(action, refresh)

            ttk.Button(toolbar, text="Remove selected", command=remove).pack(side="left", padx=8)
        ttk.Button(toolbar, text="Refresh", command=refresh).pack(side="right")
        for row in rows:
            row["student"] = f"{row['first_name']} {row['last_name']}"
        tree = self.table(
            frame,
            [
                ("date", "DATE", 110),
                ("start_time", "TIME", 75),
                ("student", "STUDENT", 180),
                ("class_name", "CLASS", 65),
                ("subject", "SUBJECT", 200),
                ("status", "STATUS", 110),
            ],
            rows,
        )

    def attendance_dialog(self, refresh):
        students = self.student_choices()
        lessons = {
            f"#{lesson['id']} · {DAYS[lesson['weekday']]} {lesson['start_time']} / {lesson['class_name']} / {lesson['subject']}": lesson[
                "id"
            ]
            for lesson in self.service.lessons()
        }

        def save(values):
            if values["student"] not in students or values["lesson"] not in lessons:
                raise ValueError("Choose a student and a lesson.")
            self.service.mark_attendance(
                students[values["student"]], lessons[values["lesson"]], values["date"], values["status"]
            )

        self.dialog(
            "Record attendance",
            [
                ("student", "Student", {"values": list(students)}),
                ("lesson", "Lesson", {"values": list(lessons)}),
                ("date", "Date (must match the lesson's weekday)", {"default": date.today().isoformat()}),
                ("status", "Status", {"values": STATUSES}),
            ],
            save,
            refresh,
        )

    def messages_page(self, frame, sent=False):
        self.heading(
            frame,
            "Keep the conversation going.",
            "Send a message using the recipient's school email address. Double-click a message to read it.",
        )

        def refresh():
            return self.reload(frame, lambda f: self.messages_page(f, sent))

        toolbar = self.toolbar(frame)
        ttk.Button(
            toolbar, text="+ New message", style="Primary.TButton", command=lambda: self.compose_message(refresh)
        ).pack(side="left")
        ttk.Button(toolbar, text="Inbox", command=lambda: self.reload(frame, self.messages_page)).pack(
            side="left", padx=8
        )
        ttk.Button(
            toolbar, text="Sent", command=lambda: self.reload(frame, lambda f: self.messages_page(f, True))
        ).pack(side="left")
        ttk.Button(toolbar, text="Refresh", command=refresh).pack(side="right")
        ttk.Label(frame, text="Sent messages" if sent else "Inbox", style="Heading.TLabel").pack(
            anchor="w", pady=(0, 12)
        )
        rows = self.service.messages(sent=sent)
        tree = self.table(
            frame,
            [
                ("receiver" if sent else "sender", "TO" if sent else "FROM", 250),
                ("subject", "SUBJECT", 400),
                ("sent_at", "SENT", 170),
            ],
            rows,
        )

        def read(event=None):
            if not tree.selection():
                return
            row = self.selected(tree, rows)
            top = tk.Toplevel(self)
            top.title(row["subject"])
            top.geometry("650x460")
            body = ttk.Frame(top, padding=24)
            body.pack(fill="both", expand=True)
            ttk.Label(body, text=row["subject"], style="Heading.TLabel", wraplength=580).pack(anchor="w")
            ttk.Label(
                body, text=f"From: {row['sender']}\nTo: {row['receiver']}\n{row['sent_at']}", style="Muted.TLabel"
            ).pack(anchor="w", pady=15)
            text = tk.Text(body, wrap="word", borderwidth=0, padx=12, pady=12)
            text.pack(fill="both", expand=True)
            text.insert("1.0", row["body"])
            text.configure(state="disabled")

        tree.bind("<Double-1>", read)
        tree.bind("<Return>", read)
        ttk.Button(frame, text="Read selected message", command=read).pack(anchor="w", pady=12)

    def compose_message(self, refresh):
        top = tk.Toplevel(self)
        top.title("New message")
        top.geometry("600x600")
        top.transient(self)
        top.grab_set()
        body = ttk.Frame(top, padding=24)
        body.pack(fill="both", expand=True)
        ttk.Label(body, text="New message", style="Heading.TLabel").pack(anchor="w")
        receiver = self.field(body, "Recipient email")
        subject = self.field(body, "Subject")
        ttk.Label(body, text="Message").pack(anchor="w", pady=(15, 5))
        text = tk.Text(body, height=10, wrap="word", borderwidth=1, relief="solid", padx=10, pady=10)
        text.pack(fill="both", expand=True)

        def send():
            if self.run_action(
                lambda: self.service.send_message(receiver.get(), subject.get(), text.get("1.0", "end-1c"))
            ):
                top.destroy()
                refresh()

        ttk.Button(body, text="Send message", style="Primary.TButton", command=send).pack(anchor="w", pady=15)

    def account_page(self, frame):
        user = self.service.user
        self.heading(
            frame, "Your account.", "Keep your sign-in details up to date. Use a password with at least 10 characters."
        )
        ttk.Label(frame, text=f"{user['first_name']} {user['last_name']}", style="Heading.TLabel").pack(anchor="w")
        ttk.Label(
            frame,
            text=f"{user['email']}   /   {user['role'].title()}"
            + (f"   /   Class {user['class_name']}" if user["class_name"] else ""),
            style="Muted.TLabel",
        ).pack(anchor="w", pady=10)
        form = ttk.Frame(frame, width=440)
        form.pack(anchor="w", pady=15)
        old = self.field(form, "Current password", secret=True)
        new = self.field(form, "New password", secret=True)
        confirmation = self.field(form, "Confirm new password", secret=True)

        def change():
            def action():
                if new.get() != confirmation.get():
                    raise ValueError("The new passwords do not match.")
                self.service.change_password(old.get(), new.get())

            if self.run_action(action, success="Your password has been updated."):
                for entry in (old, new, confirmation):
                    entry.delete(0, "end")

        ttk.Button(form, text="Update password", style="Primary.TButton", command=change).pack(anchor="w", pady=18)

    def admin_page(self, frame):
        self.heading(
            frame,
            "A well-run school starts here.",
            "Manage accounts and the weekly timetable. Deactivation preserves academic records and message history.",
        )
        toolbar = self.toolbar(frame)

        def refresh():
            return self.reload(frame, self.admin_page)

        rows = self.service.users()
        ttk.Button(toolbar, text="+ Add user", style="Primary.TButton", command=lambda: self.user_dialog(refresh)).pack(
            side="left"
        )

        def deactivate():
            def action():
                row = self.selected(tree, rows)
                if messagebox.askyesno(
                    "Deactivate account",
                    f"Deactivate {row['email']}? They will no longer be able to sign in.",
                    parent=self,
                ):
                    self.service.deactivate_user(row["id"])

            self.run_action(action, refresh)

        def reset():
            def action():
                row = self.selected(tree, rows)
                self.dialog(
                    "Reset password",
                    [
                        ("password", "New password (at least 10 characters)", {"secret": True}),
                        ("confirm", "Confirm new password", {"secret": True}),
                    ],
                    lambda v: save_reset(row, v),
                    refresh,
                )

            self.run_action(action)

        def save_reset(row, values):
            if values["password"] != values["confirm"]:
                raise ValueError("The passwords do not match.")
            self.service.reset_password(row["id"], values["password"])

        ttk.Button(toolbar, text="Deactivate", command=deactivate).pack(side="left", padx=8)
        ttk.Button(toolbar, text="Reset password", command=reset).pack(side="left")
        ttk.Button(toolbar, text="Manage lessons", command=self.lesson_manager).pack(side="right", padx=8)
        ttk.Button(toolbar, text="Refresh", command=refresh).pack(side="right")
        for row in rows:
            row["status"] = "Active" if row["active"] else "Inactive"
        tree = self.table(
            frame,
            [
                ("id", "ID", 45),
                ("first_name", "FIRST NAME", 110),
                ("last_name", "LAST NAME", 110),
                ("email", "EMAIL", 230),
                ("role", "ROLE", 120),
                ("class_name", "CLASS", 65),
                ("status", "STATUS", 75),
            ],
            rows,
        )

    def user_dialog(self, refresh):
        def save(values):
            if values["password"] != values["confirmation"]:
                raise ValueError("The passwords do not match.")
            self.service.create_user(
                values["first"], values["last"], values["email"], values["password"], values["role"], values["class"]
            )

        self.dialog(
            "Add school account",
            [
                ("first", "First name", {}),
                ("last", "Last name", {}),
                ("email", "Email address", {}),
                ("role", "Role", {"values": ROLES}),
                ("class", "Class (required for students only)", {}),
                ("password", "Password (at least 10 characters)", {"secret": True}),
                ("confirmation", "Confirm password", {"secret": True}),
            ],
            save,
            refresh,
        )

    def lesson_manager(self):
        top = tk.Toplevel(self)
        top.title("Manage lessons")
        top.geometry("1050x650")
        frame = ttk.Frame(top, padding=24)
        frame.pack(fill="both", expand=True)

        def build():
            for widget in frame.winfo_children():
                widget.destroy()
            self.heading(
                frame,
                "Weekly timetable",
                "Conflicts in teacher, class, or room are rejected. Lessons with attendance records are retained.",
            )
            toolbar = self.toolbar(frame)
            ttk.Button(
                toolbar, text="+ Add lesson", style="Primary.TButton", command=lambda: self.lesson_dialog(build)
            ).pack(side="left")
            rows = self.service.lessons()
            for row in rows:
                row["day"] = DAYS[row["weekday"]]
                row["teacher"] = f"{row['first_name']} {row['last_name']}"

            def remove():
                def action():
                    row = self.selected(tree, rows)
                    if messagebox.askyesno("Remove lesson", "Permanently remove this lesson?", parent=top):
                        self.service.delete_lesson(row["id"])

                self.run_action(action, build)

            ttk.Button(toolbar, text="Remove selected", command=remove).pack(side="left", padx=8)
            tree = self.table(
                frame,
                [
                    ("day", "DAY", 100),
                    ("start_time", "START", 65),
                    ("end_time", "END", 65),
                    ("subject", "SUBJECT", 180),
                    ("class_name", "CLASS", 60),
                    ("teacher", "TEACHER", 160),
                    ("room", "ROOM", 110),
                ],
                rows,
            )

        build()

    def lesson_dialog(self, refresh):
        teachers = {
            f"#{u['id']} · {u['first_name']} {u['last_name']}": u["id"]
            for u in self.service.users()
            if u["role"] in ("TEACHER", "HEADTEACHER") and u["active"]
        }

        def save(values):
            if values["teacher"] not in teachers or values["day"] not in DAYS:
                raise ValueError("Choose a teacher and a weekday.")
            self.service.add_lesson(
                values["subject"],
                values["class"],
                teachers[values["teacher"]],
                DAYS.index(values["day"]),
                values["start"],
                values["end"],
                values["room"],
            )

        self.dialog(
            "Add lesson",
            [
                ("subject", "Subject", {}),
                ("class", "Class", {}),
                ("teacher", "Teacher", {"values": list(teachers)}),
                ("day", "Weekday", {"values": DAYS}),
                ("start", "Start time (HH:MM)", {"default": "09:00"}),
                ("end", "End time (HH:MM)", {"default": "09:45"}),
                ("room", "Room", {}),
            ],
            save,
            refresh,
        )
