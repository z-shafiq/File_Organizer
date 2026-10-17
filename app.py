
app.py - FileOrganizer (simple version)
Pages: Dashboard | File Explorer | Duplicate Audit | Organizer
"""

import datetime
import customtkinter as ctk
from tkinter import filedialog, messagebox, ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import backend
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# Colors
BG_MAIN = "#0F172A"
BG_SIDEBAR = "#0B0F19"
BG_CARD = "#1E293B"
ACCENT = "#6366F1"
ACCENT_HOVER = "#4F46E5"
MUTED = "#94A3B8"
GREEN = "#10B981"
COLORS = ['#6366F1', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#64748B']


class ModernOrganizerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("FileOrganizer - EF101-P19")
        self.geometry("1280x780")
        self.minsize(1100, 650)
        self.configure(fg_color=BG_MAIN)

        # Data of the current scan
        self.inventory = []
        self.duplicates = []
        self.folder_count = 0
        self.root_dir = ""
        self.scan_time = ""
        self.summary = {}
        self.plan = []
        self.shown = {}                       # table row id -> file record
        self.sort_key, self.sort_reverse = "name", False

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.setup_style()
        self.setup_sidebar()
        self.setup_top_bar()
        self.frames = {}
        self.setup_dashboard()
        self.setup_explorer()
        self.setup_duplicates()
        self.setup_organizer()
        self.show_frame("dashboard")

    # ================= BUILDING THE SCREEN =================
    def setup_style(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background=BG_CARD, foreground="#F8FAFC", fieldbackground=BG_CARD,
                        rowheight=28, borderwidth=0)
        style.configure("Treeview.Heading", background=BG_MAIN, foreground="#A5B4FC",
                        font=("Segoe UI", 10, "bold"), relief="flat")
        style.map("Treeview", background=[('selected', '#4338CA')])

    def make_table(self, parent, columns, titles, widths):
        """Small helper: a table (Treeview) with a scrollbar."""
        box = ctk.CTkFrame(parent, fg_color=BG_CARD, corner_radius=12)
        table = ttk.Treeview(box, columns=columns, show="headings", selectmode="browse")
        for col, title, width in zip(columns, titles, widths):
            table.heading(col, text=title)
            table.column(col, width=width)
        scroll = ttk.Scrollbar(box, orient="vertical", command=table.yview)
        table.configure(yscroll=scroll.set)
        table.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scroll.pack(side="right", fill="y", pady=10)
        return box, table

    def setup_sidebar(self):
        sidebar = ctk.CTkFrame(self, fg_color=BG_SIDEBAR, corner_radius=0, width=230)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)

        ctk.CTkLabel(sidebar, text="⚡ FileOrganizer", font=("Segoe UI", 20, "bold")
                     ).grid(row=0, column=0, padx=20, pady=(25, 5), sticky="w")
        ctk.CTkLabel(sidebar, text="EF101-P19", font=("Segoe UI", 11), text_color=MUTED
                     ).grid(row=1, column=0, padx=20, pady=(0, 25), sticky="w")

        self.nav_btns = {}
        items = [("dashboard", "📊  Dashboard"), ("explorer", "📂  File Explorer"),
                 ("duplicates", "🔍  Duplicate Audit"), ("organizer", "🗂️  Organizer")]
        for row, (key, label) in enumerate(items, start=2):
            btn = ctk.CTkButton(sidebar, text=label, font=("Segoe UI", 13, "bold"), anchor="w", height=42,
                                fg_color="transparent", text_color=MUTED, hover_color=BG_CARD,
                                command=lambda k=key: self.show_frame(k))
            btn.grid(row=row, column=0, padx=12, pady=4, sticky="ew")
            self.nav_btns[key] = btn

    def setup_top_bar(self):
        self.main = ctk.CTkFrame(self, fg_color="transparent")
        self.main.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main.grid_rowconfigure(1, weight=1)
        self.main.grid_columnconfigure(0, weight=1)

        bar = ctk.CTkFrame(self.main, fg_color=BG_CARD, corner_radius=12)
        bar.grid(row=0, column=0, sticky="ew", pady=(0, 15))

        ctk.CTkButton(bar, text="Select Folder & Scan", font=("Segoe UI", 13, "bold"), fg_color=ACCENT,
                      hover_color=ACCENT_HOVER, height=38, command=self.execute_scan
                      ).pack(side="left", padx=15, pady=12)
        self.lbl_dir = ctk.CTkLabel(bar, text="No folder selected", text_color=MUTED)
        self.lbl_dir.pack(side="left", padx=10)

        self.btn_csv = ctk.CTkButton(bar, text="Export CSV", width=100, height=36, fg_color="#059669",
                                     state="disabled", command=self.export_csv)
        self.btn_csv.pack(side="right", padx=(5, 15), pady=12)
        self.btn_json = ctk.CTkButton(bar, text="Export JSON", width=100, height=36, fg_color="#0EA5E9",
                                      state="disabled", command=self.export_json)
        self.btn_json.pack(side="right", padx=5, pady=12)

    # ---------- Dashboard ----------
    def setup_dashboard(self):
        frame = ctk.CTkFrame(self.main, fg_color="transparent")
        self.frames["dashboard"] = frame
        frame.grid_columnconfigure(0, weight=3)
        frame.grid_columnconfigure(1, weight=1)
        frame.grid_rowconfigure(1, weight=1)

        cards = ctk.CTkFrame(frame, fg_color="transparent")
        cards.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 15))
        cards.columnconfigure((0, 1, 2, 3), weight=1, uniform="a")
        self.card_files = self.make_card(cards, "Total Files", "#3B82F6", 0)
        self.card_folders = self.make_card(cards, "Total Folders", "#8B5CF6", 1)
        self.card_size = self.make_card(cards, "Total Storage", GREEN, 2)
        self.card_dups = self.make_card(cards, "Duplicate Groups", "#F59E0B", 3)

        self.chart_area = ctk.CTkFrame(frame, fg_color=BG_CARD, corner_radius=12)
        self.chart_area.grid(row=1, column=0, sticky="nsew", padx=(0, 8))

        right = ctk.CTkFrame(frame, fg_color="transparent")
        right.grid(row=1, column=1, sticky="nsew", padx=(8, 0))
        ctk.CTkLabel(right, text="Top 10 largest files", font=("Segoe UI", 14, "bold")
                     ).pack(anchor="w", pady=(0, 6))
        box, self.top_table = self.make_table(right, ("name", "size"), ("File", "Size"), (150, 80))
        box.pack(fill="both", expand=True)

    def make_card(self, parent, title, color, col):
        card = ctk.CTkFrame(parent, fg_color=BG_CARD, corner_radius=12)
        card.grid(row=0, column=col, padx=(0 if col == 0 else 8, 0), sticky="ew")
        ctk.CTkFrame(card, fg_color=color, height=4, corner_radius=0).pack(fill="x")
        ctk.CTkLabel(card, text=title, font=("Segoe UI", 11, "bold"), text_color=MUTED
                     ).pack(anchor="w", padx=15, pady=(12, 2))
        value = ctk.CTkLabel(card, text="0", font=("Segoe UI", 22, "bold"))
        value.pack(anchor="w", padx=15, pady=(0, 12))
        return value

    # ---------- Explorer ----------
    def setup_explorer(self):
        frame = ctk.CTkFrame(self.main, fg_color="transparent")
        self.frames["explorer"] = frame

        bar = ctk.CTkFrame(frame, fg_color=BG_CARD, corner_radius=10)
        bar.pack(fill="x", pady=(0, 12))

        self.e_search = ctk.CTkEntry(bar, placeholder_text="🔍 Search by name, extension or category...",
                                     height=36, border_width=0, fg_color=BG_MAIN)
        self.e_search.pack(fill="x", padx=10, pady=(10, 6))

        row = ctk.CTkFrame(bar, fg_color="transparent")
        row.pack(fill="x", padx=10, pady=(0, 10))
        self.cat_var = ctk.StringVar(value="All")
        ctk.CTkOptionMenu(row, values=["All"] + backend.ALL_CATEGORIES, variable=self.cat_var, width=120,
                          command=lambda v: self.apply_filters()).pack(side="left", padx=(0, 6))
        self.e_min = self.small_entry(row, "Min MB", 70)
        self.e_max = self.small_entry(row, "Max MB", 70)
        self.e_folder = self.small_entry(row, "Folder contains", 140)
        self.e_from = self.small_entry(row, "From YYYY-MM-DD", 130)
        self.e_to = self.small_entry(row, "To YYYY-MM-DD", 130)
        ctk.CTkButton(row, text="Reset", width=60, fg_color="#475569", command=self.reset_filters
                      ).pack(side="left", padx=6)
        self.e_search.bind("<KeyRelease>", lambda e: self.apply_filters())

        cols = ("name", "category", "size", "extension", "modified", "folder")
        self.col_titles = {"name": "File Name", "category": "Category", "size": "Size", "extension": "Type",
                           "modified": "Modified", "folder": "Folder"}
        self.col_keys = {"name": "name", "category": "category", "size": "size_bytes", "extension": "extension",
                         "modified": "modified_at", "folder": "folder"}
        box, self.table = self.make_table(frame, cols, list(self.col_titles.values()),
                                          (220, 100, 90, 70, 140, 220))
        box.pack(fill="both", expand=True)
        for col in cols:                                   # click a heading to sort
            self.table.heading(col, command=lambda c=col: self.sort_by(c))
        self.table.bind("<Double-1>", self.on_double_click)

        self.lbl_count = ctk.CTkLabel(frame, text="", text_color=MUTED)
        self.lbl_count.pack(anchor="w", pady=(6, 0))

    def small_entry(self, parent, placeholder, width):
        entry = ctk.CTkEntry(parent, placeholder_text=placeholder, width=width, fg_color=BG_MAIN)
        entry.pack(side="left", padx=3)
        entry.bind("<KeyRelease>", lambda e: self.apply_filters())
        return entry

    # ---------- Duplicates ----------
    def setup_duplicates(self):
        frame = ctk.CTkFrame(self.main, fg_color=BG_CARD, corner_radius=12)
        self.frames["duplicates"] = frame
        self.txt_dups = ctk.CTkTextbox(frame, font=("Consolas", 12), fg_color="transparent", wrap="word")
        self.txt_dups.pack(fill="both", expand=True, padx=15, pady=15)

    # ---------- Organizer ----------
    def setup_organizer(self):
        frame = ctk.CTkFrame(self.main, fg_color=BG_CARD, corner_radius=12)
        self.frames["organizer"] = frame
        card = ctk.CTkFrame(frame, fg_color="transparent")
        card.pack(fill="both", expand=True, padx=25, pady=25)

        ctk.CTkLabel(card, text="Safe Organizer", font=("Segoe UI", 18, "bold")).pack(anchor="w")
        ctk.CTkLabel(card, text="Step 1: preview what will happen.  Step 2: confirm to COPY files into "
                                "category folders. Originals are never changed or overwritten.",
                     text_color=MUTED).pack(anchor="w", pady=(2, 15))

        buttons = ctk.CTkFrame(card, fg_color="transparent")
        buttons.pack(anchor="w", pady=(0, 12))
        self.btn_preview = ctk.CTkButton(buttons, text="1. Choose Target & Preview", height=40, fg_color=ACCENT,
                                         state="disabled", command=self.preview_organize)
        self.btn_preview.pack(side="left", padx=(0, 10))
        self.btn_apply = ctk.CTkButton(buttons, text="2. Confirm & Copy", height=40, fg_color=GREEN,
                                       state="disabled", command=self.execute_organize)
        self.btn_apply.pack(side="left")

        self.txt_org_log = ctk.CTkTextbox(card, font=("Consolas", 11), fg_color=BG_MAIN, text_color=GREEN)
        self.txt_org_log.pack(fill="both", expand=True)

    def show_frame(self, key):
        for name, btn in self.nav_btns.items():
            btn.configure(fg_color=BG_CARD if name == key else "transparent",
                          text_color="#F8FAFC" if name == key else MUTED)
        for f in self.frames.values():
            f.grid_forget()
        self.frames[key].grid(row=1, column=0, sticky="nsew")

    # ================= SCANNING =================
    def execute_scan(self):
        folder = filedialog.askdirectory(title="Select the folder to scan")
        if not folder:
            return
        self.lbl_dir.configure(text="Scanning... please wait", text_color=MUTED)
        self.update()                                       # refresh the window

        self.root_dir = folder
        self.scan_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.inventory, self.folder_count, problems = backend.scan_directory(folder)
        self.duplicates = backend.find_duplicates(self.inventory)
        self.make_summary()

        self.lbl_dir.configure(text=f"Active: {folder}", text_color=GREEN)
        for btn in (self.btn_csv, self.btn_json, self.btn_preview):
            btn.configure(state="normal")
        self.btn_apply.configure(state="disabled")
        self.plan = []
        self.txt_org_log.delete("1.0", "end")

        self.update_cards()
        self.render_charts()
        self.render_top10()
        self.reset_filters()
        self.render_duplicates()

        if problems:
            messagebox.showwarning("Some items skipped",
                                   f"{len(problems)} item(s) could not be read (permission/locked). "
                                   f"Nothing was changed.\n\nExample:\n" + "\n".join(problems[:5]))

    def make_summary(self):
        """Numbers used by the dashboard and the JSON export."""
        by_category = {}
        for cat in backend.ALL_CATEGORIES:
            by_category[cat] = {'count': 0, 'size_bytes': 0}
        for rec in self.inventory:
            by_category[rec['category']]['count'] += 1
            by_category[rec['category']]['size_bytes'] += rec['size_bytes']
        total = sum(r['size_bytes'] for r in self.inventory)
        recoverable = sum(g['recoverable_bytes'] for g in self.duplicates)
        self.summary = {
            'total_files': len(self.inventory),
            'total_folders': self.folder_count,
            'total_size': backend.format_size(total),
            'by_category': by_category,
            'duplicate_groups': len(self.duplicates),
            'recoverable_space': backend.format_size(recoverable),
        }

    def update_cards(self):
        self.card_files.configure(text=f"{self.summary['total_files']:,}")
        self.card_folders.configure(text=f"{self.summary['total_folders']:,}")
        self.card_size.configure(text=self.summary['total_size'])
        self.card_dups.configure(text=str(self.summary['duplicate_groups']))

    def render_charts(self):
        for widget in self.chart_area.winfo_children():
            widget.destroy()

        cats = [(c, d) for c, d in self.summary['by_category'].items() if d['count'] > 0]
        fig = Figure(figsize=(7, 3.8), facecolor=BG_CARD)
        ax1, ax2 = fig.subplots(1, 2)

        # Chart 1: storage used by each category
        ax1.set_facecolor(BG_CARD)
        sizes = [d['size_bytes'] for c, d in cats]
        if sum(sizes) > 0:
            pieces, _ = ax1.pie(sizes, colors=COLORS[:len(cats)],
                                wedgeprops=dict(width=0.4, edgecolor=BG_CARD))
            ax1.legend(pieces, [f"{c}: {backend.format_size(d['size_bytes'])}" for c, d in cats],
                       loc="upper center", bbox_to_anchor=(0.5, 0.0), ncol=2, frameon=False,
                       labelcolor="#F8FAFC", fontsize=8)
        ax1.set_title("Storage by Category", color="#F8FAFC", fontsize=11, fontweight="bold")

        # Chart 2: number of files in each category
        ax2.set_facecolor(BG_CARD)
        bars = ax2.barh([c for c, d in cats][::-1], [d['count'] for c, d in cats][::-1], color=ACCENT)
        ax2.bar_label(bars, color="#F8FAFC", fontsize=8)
        ax2.tick_params(colors=MUTED, labelsize=8)
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        ax2.set_title("Number of Files by Category", color="#F8FAFC", fontsize=11, fontweight="bold")

        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=self.chart_area)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    def render_top10(self):
        self.top_table.delete(*self.top_table.get_children())
        biggest = sorted(self.inventory, key=lambda r: r['size_bytes'], reverse=True)[:10]
        for rec in biggest:
            self.top_table.insert("", "end", values=(rec['name'], rec['size_human']))

    # ================= EXPLORER =================
    def to_number(self, entry):
        """Text box -> number (or None if empty/invalid)."""
        try:
            return float(entry.get().strip())
        except ValueError:
            return None

    def valid_date(self, entry):
        """Text box -> 'YYYY-MM-DD' (or '' if empty/invalid)."""
        text = entry.get().strip()
        try:
            datetime.datetime.strptime(text, "%Y-%m-%d")
            return text
        except ValueError:
            return ""

    def apply_filters(self):
        rows = backend.filter_inventory(
            self.inventory,
            query=self.e_search.get().strip(),
            category=self.cat_var.get(),
            min_mb=self.to_number(self.e_min),
            max_mb=self.to_number(self.e_max),
            folder=self.e_folder.get().strip(),
            date_from=self.valid_date(self.e_from),
            date_to=self.valid_date(self.e_to),
        )
        rows.sort(key=lambda r: (r[self.sort_key].lower() if isinstance(r[self.sort_key], str)
                                 else r[self.sort_key]), reverse=self.sort_reverse)

        self.table.delete(*self.table.get_children())
        self.shown = {}
        for i, rec in enumerate(rows):
            self.shown[str(i)] = rec
            self.table.insert("", "end", iid=str(i), values=(
                rec['name'], rec['category'], rec['size_human'], rec['extension'],
                rec['modified_at'], rec['folder']))
        self.lbl_count.configure(text=f"Showing {len(rows)} of {len(self.inventory)} files "
                                      f"(double-click a row for details)")

    def reset_filters(self):
        for entry in (self.e_search, self.e_min, self.e_max, self.e_folder, self.e_from, self.e_to):
            if entry.get():
                entry.delete(0, "end")
        self.cat_var.set("All")
        self.apply_filters()

    def sort_by(self, col):
        key = self.col_keys[col]
        self.sort_reverse = (not self.sort_reverse) if key == self.sort_key else False
        self.sort_key = key
        for c, title in self.col_titles.items():
            arrow = ""
            if self.col_keys[c] == key:
                arrow = " ▼" if self.sort_reverse else " ▲"
            self.table.heading(c, text=title + arrow)
        self.apply_filters()

    def on_double_click(self, event):
        selected = self.table.selection()
        if not selected:
            return
        rec = self.shown[selected[0]]
        text = (f"Name: {rec['name']}\nFull path: {rec['path']}\nRelative path: {rec['relative_path']}\n"
                f"Size: {rec['size_human']} ({rec['size_bytes']} bytes)\n"
                f"Created: {rec['created_at']}\nModified: {rec['modified_at']}")
        if rec['category'] == "Images":
            meta = backend.extract_image_metadata(rec['path'])
            text += f"\n\nImage format: {meta['format']}\nDimensions: {meta['dimensions']}"
        messagebox.showinfo("File Details", text)

    # ================= DUPLICATES =================
    def render_duplicates(self):
        self.txt_dups.delete("1.0", "end")
        out = ("WHY FILE NAMES ARE NOT ENOUGH:\n"
               "Two files can have the same name but different content, and identical files can have\n"
               "different names. So we compare the size first, then the SHA-256 fingerprint of the\n"
               "content. Same size + same SHA-256 = exact duplicate.\n"
               "Nothing is deleted automatically - this page only reports.\n\n")
        if not self.duplicates:
            out += "No exact duplicates found."
        else:
            out += (f"{len(self.duplicates)} duplicate group(s) - potentially recoverable space: "
                    f"{self.summary['recoverable_space']}\n\n")
            for number, group in enumerate(self.duplicates, start=1):
                out += (f"Group {number}  |  each file: {backend.format_size(group['size_bytes'])}  |  "
                        f"recoverable: {backend.format_size(group['recoverable_bytes'])}\n")
                for path in group['paths']:
                    out += f"   - {path}\n"
                out += "\n"
        self.txt_dups.insert("1.0", out)

    # ================= ORGANIZER =================
    def preview_organize(self):
        target = filedialog.askdirectory(title="Select the destination folder")
        if not target:
            return
        self.plan = backend.plan_organization(self.inventory, target)
        self.txt_org_log.delete("1.0", "end")
        self.txt_org_log.insert("end", f"PREVIEW ONLY - nothing has been changed yet.\n"
                                       f"{len(self.plan)} files would be COPIED to: {target}\n\n")
        for source, destination in self.plan:
            self.txt_org_log.insert("end", f"{source}\n    -> {destination}\n")
        self.btn_apply.configure(state="normal")

    def execute_organize(self):
        if not messagebox.askyesno("Confirm", f"Copy {len(self.plan)} files now?\n"
                                              f"Originals stay untouched, nothing is overwritten."):
            return
        self.update()
        logs = backend.organize_files(self.plan)
        self.txt_org_log.delete("1.0", "end")
        self.txt_org_log.insert("1.0", "\n".join(logs))
        self.btn_apply.configure(state="disabled")
        messagebox.showinfo("Done", "Copy finished. See the log.")

    # ================= EXPORT =================
    def export_csv(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV File", "*.csv")])
        if path and backend.export_inventory_csv(self.inventory, self.root_dir, self.scan_time, path):
            messagebox.showinfo("Export", f"Saved:\n{path}")

    def export_json(self):
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON File", "*.json")])
        if path and backend.export_inventory_json(self.inventory, self.summary, self.root_dir,
                                                  self.scan_time, path):
            messagebox.showinfo("Export", f"Saved:\n{path}")


if __name__ == "__main__":
    app = ModernOrganizerApp()
    app.mainloop()