import tkinter
from tkinter import ttk
from tkinter import filedialog
import customtkinter

import pandas as pd
import numpy as np
import random
from collections import defaultdict, Counter
from datetime import date, datetime



import os
import ast

import matplotlib.pyplot as plt
import matplotlib
import matplotlib.dates as mdates
import matplotlib.patches as mpatches
matplotlib.use('TkAgg') 
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure



#  Differennt GUI's (seperate) that I need here - 1. Entry Position (as In gateway). Shall show some extra things like Stats or recently added tasks etc
# 2. Addition of Task (I hope that we have validation of data along that)
# 3. Modification of Tasks
# 4. Stats of Tasks
# 5. Random Gradient Colors and Animations would be nice but not specifically needed

class add_tasks(customtkinter.CTkFrame):
    
    TAG_OPTIONS = [
        "C","Cpp","Bash","Analytics","Machine Learning",
        "Artificial Intelligence","Python","LaTeX",
        "Core Computer Science","Algorithms","Mathematics",
        "Space and Astronomy","Embedded","Compiler",
        "Hobby","Work","Obligation","R","GPU programming",
        "Game Development","Portfolio and Design",
        "DevOPS Shenanigans","AR/VR- Mixed Reality",
        "Databases","Teleology of Projects and Frameworks"
    ]

    def __init__(self, master):
        super().__init__(master)
        #Tasks,Description,Prediction_Time,Priority,Tags,Status,Subtasks,Time_Taken_Until,Progress_Till,Project_Folder_Location,Estimated_Effort_Points,Dates
        default_priority = 5
        # Layout
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, minsize=220)
        self.columnconfigure(2, weight=3)
        self.columnconfigure(3, weight=1)

        for i in range(15):
            self.grid_rowconfigure(i, weight=1)

        # ================================
        # Task Name
        # ================================
        self.ask_input_label = customtkinter.CTkLabel(self, text="Task Name")
        self.ask_input_label.grid(row=0, column=1, sticky="e", padx=(0,10), pady=5)

        self.input = customtkinter.CTkEntry(
            self,
            placeholder_text="Give Identity to your tasks"
        )
        self.input.grid(row=0, column=2, sticky="ew", padx=(0,20), pady=5)

        # ================================
        # Description
        # ================================
        self.ask_desc_label = customtkinter.CTkLabel(self, text="Description")
        self.ask_desc_label.grid(row=1, column=1, sticky="ne", padx=(0,10), pady=5)

        self.desc = customtkinter.CTkTextbox(self, height=80)
        self.desc.grid(row=1, column=2, sticky="ew", padx=(0,20), pady=5)

        # ================================
        # Prediction Time (Default = 36)
        # ================================
        self.ask_predi_label = customtkinter.CTkLabel(self, text="Prediction Time (Hours)")
        self.ask_predi_label.grid(row=2, column=1, sticky="e", padx=(0,10))

        self.predi_value_label = customtkinter.CTkLabel(self, text="36")
        self.predi_value_label.grid(row=2, column=2, sticky="w")

        self.predi_time = customtkinter.CTkSlider(
            self,
            from_=1,
            to=200,
            number_of_steps=199,
            command=lambda v: self.predi_value_label.configure(text=f"{int(v)}")
        )
        self.predi_time.set(36)
        self.predi_time.grid(row=3, column=1, columnspan=2, sticky="ew", padx=20, pady=5)

        # ================================
        # Priority (1–10)
        # ================================
        self.ask_priority_label = customtkinter.CTkLabel(
            self,
            text="Priority (1 = Low, 10 = Critical)"
        )
        self.ask_priority_label.grid(row=4, column=1, sticky="e", padx=(0,10))

        self.priority_value_label = customtkinter.CTkLabel(
            self,
            text=str(default_priority)
        )
        self.priority_value_label.grid(row=4, column=2, sticky="w")

        self.priority_slider = customtkinter.CTkSlider(
            self,
            from_=1,
            to=10,
            number_of_steps=9,
            command=lambda v: self.priority_value_label.configure(text=f"{int(v)}")
        )
        self.priority_slider.set(default_priority)
        self.priority_slider.grid(row=5, column=1, columnspan=2, sticky="ew", padx=20, pady=5)

        # ================================
        # Tags (Scrollable Multi Select)
        # ================================
        self.ask_tags_label = customtkinter.CTkLabel(self, text="Tags / Categories")
        self.ask_tags_label.grid(row=6, column=1, sticky="ne", padx=(0,10), pady=5)

        self.tags_frame = customtkinter.CTkScrollableFrame(self, height=120)
        self.tags_frame.grid(row=6, column=2, sticky="ew", padx=(0,20), pady=5)

        self.tag_vars = {}

        for tag in self.TAG_OPTIONS:
            var = customtkinter.StringVar(value="off")
            cb = customtkinter.CTkCheckBox(
                self.tags_frame,
                text=tag,
                variable=var,
                onvalue="on",
                offvalue="off"
            )
            cb.pack(anchor="w")
            self.tag_vars[tag] = var

        # ================================
        # Subtasks
        # ================================
        self.ask_Subtasks_label = customtkinter.CTkLabel(self, text="Subtasks")
        self.ask_Subtasks_label.grid(row=7, column=1, sticky="ne", padx=(0,10), pady=5)

        self.subtasks = customtkinter.CTkTextbox(self, height=80)
        self.subtasks.grid(row=7, column=2, sticky="ew", padx=(0,20), pady=5)

        # ================================
        # Project Folder Location
        # ================================
        self.ask_projectfolder_label = customtkinter.CTkLabel(self, text="Project Folder")
        self.ask_projectfolder_label.grid(row=8, column=1, sticky="e", padx=(0,10))

        self.folder_path = customtkinter.StringVar()

        self.folder_button = customtkinter.CTkButton(
            self,
            text="Choose Folder",
            command=self.select_folder
        )
        self.folder_button.grid(row=8, column=2, sticky="w")

        self.folder_display = customtkinter.CTkLabel(
            self,
            textvariable=self.folder_path,
            wraplength=400
        )
        self.folder_display.grid(row=9, column=2, sticky="w")

        # ================================
        # Estimated Effort Points
        # Format: iii _ iii _ iii
        # ================================
        self.ask_estimatedef_label = customtkinter.CTkLabel(
            self,
            text="Estimated Effort Points "
        )
        self.ask_estimatedef_label.grid(row=10, column=1, sticky="e", padx=(0,10))

        self.effort_entry = customtkinter.CTkEntry(
            self,
            placeholder_text="3 _ 5 _ 8 _ 13"
        )
        self.effort_entry.grid(row=10, column=2, sticky="ew", padx=(0,20))


        self.submit_button = customtkinter.CTkButton(
            self,
            text="Add Task",
            height=42,
            corner_radius=10,
            font=customtkinter.CTkFont(size=14, weight="bold"),
            fg_color="#2C6E49",
            hover_color="#1B4332",
            text_color="#E8F5E9",
            command=self.update_data
        )
        self.submit_button.grid(
            row=11,
            column=1,
            columnspan=2,
            sticky="ew",
            padx=20,
            pady=(15, 5)
        )


        self.clear_button = customtkinter.CTkButton(
            self,
            text="Clear Fields",
            height=36,
            corner_radius=10,
            font=customtkinter.CTkFont(size=12),
            fg_color="transparent",
            border_width=1,
            border_color="#555555",
            hover_color="#2A2A2A",
            text_color="#AAAAAA",
            command=self.clear_fields
        )
        self.clear_button.grid(
            row=12,
            column=1,
            columnspan=2,
            sticky="ew",
            padx=20,
            pady=(5, 15)
        )
        

    def update_data(self):
        add_data["Tasks"] = self.input.get()
        add_data["Description"] = self.desc.get("1.0", "end-1c")
        add_data["Prediction_Time"] = int(self.predi_time.get())
        add_data["Priority"] = int(self.priority_slider.get())
        add_data["Tags"] = [tag for tag, var in self.tag_vars.items() if var.get() == "on"]
        add_data["Subtasks"] = self.subtasks.get("1.0", "end-1c")
        add_data["Project_Folder_Location"] = self.folder_path.get()
        add_data["Estimated_Effort_Points"] = self.effort_entry.get() + "_000_000"
        today = date.today().strftime('%d/%m/%Y')
        add_data["Status"] = "Uninitiated"
        add_data["Time_Taken_Until"] = "00.00_00.00_00.00_00.00"
        add_data["Progress_Till"] = "0"
        add_data["Dates"] = f"{today}_00/00/00_00/00/00_00/00/00"
        global data_df
        new_row = pd.DataFrame([add_data])
        data_df = pd.concat([data_df, new_row], ignore_index=True)
        data_df.to_csv(data_path, index=False)
        add_data = dict.fromkeys(data_header, None)

    def clear_fields(self):
        self.input.delete(0, "end")
        self.desc.delete("1.0", "end")
        self.predi_time.set(36)
        self.predi_value_label.configure(text="36")
        self.priority_slider.set(5)
        self.priority_value_label.configure(text="5")
        self.subtasks.delete("1.0", "end")
        self.effort_entry.delete(0, "end")
        self.folder_path.set("")
        for var in self.tag_vars.values():
            var.set("off")
        add_data = dict.fromkeys(data_header, None)

    
    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_path.set(folder)

