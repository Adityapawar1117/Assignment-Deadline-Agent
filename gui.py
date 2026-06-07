"""
Assignment Deadline Management Agent — Tkinter GUI
===================================================
Run: python gui.py
Requires: Python 3.8+  (no external packages needed)
"""

import tkinter as tk
from tkinter import ttk, messagebox, font as tkfont
from datetime import date, timedelta
from agent import Assignment, HeuristicScheduler, UtilityFunction

# ─── Color Palette ──────────────────────────────────────────────────────────
C = {
    "bg":        "#0f1117",
    "surface":   "#1a1d27",
    "surface2":  "#232736",
    "border":    "#2e3347",
    "accent":    "#4f8ef7",
    "accent2":   "#f7694f",
    "accent3":   "#3ecf8e",
    "amber":     "#f7c14f",
    "text":      "#e8eaf0",
    "muted":     "#7c8299",
    "critical":  "#f76f4f",
    "high":      "#f7c14f",
    "medium":    "#4f8ef7",
    "low":       "#3ecf8e",
    "overdue":   "#e24b4a",
}

DIFF_LABELS = {1: "Easy", 2: "Medium", 3: "Hard"}
TYPES       = ["Report", "Coding", "Presentation", "Problem Set", "Research", "Lab Work"]
URGENCY_COLORS = {
    "OVERDUE":  C["overdue"],
    "CRITICAL": C["critical"],
    "HIGH":     C["high"],
    "MEDIUM":   C["medium"],
    "LOW":      C["low"],
}

_id_counter = [1]

def new_id():
    i = _id_counter[0]
    _id_counter[0] += 1
    return i

def sample_data():
    today = date.today()
    return [
        Assignment(new_id(), "DBMS",           "ER Diagram Project",          today+timedelta(2), 4.0, 2, "Report"),
        Assignment(new_id(), "Machine Learning","Neural Net Implementation",   today+timedelta(3), 8.0, 3, "Coding"),
        Assignment(new_id(), "OS",              "CPU Scheduling Algorithm",    today+timedelta(3), 5.0, 3, "Coding"),
        Assignment(new_id(), "Mathematics",     "Linear Algebra Problem Set",  today+timedelta(5), 3.0, 2, "Problem Set"),
        Assignment(new_id(), "Computer Networks","TCP/IP Presentation",        today+timedelta(7), 2.0, 1, "Presentation"),
    ]


# ─────────────────────────────────────────────────────────────────────────────
#  MAIN APP WINDOW
# ─────────────────────────────────────────────────────────────────────────────

class AgentApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Assignment Deadline Management Agent")
        self.geometry("1150x720")
        self.minsize(900, 600)
        self.configure(bg=C["bg"])

        self.assignments: list[Assignment] = sample_data()
        self.scheduler   = None
        self.opt_ran     = False

        self._setup_styles()
        self._build_ui()
        self.refresh_all()

    # ── Styles ──────────────────────────────────────────────────────────────
    def _setup_styles(self):
        self.style = ttk.Style(self)
        self.style.theme_use("clam")
        self.style.configure("TNotebook", background=C["bg"], borderwidth=0)
        self.style.configure("TNotebook.Tab",
            background=C["surface"], foreground=C["muted"],
            padding=[16, 8], font=("Courier", 10, "bold"), borderwidth=0)
        self.style.map("TNotebook.Tab",
            background=[("selected", C["surface2"])],
            foreground=[("selected", C["accent"])])
        self.style.configure("TFrame", background=C["bg"])
        self.style.configure("Dark.TFrame", background=C["surface"])
        self.style.configure("Treeview",
            background=C["surface"], foreground=C["text"],
            fieldbackground=C["surface"], rowheight=30,
            font=("Courier", 10))
        self.style.configure("Treeview.Heading",
            background=C["surface2"], foreground=C["accent"],
            font=("Courier", 10, "bold"), relief="flat")
        self.style.map("Treeview", background=[("selected", C["accent"])])
        self.style.configure("TScrollbar",
            background=C["surface2"], troughcolor=C["surface"],
            arrowcolor=C["muted"])

    # ── Main UI Structure ────────────────────────────────────────────────────
    def _build_ui(self):
        # Header
        hdr = tk.Frame(self, bg=C["surface"], height=56)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text="◈  ASSIGNMENT DEADLINE MANAGEMENT AGENT",
                 bg=C["surface"], fg=C["accent"],
                 font=("Courier", 13, "bold")).pack(side="left", padx=20, pady=14)
        tk.Label(hdr, text="Utility-Based  ·  Heuristic Search  ·  Scheduling",
                 bg=C["surface"], fg=C["muted"],
                 font=("Courier", 9)).pack(side="right", padx=20)

        sep = tk.Frame(self, bg=C["border"], height=1)
        sep.pack(fill="x")

        # Notebook
        self.nb = ttk.Notebook(self)
        self.nb.pack(fill="both", expand=True, padx=12, pady=10)

        self.tab_dash   = ttk.Frame(self.nb)
        self.tab_add    = ttk.Frame(self.nb)
        self.tab_opt    = ttk.Frame(self.nb)
        self.tab_about  = ttk.Frame(self.nb)

        self.nb.add(self.tab_dash,  text="  Dashboard  ")
        self.nb.add(self.tab_add,   text="  Add Assignment  ")
        self.nb.add(self.tab_opt,   text="  Optimize  ")
        self.nb.add(self.tab_about, text="  About Agent  ")

        self._build_dashboard()
        self._build_add_form()
        self._build_optimize()
        self._build_about()

    # ── Helper Widgets ───────────────────────────────────────────────────────
    def _label(self, parent, text, **kw):
        defaults = dict(bg=C["bg"], fg=C["text"], font=("Courier", 10))
        defaults.update(kw)
        return tk.Label(parent, text=text, **defaults)

    def _card(self, parent, **kw):
        f = tk.Frame(parent, bg=C["surface"], bd=0, highlightthickness=1,
                     highlightbackground=C["border"], **kw)
        return f

    def _section(self, parent, title):
        tk.Label(parent, text=title.upper(),
                 bg=C["bg"], fg=C["muted"],
                 font=("Courier", 9, "bold")).pack(anchor="w", padx=2, pady=(10, 3))

    def _btn(self, parent, text, cmd, color=None, **kw):
        c = color or C["accent"]
        b = tk.Button(parent, text=text, command=cmd,
                      bg=c, fg="#fff", activebackground=C["border"],
                      activeforeground=C["text"], relief="flat",
                      font=("Courier", 10, "bold"), cursor="hand2",
                      padx=14, pady=6, bd=0, **kw)
        return b

    # ── DASHBOARD TAB ────────────────────────────────────────────────────────
    def _build_dashboard(self):
        p = self.tab_dash
        p.configure(style="TFrame")

        # ── Stat cards row
        self.stat_frame = tk.Frame(p, bg=C["bg"])
        self.stat_frame.pack(fill="x", padx=10, pady=(12, 6))

        # ── Split pane
        split = tk.Frame(p, bg=C["bg"])
        split.pack(fill="both", expand=True, padx=10, pady=4)

        # Left: assignment list
        left = self._card(split)
        left.pack(side="left", fill="both", expand=True, padx=(0, 6))
        tk.Label(left, text="ASSIGNMENT QUEUE  (sorted by priority)",
                 bg=C["surface"], fg=C["accent"],
                 font=("Courier", 10, "bold")).pack(anchor="w", padx=12, pady=(10, 4))

        cols = ("Subject", "Title", "Deadline", "Hrs", "Diff", "Urgency", "Score")
        self.tree = ttk.Treeview(left, columns=cols, show="headings", selectmode="browse")
        widths    = [90, 200, 90, 45, 65, 80, 60]
        for col, w in zip(cols, widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w, anchor="center" if col not in ("Title","Subject") else "w")
        ys = ttk.Scrollbar(left, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=ys.set)
        self.tree.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=(0, 10))
        ys.pack(side="left", fill="y", pady=(0, 10), padx=(0, 8))

        btn_row = tk.Frame(left, bg=C["surface"])
        btn_row.pack(fill="x", padx=10, pady=(0, 10))
        self._btn(btn_row, "✓ Mark Done",   self._mark_done,   C["accent3"]).pack(side="left", padx=(0, 6))
        self._btn(btn_row, "✕ Delete",      self._delete_item, C["overdue"]).pack(side="left")

        # Right: workload forecast
        right = self._card(split, width=260)
        right.pack(side="right", fill="y")
        right.pack_propagate(False)
        tk.Label(right, text="7-DAY WORKLOAD FORECAST",
                 bg=C["surface"], fg=C["accent"],
                 font=("Courier", 10, "bold")).pack(anchor="w", padx=12, pady=(10, 6))
        self.forecast_frame = tk.Frame(right, bg=C["surface"])
        self.forecast_frame.pack(fill="both", expand=True, padx=12, pady=(0, 10))

    # ── ADD FORM TAB ─────────────────────────────────────────────────────────
    def _build_add_form(self):
        p = self.tab_add
        p.configure(style="TFrame")

        card = self._card(p)
        card.place(relx=0.5, rely=0.5, anchor="center", width=480)

        tk.Label(card, text="NEW ASSIGNMENT", bg=C["surface"], fg=C["accent"],
                 font=("Courier", 12, "bold")).grid(row=0, column=0, columnspan=2,
                 sticky="w", padx=20, pady=(18, 8))

        fields = [
            ("Subject",          "entry",  None),
            ("Title",            "entry",  None),
            ("Deadline (YYYY-MM-DD)", "entry", None),
            ("Estimated Hours",  "entry",  None),
            ("Difficulty",       "combo",  ["1 - Easy", "2 - Medium", "3 - Hard"]),
            ("Type",             "combo",  TYPES),
        ]

        self._form_vars = {}
        for i, (lbl, kind, opts) in enumerate(fields):
            row = i + 1
            tk.Label(card, text=lbl, bg=C["surface"], fg=C["muted"],
                     font=("Courier", 10)).grid(row=row, column=0, sticky="w",
                     padx=20, pady=4)
            if kind == "entry":
                var = tk.StringVar()
                e = tk.Entry(card, textvariable=var,
                             bg=C["surface2"], fg=C["text"], insertbackground=C["text"],
                             relief="flat", font=("Courier", 10),
                             highlightthickness=1, highlightbackground=C["border"],
                             highlightcolor=C["accent"])
                e.grid(row=row, column=1, sticky="ew", padx=20, pady=4, ipady=5)
            else:
                var = tk.StringVar(value=opts[0])
                cb = ttk.Combobox(card, textvariable=var, values=opts,
                                  state="readonly", font=("Courier", 10))
                cb.grid(row=row, column=1, sticky="ew", padx=20, pady=4, ipady=4)
                self.style.configure("TCombobox",
                    fieldbackground=C["surface2"], background=C["surface2"],
                    foreground=C["text"], arrowcolor=C["muted"])
            self._form_vars[lbl] = var

        card.columnconfigure(1, weight=1)

        today_str = date.today().isoformat()
        self._form_vars["Deadline (YYYY-MM-DD)"].set((date.today()+timedelta(3)).isoformat())

        self.add_status = tk.Label(card, text="", bg=C["surface"], fg=C["accent3"],
                                   font=("Courier", 10))
        self.add_status.grid(row=len(fields)+2, column=0, columnspan=2, pady=(4, 0))

        self._btn(card, "+ Add Assignment", self._add_assignment, C["accent"]).grid(
            row=len(fields)+1, column=0, columnspan=2, pady=14, padx=20, sticky="ew")

    # ── OPTIMIZE TAB ─────────────────────────────────────────────────────────
    def _build_optimize(self):
        p = self.tab_opt
        p.configure(style="TFrame")

        top = tk.Frame(p, bg=C["bg"])
        top.pack(fill="x", padx=12, pady=(12, 6))

        info = self._card(top)
        info.pack(side="left", fill="x", expand=True, padx=(0, 8))
        tk.Label(info, text="HEURISTIC OPTIMIZATION ENGINE",
                 bg=C["surface"], fg=C["accent"],
                 font=("Courier", 10, "bold")).pack(anchor="w", padx=14, pady=(12, 4))
        tk.Label(info,
                 text="Greedy Best-First Search  ·  Deadline Relaxation  ·  Constraint Propagation",
                 bg=C["surface"], fg=C["muted"],
                 font=("Courier", 9)).pack(anchor="w", padx=14, pady=(0, 12))

        ctrl = tk.Frame(top, bg=C["bg"])
        ctrl.pack(side="right")
        self._btn(ctrl, "▶  Run Agent",   self._run_optimize,  C["accent3"]).pack(pady=4)
        self._btn(ctrl, "↺  Reset",       self._reset_opt,     C["surface2"]).pack(pady=4)

        self.score_lbl = tk.Label(ctrl, text="Score: —",
                                  bg=C["bg"], fg=C["accent"],
                                  font=("Courier", 12, "bold"))
        self.score_lbl.pack(pady=4)

        bottom = tk.Frame(p, bg=C["bg"])
        bottom.pack(fill="both", expand=True, padx=12, pady=4)

        # Agent log
        log_card = self._card(bottom)
        log_card.pack(side="left", fill="both", expand=True, padx=(0, 8))
        tk.Label(log_card, text="AGENT LOG",
                 bg=C["surface"], fg=C["accent"],
                 font=("Courier", 10, "bold")).pack(anchor="w", padx=12, pady=(10, 4))
        self.log_text = tk.Text(log_card, bg=C["surface2"], fg=C["muted"],
                                font=("Courier", 9), relief="flat",
                                state="disabled", wrap="word")
        ls = ttk.Scrollbar(log_card, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=ls.set)
        self.log_text.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=(0, 10))
        ls.pack(side="left", fill="y", pady=(0, 10), padx=(0, 8))

        self.log_text.tag_configure("ok",   foreground=C["accent3"])
        self.log_text.tag_configure("warn", foreground=C["amber"])
        self.log_text.tag_configure("err",  foreground=C["overdue"])
        self.log_text.tag_configure("info", foreground=C["accent"])
        self.log_text.tag_configure("sep",  foreground=C["border"])

        # Recommendations
        rec_card = self._card(bottom, width=320)
        rec_card.pack(side="right", fill="both")
        rec_card.pack_propagate(False)
        tk.Label(rec_card, text="RECOMMENDATIONS",
                 bg=C["surface"], fg=C["accent"],
                 font=("Courier", 10, "bold")).pack(anchor="w", padx=12, pady=(10, 4))
        self.rec_frame = tk.Frame(rec_card, bg=C["surface"])
        self.rec_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    # ── ABOUT TAB ────────────────────────────────────────────────────────────
    def _build_about(self):
        p = self.tab_about
        p.configure(style="TFrame")

        canvas = tk.Canvas(p, bg=C["bg"], highlightthickness=0)
        sb = ttk.Scrollbar(p, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        canvas.pack(fill="both", expand=True)

        inner = tk.Frame(canvas, bg=C["bg"])
        canvas.create_window((0, 0), window=inner, anchor="nw")
        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        def section(title, content_lines):
            f = self._card(inner)
            f.pack(fill="x", padx=12, pady=5)
            tk.Label(f, text=title, bg=C["surface"], fg=C["accent"],
                     font=("Courier", 11, "bold")).pack(anchor="w", padx=14, pady=(12, 4))
            for line in content_lines:
                tk.Label(f, text=line, bg=C["surface"], fg=C["muted"],
                         font=("Courier", 10), justify="left",
                         wraplength=800, anchor="w").pack(anchor="w", padx=14, pady=2)
            tk.Label(f, text="", bg=C["surface"]).pack(pady=4)

        section("AGENT TYPE — UTILITY-BASED AGENT", [
            "Percepts  : Assignment list (subject, title, deadline, hours, difficulty)",
            "Actions   : Schedule task on deadline OR reschedule to an earlier date",
            "Goals     : Minimize daily workload peaks, reduce student overload",
            "Utility   : U(a) = 0.5*(1/slack) + 0.3*diff_norm + 0.2*hours_norm",
            "Decision  : Agent always picks the action that maximises expected utility.",
        ])

        section("AI TECHNIQUES", [
            "1. Heuristic Search (Greedy Best-First)  — Priority queue ordered by U(a);",
            "   agent expands highest-utility node first (most urgent/hardest task first).",
            "",
            "2. Scheduling — Maps assignments onto a 14-day calendar. Tracks daily load.",
            "   Enforces hard constraint: daily work ≤ 6 hours.",
            "",
            "3. Deadline Relaxation — If deadline day is overloaded AND slack > 1 day,",
            "   agent finds earliest free slot before deadline and recommends starting there.",
            "",
            "4. Constraint Propagation — After each assignment, updates the schedule dict",
            "   so subsequent nodes see accurate remaining capacity.",
        ])

        section("UTILITY FUNCTION BREAKDOWN", [
            "U(a) = w₁·(1/max(slack,1))  +  w₂·(difficulty/3)  +  w₃·(hours/12)",
            "",
            "w₁ = 0.50  →  Urgency is the dominant factor (deadline proximity)",
            "w₂ = 0.30  →  Harder tasks get higher priority to avoid last-minute panic",
            "w₃ = 0.20  →  Longer tasks should be started earlier",
            "",
            "Score/100 = min(100, U × 120)   (maps raw utility to student-readable score)",
        ])

        section("PROJECT DETAILS", [
            "College Project  : Assignment Deadline Management Agent",
            "Agent Type       : Utility-Based Agent",
            "Problem          : Optimize assignment deadlines to reduce student overload",
            "Goal             : Minimize peak daily workload, prevent deadline clustering",
            "AI Techniques    : Heuristic Search, Priority Queuing, Constraint Scheduling,",
            "                   Deadline Relaxation, Utility Scoring Function",
            "Language         : Python 3.8+",
            "GUI Framework    : Tkinter (built-in, no external dependencies)",
        ])

    # ─────────────────────────────────────────────────────────────────────────
    #  LOGIC CALLBACKS
    # ─────────────────────────────────────────────────────────────────────────

    def refresh_all(self):
        self._refresh_stats()
        self._refresh_tree()
        self._refresh_forecast()

    def _refresh_stats(self):
        for w in self.stat_frame.winfo_children():
            w.destroy()
        pending  = [a for a in self.assignments if a.status == "pending"]
        urgent   = [a for a in pending if 0 <= a.slack_days() <= 2]
        overdue  = [a for a in pending if a.slack_days() < 0]
        total_h  = sum(a.estimated_hours for a in pending)

        stats = [
            ("Total",    str(len(pending)),    C["accent"]),
            ("Urgent",   str(len(urgent)),     C["amber"]),
            ("Overdue",  str(len(overdue)),    C["overdue"]),
            ("Hours",    f"{total_h:.0f}h",    C["accent3"]),
        ]
        for label, val, color in stats:
            f = tk.Frame(self.stat_frame, bg=C["surface"],
                         highlightthickness=1, highlightbackground=C["border"])
            f.pack(side="left", expand=True, fill="x", padx=4)
            tk.Label(f, text=val,   bg=C["surface"], fg=color,
                     font=("Courier", 22, "bold")).pack(pady=(10, 2))
            tk.Label(f, text=label, bg=C["surface"], fg=C["muted"],
                     font=("Courier", 9)).pack(pady=(0, 10))

    def _refresh_tree(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        pending = [a for a in self.assignments if a.status == "pending"]
        pending.sort(key=lambda a: -UtilityFunction.compute(a))

        for a in pending:
            u     = UtilityFunction.compute(a)
            score = UtilityFunction.score_to_100(u)
            urg   = a.urgency_label()
            color = URGENCY_COLORS.get(urg, C["text"])
            tag   = urg.lower()
            self.tree.insert("", "end",
                values=(a.subject, a.title, str(a.deadline),
                        f"{a.estimated_hours}h", DIFF_LABELS[a.difficulty],
                        urg, score),
                iid=str(a.id), tags=(tag,))
            self.tree.tag_configure(tag, foreground=color)

    def _refresh_forecast(self):
        for w in self.forecast_frame.winfo_children():
            w.destroy()
        sched: dict = {}
        for a in self.assignments:
            if a.status == "pending":
                sched[a.deadline] = sched.get(a.deadline, 0) + a.estimated_hours

        for i in range(7):
            d    = date.today() + timedelta(days=i)
            load = sched.get(d, 0.0)
            pct  = min(1.0, load / 8.0)
            color = C["overdue"] if load > 6 else C["amber"] if load > 3 else C["accent3"]
            lbl  = d.strftime("%a %d")

            row = tk.Frame(self.forecast_frame, bg=C["surface"])
            row.pack(fill="x", pady=2)
            tk.Label(row, text=lbl, bg=C["surface"], fg=C["muted"],
                     font=("Courier", 9), width=8, anchor="w").pack(side="left")

            bar_bg = tk.Frame(row, bg=C["surface2"], height=14)
            bar_bg.pack(side="left", fill="x", expand=True, padx=4)
            bar_bg.pack_propagate(False)
            if pct > 0:
                bar_fill = tk.Frame(bar_bg, bg=color, height=14)
                bar_fill.place(relwidth=pct, relheight=1)

            tk.Label(row, text=f"{load:.1f}h", bg=C["surface"], fg=color,
                     font=("Courier", 9), width=5).pack(side="right")

    def _mark_done(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Select", "Select an assignment first."); return
        aid = int(sel[0])
        for a in self.assignments:
            if a.id == aid:
                a.status = "done"; break
        self.refresh_all()

    def _delete_item(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Select", "Select an assignment first."); return
        aid = int(sel[0])
        self.assignments = [a for a in self.assignments if a.id != aid]
        self.refresh_all()

    def _add_assignment(self):
        v = self._form_vars
        subj  = v["Subject"].get().strip()
        title = v["Title"].get().strip()
        dstr  = v["Deadline (YYYY-MM-DD)"].get().strip()
        hrs   = v["Estimated Hours"].get().strip()
        diff  = int(v["Difficulty"].get().split()[0])
        atype = v["Type"].get()

        if not subj or not title or not dstr or not hrs:
            messagebox.showerror("Error", "All fields are required."); return
        try:
            deadline = date.fromisoformat(dstr)
        except ValueError:
            messagebox.showerror("Error", "Date must be YYYY-MM-DD format."); return
        try:
            hours = float(hrs)
            if hours <= 0 or hours > 40:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Hours must be a number between 0.5 and 40."); return

        a = Assignment(new_id(), subj, title, deadline, hours, diff, atype)
        self.assignments.append(a)
        self.add_status.config(text=f"✓ '{title}' added successfully!", fg=C["accent3"])
        self.after(2500, lambda: self.add_status.config(text=""))
        self.refresh_all()
        self.nb.select(0)

    def _run_optimize(self):
        self.scheduler = HeuristicScheduler(self.assignments)
        recs           = self.scheduler.run()
        score          = self.scheduler.overall_score()

        # ── Log
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        for line in self.scheduler.log:
            if line.startswith("►") or "[INIT]" in line or "[LOAD]" in line or "[DONE]" in line or "[QUEUE]" in line or "[HEURISTIC]" in line:
                tag = "info"
            elif "[OK]" in line:
                tag = "ok"
            elif "[RESCHEDULE]" in line:
                tag = "warn"
            elif "[WARNING]" in line or "[WARN]" in line:
                tag = "err"
            elif line.startswith("─"):
                tag = "sep"
            else:
                tag = None
            self.log_text.insert("end", line + "\n", tag or "")
        self.log_text.configure(state="disabled")
        self.log_text.see("end")

        # ── Score
        c = C["accent3"] if score >= 70 else C["amber"] if score >= 50 else C["overdue"]
        self.score_lbl.config(text=f"Score: {score}/100", fg=c)

        # ── Recommendations
        for w in self.rec_frame.winfo_children():
            w.destroy()
        if not recs:
            tk.Label(self.rec_frame, text="✓  Schedule is optimal.\nNo overloads detected.",
                     bg=C["surface"], fg=C["accent3"],
                     font=("Courier", 10), justify="center").pack(expand=True)
        else:
            ys2 = ttk.Scrollbar(self.rec_frame, orient="vertical")
            rtext = tk.Text(self.rec_frame, bg=C["surface2"], fg=C["text"],
                            font=("Courier", 9), relief="flat", wrap="word",
                            yscrollcommand=ys2.set, state="normal")
            ys2.configure(command=rtext.yview)
            rtext.pack(side="left", fill="both", expand=True)
            ys2.pack(side="left", fill="y")

            rtext.tag_configure("head",   foreground=C["accent"],  font=("Courier", 9, "bold"))
            rtext.tag_configure("action", foreground=C["amber"])
            rtext.tag_configure("reason", foreground=C["muted"])
            rtext.tag_configure("sep2",   foreground=C["border"])

            for r in recs:
                rtext.insert("end", f"[{r['action']}] {r['subject']}\n", "head")
                rtext.insert("end", f"{r['title']}\n", "head")
                rtext.insert("end", f"Start by: {r['recommended_start']}  ({r['hours']}h)\n", "action")
                rtext.insert("end", f"{r['reason']}\n", "reason")
                rtext.insert("end", "─"*36 + "\n", "sep2")
            rtext.configure(state="disabled")

        self.opt_ran = True

    def _reset_opt(self):
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.configure(state="disabled")
        for w in self.rec_frame.winfo_children():
            w.destroy()
        self.score_lbl.config(text="Score: —", fg=C["accent"])
        self.opt_ran = False


# ─────────────────────────────────────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = AgentApp()
    app.mainloop()