class modify_tasks(customtkinter.CTkFrame):
    def __init__(self,master):
        super().__init__(master)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.top_bar = customtkinter.CTkFrame(self, fg_color="transparent")
        self.top_bar.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 0))
        self.top_bar.columnconfigure(0, weight=1)
        self.title_label = customtkinter.CTkLabel(
            self.top_bar,
            text="Task Archive — The Record of All Obligations",
            font=customtkinter.CTkFont(size=14, weight="bold")
        )
        self.title_label.grid(row=0, column=0, sticky="w", padx=5)
        self.reload_button = customtkinter.CTkButton(
            self.top_bar,
            text="↺ Reload",
            width=90,
            height=30,
            corner_radius=8,
            fg_color="transparent",
            border_width=1,
            border_color="#555555",
            hover_color="#2A2A2A",
            text_color="#AAAAAA",
            command=self.load_data
        )
        self.reload_button.grid(row=0, column=1, sticky="e", padx=5)

        self.save_button = customtkinter.CTkButton(
            self.top_bar,
            text="⊕ Save Changes",
            width=120,
            height=30,
            corner_radius=8,
            fg_color="#2C6E49",
            hover_color="#1B4332",
            text_color="#E8F5E9",
            command=self.save_data
        )
        self.save_button.grid(row=0, column=2, sticky="e", padx=5)
        self.tree_container = customtkinter.CTkFrame(self, fg_color="#1A1A1A", corner_radius=10)
        self.tree_container.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.tree_container.rowconfigure(0, weight=1)
        self.tree_container.columnconfigure(0, weight=1)
        style = ttk.Style()
        style.theme_use("default")

        style.configure("Custom.Treeview",
            background="#1E1E1E",
            foreground="#CCCCCC",
            rowheight=28,
            fieldbackground="#1E1E1E",
            bordercolor="#333333",
            borderwidth=0,
            font=("Consolas", 11)
        )
        style.configure("Custom.Treeview.Heading",
            background="#2A2A2A",
            foreground="#FFFFFF",
            relief="flat",
            font=("Consolas", 11, "bold")
        )
        style.map("Custom.Treeview",
            background=[("selected", "#2C6E49")],
            foreground=[("selected", "#FFFFFF")]
        )
        style.map("Custom.Treeview.Heading",
            background=[("active", "#3A3A3A")]
        )
        self.tree = ttk.Treeview(
            self.tree_container,
            style="Custom.Treeview",
            selectmode="browse",
            show="headings"
        )
        self.tree.grid(row=0, column=0, sticky="nsew")
        self.scroll_y = ttk.Scrollbar(
            self.tree_container,
            orient="vertical",
            command=self.tree.yview
        )
        self.scroll_y.grid(row=0, column=1, sticky="ns")

        self.scroll_x = ttk.Scrollbar(
            self.tree_container,
            orient="horizontal",
            command=self.tree.xview
        )
        self.scroll_x.grid(row=1, column=0, sticky="ew")

        self.tree.configure(
            yscrollcommand=self.scroll_y.set,
            xscrollcommand=self.scroll_x.set
        )
        self.edit_entry = customtkinter.CTkEntry(
            master=self.tree_container,
            fg_color="#2C2C2C",
            text_color="#FFFFFF",
            corner_radius=0,
            font=("Consolas", 11),
            border_width=1,
            border_color="#2C6E49",
        )
        self.edit_entry.bind("<Return>", self.commit_edit)
        self.edit_entry.bind("<Escape>", self.cancel_edit)
        self.edit_entry.bind("<FocusOut>", self.commit_edit)

        self._edit_item = None
        self._edit_column = None
        self.tree.bind("<Double-1>", self.on_double_click)
        self.status_label = customtkinter.CTkLabel(
            self,
            text="",
            text_color="#4CAF50",
            font=customtkinter.CTkFont(size=11)
        )
        self.status_label.grid(row=2, column=0, pady=(0, 8))
        self.load_data()
    def load_data(self):
        self.tree.delete(*self.tree.get_children())
        global data_df
        data_df = pd.read_csv(data_path)

        columns = list(data_df.columns)
        self.tree["columns"] = columns
        for col in columns:
            self.tree.heading(col, text=col, anchor="w")
            # Width proportional — narrower for status/priority, wider for description
            col_width = 180 if col in ("Description", "Subtasks", "Progress_Till") else 120
            self.tree.column(col, width=col_width, anchor="w", stretch=False, minwidth=60)
        for _, row in data_df.iterrows():
            values = [str(v) if pd.notna(v) else "" for v in row]
            self.tree.insert("", "end", values=values)
        self.status_label.configure(
            text=f"{len(data_df)} task(s) loaded from the archive.",
            text_color="#4CAF50"
        )

    def on_double_click(self, event):
        region = self.tree.identify_region(event.x, event.y)
        if region != "cell":
            return
        col_id  = self.tree.identify_column(event.x)
        row_id  = self.tree.identify_row(event.y)
        if not row_id:
            return
        col_index = int(col_id.replace("#", "")) - 1
        col_name  = self.tree["columns"][col_index]
        x, y, width, height = self.tree.bbox(row_id, col_id)
        current_value = self.tree.set(row_id, col_name)
        self._edit_item   = row_id
        self._edit_column = col_name
        
        self.edit_entry.configure(width=width, height=height)
        self.edit_entry.place(in_=self.tree_container, x=x, y=y)
        
        self.edit_entry.delete(0, "end")
        self.edit_entry.insert(0, current_value)
        self.edit_entry.focus_set()
        self.edit_entry.select_range(0, "end")

    def commit_edit(self, event=None):
        if self._edit_item is None:
            return
        new_value = self.edit_entry.get()
        col_name  = self._edit_column
        row_id    = self._edit_item
        self._edit_item   = None
        self._edit_column = None
        self.edit_entry.place_forget()
        self.tree.set(row_id, col_name, new_value)
        row_index = self.tree.index(row_id)
        try:
            target_dtype = data_df[col_name].dtype
            typed_value = pd.array([new_value], dtype=target_dtype)[0]
        except (ValueError, TypeError):
            typed_value = new_value
        data_df.at[row_index, col_name] = typed_value
        self.status_label.configure(
            text=f"✎ '{col_name}' modified — remember to save.",
            text_color="#FFA726"
        )
        self.edit_entry.place_forget()
        self._edit_item   = None
        self._edit_column = None
        
    def cancel_edit(self, event=None):
        self.edit_entry.place_forget()
        self._edit_item   = None
        self._edit_column = None
    def save_data(self):
        try:
            data_df.to_csv(data_path, index=False)
            self.status_label.configure(
                text="✓ All changes committed to the archive.",
                text_color="#4CAF50"
            )
        except Exception as e:
            self.status_label.configure(
                text=f"✗ The archive refused: {e}",
                text_color="#EF5350"
            )
        
        

# ─────────────────────────────────────────────────────────────────────────────
#  STATS  –  Palette & parsing helpers (module-level, shared by the class)
# ─────────────────────────────────────────────────────────────────────────────

_BG     = "#0f0d1f"
_FRAME  = "#1c1a2e"
_BORDER = "#3a2f52"
_TEXT   = "#c9c0e8"
_MUTED  = "#6b5f8a"

_PALETTE = [
    "#6a29c8", "#e040fb", "#00bcd4", "#ff6b6b",
    "#ffd93d", "#6bcb77", "#4d96ff", "#ff9f1c",
    "#f06292", "#80cbc4", "#ce93d8", "#a5d6a7",
]

_S_COL = {
    "Uninitiated":    "#4d96ff",
    "Ongoing":        "#6bcb77",
    "Halted":         "#ffd93d",
    "Dropped":        "#ff6b6b",
    "Completed":      "#a78bfa",
    "Post Completion":"#e040fb",
}


def _s_tags(s):
    try:   return ast.literal_eval(str(s))
    except: return []

def _s_time_taken(s):
    """(active_days, labor_hours, efficiency_pct, halt_days)"""
    try:
        p = str(s).strip().split("_")
        if len(p) == 4:
            return float(p[0]), float(p[1]), float(p[2]), float(p[3])
    except:
        pass
    return 0.0, 0.0, 0.0, 0.0

def _s_effort(s):
    """[decl_ef, mid_ef, comp_ef]"""
    try:
        p = [int(x) for x in str(s).split("_")]
        return (p + [0, 0, 0])[:3]
    except:
        return [0, 0, 0]

def _s_one_date(d):
    d = str(d).strip()
    if not d or d.startswith("00"):
        return None
    try:
        return datetime.strptime(d, "%d/%m/%Y")
    except:
        return None

def _s_dates(s):
    r = [_s_one_date(p) for p in str(s).strip().split("_")]
    return (r + [None] * 5)[:5]   # [decl, init, ongoing, halt, comp]

def _s_nlp(desc):
    w = str(desc).lower().split()
    if not w: return 0.5
    lex    = len(set(w)) / len(w)
    length = min(len(w) / 40.0, 1.0)
    return 0.5 + length * lex

def _s_cur_ef(ef_list):
    for v in reversed(ef_list):
        if v > 0: return v
    return ef_list[0] if ef_list else 0

def _s_prepare(raw):
    df = raw.copy()
    df["tags_list"] = df["Tags"].apply(_s_tags)
    df["num_tags"]  = df["tags_list"].apply(len)

    tt = df["Time_Taken_Until"].apply(_s_time_taken)
    df["active_days"]  = tt.apply(lambda x: x[0])
    df["labor_hours"]  = tt.apply(lambda x: x[1])
    df["eff_pct"]      = tt.apply(lambda x: x[2])
    df["halt_days"]    = tt.apply(lambda x: x[3])

    ef = df["Estimated_Effort_Points"].apply(_s_effort)
    df["ef_list"] = ef
    df["ef_decl"] = ef.apply(lambda x: x[0])
    df["ef_mid"]  = ef.apply(lambda x: x[1])
    df["ef_comp"] = ef.apply(lambda x: x[2])
    df["ef_cur"]  = ef.apply(_s_cur_ef)

    dl = df["Dates"].apply(_s_dates)
    df["dt_decl"] = dl.apply(lambda x: x[0])
    df["dt_init"] = dl.apply(lambda x: x[1])
    df["dt_ong"]  = dl.apply(lambda x: x[2])
    df["dt_halt"] = dl.apply(lambda x: x[3])
    df["dt_comp"] = dl.apply(lambda x: x[4])
    df["last_act"]= dl.apply(lambda x: max((d for d in x if d), default=None))

    df["nlp"]       = df["Description"].apply(_s_nlp)
    df["progress_f"]= pd.to_numeric(df["Progress_Till"], errors="coerce").fillna(0)
    df["priority"]  = pd.to_numeric(df["Priority"],      errors="coerce").fillna(5)
    df["pred"]      = pd.to_numeric(df["Prediction_Time"],errors="coerce").fillna(0)

    def _comp_days(row):
        if row["dt_init"] and row["dt_comp"]:
            return max((row["dt_comp"] - row["dt_init"]).days, 1)
        return None
    df["comp_days"] = df.apply(_comp_days, axis=1)
    return df


def _s_fig(w=4.5, h=3.5):
    f = plt.figure(figsize=(w, h))
    f.patch.set_facecolor(_BG)
    return f

def _s_style(ax, title="", xl="", yl=""):
    ax.set_facecolor(_FRAME)
    ax.tick_params(colors=_TEXT, labelsize=6.5)
    for lbl in ax.get_xticklabels(): lbl.set_color(_TEXT)
    for lbl in ax.get_yticklabels(): lbl.set_color(_TEXT)
    ax.set_title(title, color=_TEXT, fontsize=8, pad=5)
    ax.set_xlabel(xl,   color=_MUTED, fontsize=7)
    ax.set_ylabel(yl,   color=_MUTED, fontsize=7)
    for sp in ax.spines.values(): sp.set_edgecolor(_BORDER)
    ax.grid(True, color=_BORDER, alpha=0.35, lw=0.5, ls="--")
    return ax

def _s_empty(msg="No Data"):
    f = _s_fig(); ax = f.add_subplot(111); _s_style(ax, msg); f.tight_layout(); return f

def _s_embed(fig, frame):
    for w in frame.winfo_children(): w.destroy()
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True, padx=3, pady=3)
    plt.close(fig)


# ─────────────────────────────────────────────────────────────────────────────

class stats(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        global data_df
        self.df       = _s_prepare(data_df)
        self.tag_mode = "Grouped"

        self.tabview = customtkinter.CTkTabview(
            self,
            fg_color="#1c1a2e",
            segmented_button_fg_color="#0f0d1f",
            segmented_button_unselected_color="#0f0d1f",
            segmented_button_unselected_hover_color="#3a2f52",
            segmented_button_selected_color="#6a29c8",
            segmented_button_selected_hover_color="#8a4ee0",
            text_color="#c9c0e8",
            anchor="center",
        )
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab_work      = self.tabview.add("Work Effort Progress and other Abstractions")
        self.tab_tags      = self.tabview.add("Understanding Tags")
        self.tab_halts     = self.tabview.add("Hall of Halts and Drops")
        self.tab_transcend = self.tabview.add("Is this end or Should we Transcend?")

        self._build_tab_work()
        self._build_tab_tags()
        self._build_tab_halts()
        self._build_tab_transcend()

    # ── QUAD GRID ─────────────────────────────────────────────────────────────

    def _quads(self, parent):
        c = customtkinter.CTkFrame(parent, fg_color="transparent")
        c.pack(fill="both", expand=True, padx=6, pady=6)
        c.columnconfigure(0, weight=1); c.columnconfigure(1, weight=1)
        c.rowconfigure(0, weight=1);    c.rowconfigure(1, weight=1)

        def _sect(row, col):
            bf  = customtkinter.CTkFrame(c, fg_color=_BORDER, corner_radius=8)
            bf.grid(row=row, column=col, padx=6, pady=6, sticky="nsew")
            inf = customtkinter.CTkFrame(bf, fg_color=_BG, corner_radius=6)
            inf.pack(fill="both", expand=True, padx=2, pady=2)
            return inf

        return {
            "tl": _sect(0, 0), "tr": _sect(0, 1),
            "bl": _sect(1, 0), "br": _sect(1, 1),
        }

    # ══════════════════════════════════════════════════════════════════════════
    #  TAB I  –  Work Effort Progress and other Abstractions
    # ══════════════════════════════════════════════════════════════════════════

    def _build_tab_work(self):
        s = self._quads(self.tab_work)
        _s_embed(self._c1_status_pie(),    s["tl"])
        _s_embed(self._c1_cli_bar(),       s["tr"])
        _s_embed(self._c1_labor_scatter(), s["bl"])
        _s_embed(self._c1_ef_priority(),   s["br"])

    def _c1_status_pie(self):
        counts = self.df["Status"].value_counts()
        labels = counts.index.tolist()
        sizes  = counts.values.tolist()
        colors = [_S_COL.get(l, "#888") for l in labels]

        f  = _s_fig(4.5, 3.5)
        ax = f.add_subplot(111)
        ax.set_facecolor(_BG)

        wedges, _, autotexts = ax.pie(
            sizes, labels=None, colors=colors, autopct="%1.0f%%",
            startangle=140, pctdistance=0.72,
            wedgeprops=dict(linewidth=1.6, edgecolor=_BG),
        )
        for at in autotexts:
            at.set_color(_BG); at.set_fontsize(7.5); at.set_fontweight("bold")

        leg_labels = [f"{l}  ({v})" for l, v in zip(labels, sizes)]
        ax.legend(wedges, leg_labels, loc="lower left", fontsize=6.5,
                  labelcolor=_TEXT, framealpha=0, bbox_to_anchor=(-0.08, -0.18))
        ax.set_title("Historics: Record of Conquest", color=_TEXT, fontsize=8, pad=4)
        f.tight_layout()
        return f

    def _c1_cli_bar(self):
        df = self.df[self.df["labor_hours"] > 0].dropna(subset=["last_act"])
        if df.empty: return _s_empty("No Active Task Data")

        df = df.sort_values("last_act", ascending=False).head(7).copy()
        df["cli"] = (
            df["labor_hours"]
            * df["ef_cur"].clip(lower=1)
            * (df["progress_f"] / 100).clip(lower=0.01)
            * df["num_tags"].clip(lower=1)
            * df["nlp"]
        )
        mn, mx = df["cli"].min(), df["cli"].max()
        df["cli_norm"] = (df["cli"] - mn) / (mx - mn) * 9 + 1 if mx > mn else 5.0

        labels = [str(t)[:20] for t in df["Tasks"]]
        colors = [_S_COL.get(s, "#888") for s in df["Status"]]

        f  = _s_fig(4.5, 3.5)
        ax = f.add_subplot(111)
        _s_style(ax, "Cognitive Load Index  (Last 7 Active)", "", "CLI  (1–10)")

        bars = ax.barh(labels, df["cli_norm"].values, color=colors,
                       edgecolor=_BG, linewidth=0.5, height=0.62)
        ax.set_xlim(0, 12)
        for bar, v in zip(bars, df["cli_norm"].values):
            ax.text(v + 0.2, bar.get_y() + bar.get_height() / 2,
                    f"{v:.1f}", va="center", color=_TEXT, fontsize=6.5)
        ax.invert_yaxis()

        patches = [mpatches.Patch(color=_S_COL[s], label=s)
                   for s in df["Status"].unique() if s in _S_COL]
        ax.legend(handles=patches, fontsize=5.5, labelcolor=_TEXT,
                  framealpha=0.2, facecolor=_FRAME, edgecolor=_BORDER, loc="lower right")
        f.tight_layout()
        return f

    def _c1_labor_scatter(self):
        df = self.df[self.df["labor_hours"] > 0].dropna(subset=["last_act"])
        if df.empty: return _s_empty("No Active Task Data")

        df = df.sort_values("last_act", ascending=False).head(7).reset_index(drop=True)
        task_colors = {t: _PALETTE[i % len(_PALETTE)] for i, t in enumerate(df["Tasks"])}

        f  = _s_fig(4.5, 3.5)
        ax = f.add_subplot(111)
        _s_style(ax, "Labor·Time Drift  (Last 7 Active)", "Date", "Labor Hours")

        for _, row in df.iterrows():
            c  = task_colors[row["Tasks"]]
            x2 = row["last_act"]
            x1 = row["dt_init"] if row["dt_init"] else x2
            y  = row["labor_hours"]
            sz = max(row["progress_f"] * 1.8, 25)
            ax.plot([x1, x2], [y, y], color=c, alpha=0.35, lw=1.5, zorder=1)
            ax.scatter(x2, y, s=sz, color=c, edgecolors=_BG,
                       linewidths=0.5, zorder=3, alpha=0.92)
            ax.text(x2, y + 0.25, str(row["Tasks"])[:16],
                    color=c, fontsize=5.5, va="bottom")

        ax.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m"))
        plt.setp(ax.get_xticklabels(), rotation=35, ha="right", fontsize=6)

        patches = [mpatches.Patch(color=v, label=k[:20])
                   for k, v in task_colors.items()]
        ax.legend(handles=patches, fontsize=5.2, labelcolor=_TEXT,
                  framealpha=0.2, facecolor=_FRAME, edgecolor=_BORDER,
                  loc="upper left", ncol=1)
        f.tight_layout()
        return f

    def _c1_ef_priority(self):
        df = self.df.copy()

        f  = _s_fig(5.0, 3.8)
        ax = f.add_subplot(111)
        _s_style(ax, "Effort vs Priority  —  What Calls Next?",
                 "Priority", "Effort Points (Current)")

        for _, row in df.iterrows():
            c = _S_COL.get(row["Status"], "#888")
            ax.scatter(row["priority"], row["ef_cur"], color=c, s=48,
                       edgecolors=_BG, linewidths=0.5, alpha=0.85, zorder=3)

        for p_val, grp in df.groupby("priority"):
            top2 = grp.sort_values("ef_cur", ascending=False).head(2)
            for rank, (_, r) in enumerate(top2.iterrows()):
                ax.text(r["priority"] + 0.1, r["ef_cur"] + rank * 2.2,
                        str(r["Tasks"])[:18], color=_TEXT,
                        fontsize=5.1, va="bottom", alpha=0.88)

        ax.set_xticks(range(int(df["priority"].min()), int(df["priority"].max()) + 1))

        present = df["Status"].unique()
        patches = [mpatches.Patch(color=_S_COL.get(s, "#888"), label=s)
                   for s in present if s in _S_COL]
        ax.legend(handles=patches, fontsize=5.5, labelcolor=_TEXT,
                  framealpha=0.2, facecolor=_FRAME, edgecolor=_BORDER,
                  loc="upper left", ncol=2)

        recs = (df[df["Status"].isin(["Uninitiated", "Ongoing"])]
                .sort_values(["priority", "ef_cur"], ascending=[False, False])
                .head(3))
        if not recs.empty:
            rec_text = "↑ Next:\n" + "\n".join(
                f"  [{int(r['priority'])}] {str(r['Tasks'])[:22]}"
                for _, r in recs.iterrows()
            )
            ax.text(0.99, 0.03, rec_text, transform=ax.transAxes, color=_TEXT,
                    fontsize=5.5, va="bottom", ha="right",
                    bbox=dict(boxstyle="round,pad=0.35",
                              facecolor=_FRAME, edgecolor=_BORDER, alpha=0.92))
        f.tight_layout()
        return f

    # ══════════════════════════════════════════════════════════════════════════
    #  TAB II  –  Understanding Tags
    # ══════════════════════════════════════════════════════════════════════════

    def _build_tab_tags(self):
        top_bar = customtkinter.CTkFrame(self.tab_tags, fg_color="transparent", height=38)
        top_bar.pack(fill="x", padx=10, pady=(6, 0))

        customtkinter.CTkLabel(top_bar, text="View Mode:",
                               text_color=_MUTED, font=("", 12)
                               ).pack(side="left", padx=(6, 4))

        self._tag_toggle = customtkinter.CTkSegmentedButton(
            top_bar,
            values=["Grouped", "Individual"],
            fg_color="#0f0d1f",
            selected_color="#6a29c8",
            selected_hover_color="#8a4ee0",
            unselected_color="#0f0d1f",
            unselected_hover_color="#3a2f52",
            text_color="#c9c0e8",
            command=self._on_tag_mode_change,
        )
        self._tag_toggle.set("Grouped")
        self._tag_toggle.pack(side="left", padx=6)

        chart_area = customtkinter.CTkFrame(self.tab_tags, fg_color="transparent")
        chart_area.pack(fill="both", expand=True, padx=6, pady=4)
        chart_area.columnconfigure(0, weight=1); chart_area.columnconfigure(1, weight=1)
        chart_area.rowconfigure(0, weight=1);    chart_area.rowconfigure(1, weight=1)

        def _sect(row, col):
            bf  = customtkinter.CTkFrame(chart_area, fg_color=_BORDER, corner_radius=8)
            bf.grid(row=row, column=col, padx=6, pady=6, sticky="nsew")
            inf = customtkinter.CTkFrame(bf, fg_color=_BG, corner_radius=6)
            inf.pack(fill="both", expand=True, padx=2, pady=2)
            return inf

        self._tag_sec = {
            "tl": _sect(0, 0), "tr": _sect(0, 1),
            "bl": _sect(1, 0), "br": _sect(1, 1),
        }
        self._draw_tags_charts()

    def _on_tag_mode_change(self, val):
        self.tag_mode = val
        self._draw_tags_charts()

    def _tag_df(self):
        df = self.df.copy()
        if self.tag_mode == "Grouped":
            df = df.explode("tags_list").rename(columns={"tags_list": "tag"})
            df = df[df["tag"].notna()]
        else:
            df["tag"] = df["tags_list"].apply(lambda x: x[0] if x else "Untagged")
        return df

    def _draw_tags_charts(self):
        tdf = self._tag_df()
        s   = self._tag_sec
        _s_embed(self._c2_tag_priority(tdf), s["tl"])
        _s_embed(self._c2_tag_predtime(tdf), s["tr"])
        _s_embed(self._c2_tag_labor_ef(tdf), s["bl"])
        _s_embed(self._c2_tag_progress(tdf), s["br"])

    def _c2_tag_priority(self, tdf):
        grp = tdf.groupby("tag")["priority"].mean().sort_values(ascending=False)
        if grp.empty: return _s_empty()
        f  = _s_fig(4.5, 3.5); ax = f.add_subplot(111)
        _s_style(ax, f"Tags → Avg Priority  [{self.tag_mode}]", "Tag", "Avg Priority")
        bars = ax.bar(range(len(grp)), grp.values, color=_PALETTE[:len(grp)],
                      edgecolor=_BG, linewidth=0.5)
        ax.set_xticks(range(len(grp)))
        ax.set_xticklabels([t[:16] for t in grp.index], rotation=45, ha="right", fontsize=6)
        for bar, v in zip(bars, grp.values):
            ax.text(bar.get_x() + bar.get_width() / 2, v + 0.05,
                    f"{v:.1f}", ha="center", color=_TEXT, fontsize=6)
        f.tight_layout(); return f

    def _c2_tag_predtime(self, tdf):
        if tdf.empty: return _s_empty()
        tags  = sorted(tdf["tag"].unique())
        tag_x = {t: i for i, t in enumerate(tags)}
        task_colors = {t: _PALETTE[i % len(_PALETTE)]
                       for i, t in enumerate(tdf["Tasks"].unique())}
        f  = _s_fig(4.5, 3.5); ax = f.add_subplot(111)
        _s_style(ax, f"Tags → Prediction Time  [{self.tag_mode}]", "Tag", "Pred. Time (hrs)")
        for _, row in tdf.iterrows():
            ax.scatter(tag_x[row["tag"]], row["pred"],
                       color=task_colors.get(row["Tasks"], "#888"),
                       s=38, edgecolors=_BG, linewidths=0.4, alpha=0.82)
        for tag, mean_v in tdf.groupby("tag")["pred"].mean().items():
            xi = tag_x[tag]
            ax.plot([xi - 0.3, xi + 0.3], [mean_v, mean_v],
                    color="#ffd93d", lw=2.0, zorder=4)
        ax.set_xticks(list(tag_x.values()))
        ax.set_xticklabels([t[:14] for t in tag_x], rotation=45, ha="right", fontsize=6)
        f.tight_layout(); return f

    def _c2_tag_labor_ef(self, tdf):
        if tdf.empty: return _s_empty()
        tags = sorted(tdf["tag"].unique())
        tag_markers = ["o","s","^","D","P","*","X","h","v","<"]
        tag_idx = {t: i for i, t in enumerate(tags)}
        task_colors = {t: _PALETTE[i % len(_PALETTE)]
                       for i, t in enumerate(tdf["Tasks"].unique())}
        f  = _s_fig(4.5, 3.5); ax = f.add_subplot(111)
        _s_style(ax, f"Tags → Labor & Effort  [{self.tag_mode}]",
                 "Labor Hours", "Effort Points")
        for _, row in tdf.iterrows():
            mk = tag_markers[tag_idx[row["tag"]] % len(tag_markers)]
            ax.scatter(row["labor_hours"], row["ef_cur"],
                       color=task_colors.get(row["Tasks"], "#888"),
                       marker=mk, s=48, edgecolors=_BG, linewidths=0.4, alpha=0.82)
        for tag in tags:
            sub = tdf[tdf["tag"] == tag]
            cx, cy = sub["labor_hours"].mean(), sub["ef_cur"].mean()
            ax.text(cx, cy + 0.6, tag[:14], color=_TEXT,
                    fontsize=5.2, ha="center", va="bottom", alpha=0.75)
        f.tight_layout(); return f

    def _c2_tag_progress(self, tdf):
        grp = tdf.groupby("tag")["progress_f"].mean().sort_values(ascending=False)
        if grp.empty: return _s_empty()
        f  = _s_fig(4.5, 3.5); ax = f.add_subplot(111)
        _s_style(ax, f"Tags → Avg Progress  [{self.tag_mode}]", "Tag", "Avg Progress (%)")
        bars = ax.bar(range(len(grp)), grp.values, color=_PALETTE[:len(grp)],
                      edgecolor=_BG, linewidth=0.5)
        ax.set_xticks(range(len(grp)))
        ax.set_xticklabels([t[:16] for t in grp.index], rotation=45, ha="right", fontsize=6)
        ax.set_ylim(0, 115)
        ax.axhline(100, color="#ffd93d", lw=0.9, ls="--", alpha=0.55)
        for bar, v in zip(bars, grp.values):
            ax.text(bar.get_x() + bar.get_width() / 2, v + 1.5,
                    f"{v:.0f}%", ha="center", color=_TEXT, fontsize=6)
        f.tight_layout(); return f

    # ══════════════════════════════════════════════════════════════════════════
    #  TAB III  –  Hall of Halts and Drops
    # ══════════════════════════════════════════════════════════════════════════

    def _build_tab_halts(self):
        hd = self.df[self.df["Status"].isin(["Halted", "Dropped"])].copy()
        s  = self._quads(self.tab_halts)
        _s_embed(self._c3_summary(hd),        s["tl"])
        _s_embed(self._c3_labor_dates(hd),    s["tr"])
        _s_embed(self._c3_common_tags(hd),    s["bl"])
        _s_embed(self._c3_progress_dates(hd), s["br"])

    def _c3_summary(self, hd):
        if hd.empty: return _s_empty("No Halt / Drop Data")
        metrics  = ["ef_cur", "pred", "labor_hours", "halt_days"]
        labels   = ["Effort Pts", "Pred. Time", "Labor Hrs", "Halt Days"]
        statuses = hd["Status"].unique()
        colors   = {"Halted": "#ffd93d", "Dropped": "#ff6b6b"}
        x = np.arange(len(metrics)); w = 0.35
        f  = _s_fig(4.5, 3.5); ax = f.add_subplot(111)
        _s_style(ax, "Halt & Drop — Mean Vitals", "Metric", "Avg Value")
        for idx, status in enumerate(statuses):
            sub    = hd[hd["Status"] == status]
            vals   = [sub[m].mean() for m in metrics]
            offset = (idx - (len(statuses) - 1) / 2) * w
            bars   = ax.bar(x + offset, vals, w, label=status,
                            color=colors.get(status, _PALETTE[idx]),
                            edgecolor=_BG, linewidth=0.5)
            for bar, v in zip(bars, vals):
                ax.text(bar.get_x() + bar.get_width() / 2, v + 0.3,
                        f"{v:.1f}", ha="center", va="bottom", color=_TEXT, fontsize=5.8)
        ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=7)
        ax.legend(fontsize=6, labelcolor=_TEXT, framealpha=0.2,
                  facecolor=_FRAME, edgecolor=_BORDER)
        f.tight_layout(); return f

    def _c3_labor_dates(self, hd):
        sub = hd.dropna(subset=["last_act"])
        if sub.empty: return _s_empty("No Date Data")
        f  = _s_fig(4.5, 3.5); ax = f.add_subplot(111)
        _s_style(ax, "Labor Hours over Time  [Halt / Drop]",
                 "Last Activity", "Labor Hours")
        for _, row in sub.iterrows():
            c = _S_COL.get(row["Status"], "#888")
            ax.scatter(row["last_act"], row["labor_hours"], color=c, s=68,
                       edgecolors=_BG, linewidths=0.6, zorder=3, alpha=0.92)
            ax.text(row["last_act"], row["labor_hours"],
                    f"  {str(row['Tasks'])[:14]}", color=c, fontsize=5.3, va="center")
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m"))
        plt.setp(ax.get_xticklabels(), rotation=35, ha="right", fontsize=6)
        patches = [mpatches.Patch(color=_S_COL[s], label=s)
                   for s in ["Halted", "Dropped"] if s in _S_COL]
        ax.legend(handles=patches, fontsize=6, labelcolor=_TEXT,
                  framealpha=0.2, facecolor=_FRAME, edgecolor=_BORDER)
        f.tight_layout(); return f

    def _c3_common_tags(self, hd):
        if hd.empty: return _s_empty("No Halt / Drop Data")
        halted_cnt  = Counter(t for lst in hd[hd["Status"]=="Halted"]["tags_list"]  for t in lst)
        dropped_cnt = Counter(t for lst in hd[hd["Status"]=="Dropped"]["tags_list"] for t in lst)
        all_tags = sorted(set(list(halted_cnt) + list(dropped_cnt)))
        x = np.arange(len(all_tags)); w = 0.38
        f  = _s_fig(5.0, 3.5); ax = f.add_subplot(111)
        _s_style(ax, "Common Tags  —  Halt vs Drop", "Tag", "Frequency")
        ax.bar(x - w/2, [halted_cnt.get(t, 0)  for t in all_tags], w,
               label="Halted",  color="#ffd93d", edgecolor=_BG, linewidth=0.5)
        ax.bar(x + w/2, [dropped_cnt.get(t, 0) for t in all_tags], w,
               label="Dropped", color="#ff6b6b", edgecolor=_BG, linewidth=0.5)
        ax.set_xticks(x)
        ax.set_xticklabels([t[:16] for t in all_tags], rotation=45, ha="right", fontsize=6)
        ax.yaxis.set_major_locator(plt.MaxNLocator(integer=True))
        ax.legend(fontsize=6.5, labelcolor=_TEXT, framealpha=0.2,
                  facecolor=_FRAME, edgecolor=_BORDER)
        f.tight_layout(); return f

    def _c3_progress_dates(self, hd):
        sub = hd.dropna(subset=["last_act"])
        if sub.empty: return _s_empty("No Date Data")
        f  = _s_fig(4.5, 3.5); ax = f.add_subplot(111)
        _s_style(ax, "Progress over Time  [Halt / Drop]",
                 "Last Activity", "Progress (%)")
        for _, row in sub.iterrows():
            c = _S_COL.get(row["Status"], "#888")
            ax.scatter(row["last_act"], row["progress_f"], color=c, s=68,
                       edgecolors=_BG, linewidths=0.6, zorder=3, alpha=0.92)
            ax.text(row["last_act"], row["progress_f"],
                    f"  {str(row['Tasks'])[:14]}", color=c, fontsize=5.3, va="center")
        ax.set_ylim(0, 108)
        ax.axhline(100, color=_MUTED, lw=0.7, ls="--", alpha=0.5)
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m"))
        plt.setp(ax.get_xticklabels(), rotation=35, ha="right", fontsize=6)
        patches = [mpatches.Patch(color=_S_COL[s], label=s)
                   for s in ["Halted", "Dropped"] if s in _S_COL]
        ax.legend(handles=patches, fontsize=6, labelcolor=_TEXT,
                  framealpha=0.2, facecolor=_FRAME, edgecolor=_BORDER)
        f.tight_layout(); return f

    # ══════════════════════════════════════════════════════════════════════════
    #  TAB IV  –  Is this end or Should we Transcend?
    # ══════════════════════════════════════════════════════════════════════════

    def _build_tab_transcend(self):
        cd = self.df[self.df["Status"].isin(["Completed", "Post Completion"])].copy()
        s  = self._quads(self.tab_transcend)
        _s_embed(self._c4_lifecycle(cd),  s["tl"])
        _s_embed(self._c4_summary(cd),    s["tr"])
        _s_embed(self._c4_bubble(cd),     s["bl"])
        _s_embed(self._c4_tags_comp(cd),  s["br"])

    def _c4_lifecycle(self, cd):
        sub = cd.dropna(subset=["dt_comp"]).sort_values("dt_comp", ascending=False).head(4)
        if sub.empty: return _s_empty("No Completed Task Data")
        f  = _s_fig(5.5, 3.8); ax = f.add_subplot(111)
        _s_style(ax, "Lifecycle Breakdown  (Last 4 Completed)", "", "Days")
        y_pos = np.arange(len(sub))
        seen_labels = set()
        for i, (_, row) in enumerate(sub.iterrows()):
            pre_d, active_d, halt_d = 0, 0, float(row["halt_days"])
            if row["dt_decl"] and row["dt_init"]:
                pre_d = max((row["dt_init"] - row["dt_decl"]).days, 0)
            if row["dt_init"] and row["dt_comp"]:
                total    = max((row["dt_comp"] - row["dt_init"]).days, 0)
                active_d = max(total - halt_d, 0)
            left = 0
            for val, col, lbl in [
                (pre_d,   "#4d96ff", "Pre-Init"),
                (active_d,"#6bcb77", "Active"),
                (halt_d,  "#ffd93d", "Halted"),
            ]:
                if val > 0:
                    kw_label = lbl if lbl not in seen_labels else "_nolegend_"
                    seen_labels.add(lbl)
                    ax.barh(i, val, left=left, color=col, edgecolor=_BG,
                            linewidth=0.4, height=0.55, label=kw_label)
                    ax.text(left + val / 2, i, f"{val:.0f}d",
                            ha="center", va="center", color=_BG, fontsize=6, fontweight="bold")
                    left += val
            ann = (f"  EF:{int(row['ef_cur'])}  Pred:{row['pred']:.0f}h  "
                   f"Labor:{row['labor_hours']:.1f}h  ↑{row['progress_f']:.0f}%")
            ax.text(left + 0.2, i, ann, color=_MUTED, fontsize=5.2, va="center")
        ax.set_yticks(y_pos)
        ax.set_yticklabels([str(t)[:26] for t in sub["Tasks"]], fontsize=6.5)
        ax.legend(fontsize=5.5, labelcolor=_TEXT, framealpha=0.2,
                  facecolor=_FRAME, edgecolor=_BORDER, loc="lower right")
        f.tight_layout(); return f

    def _c4_summary(self, cd):
        if cd.empty: return _s_empty("No Completed Task Data")
        comp_days_vals = cd["comp_days"].dropna()
        metrics = {
            "Effort Pts": cd["ef_cur"].mean(),
            "Pred Time":  cd["pred"].mean(),
            "Labor Hrs":  cd["labor_hours"].mean(),
            "Comp Days":  comp_days_vals.mean() if len(comp_days_vals) > 0 else 0,
        }
        bar_colors = ["#a78bfa", "#e040fb", "#6bcb77", "#00bcd4"]
        f  = _s_fig(4.5, 3.5); ax = f.add_subplot(111)
        _s_style(ax, "Completion — Mean Vitals", "Metric", "Avg Value")
        bars = ax.bar(metrics.keys(), metrics.values(),
                      color=bar_colors, edgecolor=_BG, linewidth=0.6)
        y_max = max(metrics.values()) if metrics else 1
        for bar, v in zip(bars, metrics.values()):
            ax.text(bar.get_x() + bar.get_width() / 2, v + y_max * 0.015,
                    f"{v:.1f}", ha="center", color=_TEXT, fontsize=7)
        for status, grp in cd.groupby("Status"):
            color = _S_COL.get(status, "#888")
            ax.text(0.98, 0.97 - list(cd["Status"].unique()).index(status) * 0.09,
                    f"● {status}: {len(grp)}", transform=ax.transAxes,
                    color=color, fontsize=6, ha="right", va="top")
        f.tight_layout(); return f

    def _c4_bubble(self, cd):
        sub = cd.dropna(subset=["comp_days"])
        if sub.empty: return _s_empty("No Completion Date Data")
        f  = _s_fig(4.5, 3.5); ax = f.add_subplot(111)
        _s_style(ax, "Priority × Comp. Time × Effort",
                 "Priority", "Completion Days")
        sc = ax.scatter(sub["priority"], sub["comp_days"],
                        s=sub["ef_cur"] * 5, c=sub["ef_cur"],
                        cmap="plasma", alpha=0.82,
                        edgecolors=_BG, linewidths=0.6)
        cb = f.colorbar(sc, ax=ax, pad=0.02, shrink=0.85)
        cb.ax.tick_params(colors=_TEXT, labelsize=6)
        cb.set_label("Effort Points", color=_TEXT, fontsize=6)
        for _, row in sub.iterrows():
            ax.text(row["priority"] + 0.07, row["comp_days"],
                    str(row["Tasks"])[:16], color=_TEXT, fontsize=5.2, va="center")
        ax.set_xticks(range(int(sub["priority"].min()), int(sub["priority"].max()) + 1))
        f.tight_layout(); return f

    def _c4_tags_comp(self, cd):
        if cd.empty: return _s_empty("No Completed Task Data")
        grp_counts = Counter(t for lst in cd["tags_list"] for t in lst)
        ind_counts = Counter(lst[0] for lst in cd["tags_list"] if lst)
        all_tags = sorted(set(list(grp_counts) + list(ind_counts)))
        x = np.arange(len(all_tags)); w = 0.38
        f  = _s_fig(5.0, 3.5); ax = f.add_subplot(111)
        _s_style(ax, "Tags → Completion Count  [Both Views]", "Tag", "Task Count")
        ax.bar(x - w/2, [grp_counts.get(t, 0) for t in all_tags], w,
               label="Grouped",    color="#a78bfa", edgecolor=_BG, linewidth=0.5)
        ax.bar(x + w/2, [ind_counts.get(t, 0) for t in all_tags], w,
               label="Individual", color="#6bcb77", edgecolor=_BG, linewidth=0.5)
        ax.set_xticks(x)
        ax.set_xticklabels([t[:16] for t in all_tags], rotation=45, ha="right", fontsize=6)
        ax.yaxis.set_major_locator(plt.MaxNLocator(integer=True))
        ax.legend(fontsize=6.5, labelcolor=_TEXT, framealpha=0.2,
                  facecolor=_FRAME, edgecolor=_BORDER)
        f.tight_layout(); return f
        





class mains_screen(customtkinter.CTkFrame):
    def __init__(self,master):
        super().__init__(master)
        greetings_options=["Greetings","Salutations","Evenings"]
        selected_greeting = random.choice(greetings_options)
        self.greetings = customtkinter.CTkLabel(self,text=selected_greeting,font=("Lexend",36))
        self.greetings.place(relx=0.5,rely=0.3,anchor="center")


class tabview(customtkinter.CTkTabview):
    def __init__(self,master):
        super().__init__(master)
        self.add("Main Screen")
        self.add("Task Addendum")
        self.add("Modification of Task")
        self.add("Stats and others")
        self.configure(
            fg_color="#b2b5b1",
            segmented_button_fg_color = "black",
            segmented_button_unselected_color="black",
            segmented_button_unselected_hover_color = "#756b6b",
            segmented_button_selected_color="#29c820",
            segmented_button_selected_hover_color="#5ec879",
            text_color="#ffffff",
            anchor="center"
        )
        
        self.main_frame = mains_screen(master=self.tab("Main Screen"))
        self.main_frame.pack(expand=True, fill="both")

        self.add_frame = add_tasks(master=self.tab("Task Addendum"))
        self.add_frame.pack(expand=True, fill="both")

        self.modify_frame = modify_tasks(master=self.tab("Modification of Task"))
        self.modify_frame.pack(expand=True, fill="both")

        self.stats_frame = stats(master=self.tab("Stats and others"))
        self.stats_frame.pack(expand=True, fill="both")


class logger(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("Task Logger")
        self.configure(fg_color="#b2b5b1")
        self.minsize(1040, 650)
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        center_x = int(screen_width / 2 - 1040 / 2)
        center_y = int(screen_height / 2 - 650 / 2)
        self.geometry(f'{1040}x{650}+{center_x}+{center_y}')
        
        self.universal_font = customtkinter.CTkFont(family="Lexend", size=12, weight="normal")
        
        self.tab_view = tabview(master=self)
        self.tab_view.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.95, relheight=0.95)


data_path = os.path.expanduser("~/Tasks/Timeline-Tasks.csv")
desc_path = os.path.expanduser("~/Tasks/Timeline-Tasks-Desc.txt")

data=pd.read_csv(data_path)
data_header=list(data.columns)
data_df = pd.DataFrame(columns=data_header)

add_data = dict.fromkeys(data_header, None)

desc_list = []

with open(desc_path, 'r') as f:
    for line in f:
        desc_list.append(line.strip())    


app=logger()
app.mainloop()


"""
Tasks/
│
├── main.py                  ← entry point only. loads CSV, creates AppState, launches logger
│
├── app_state.py             ← AppState class. holds data_df, data_path, notifies listeners
│                               replaces every `global data_df`
│
├── views/
│   ├── main_screen.py       ← mains_screen, tabview, logger  (they're tiny, live together)
│   ├── add_tasks.py         ← add_tasks class
│   ├── modify_tasks.py      ← modify_tasks class
│   │
│   └── stats/
│       ├── __init__.py      ← exports stats class
│       ├── stats_frame.py   ← stats class itself, _quads, tab builders, toggle logic
│       ├── data_prep.py     ← _s_prepare, all parsing helpers, palette constants
│       └── chart_builders.py← all _c1_ _c2_ _c3_ _c4_ methods as static functions
│                               receiving df and returning a Figure
"""
