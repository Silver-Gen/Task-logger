import pandas as pd
import numpy as np
import random
from collections import defaultdict, Counter
from datetime import date, datetime
import os
import sys
import tkinter as tk
from tkinter import simpledialog, messagebox


# ── Parsers ───────────────────────────────────────────────────────────────────
# Time_Taken_Until: PreInitiationPeriod _ Labor1 _ Labor2... _ PredictionAccuracy _ HaltingTime
# Dates:            Declaration _ Initiation _ Ongoing1 _ Ongoing2... _ Halt _ Completion
# Both have variable middles — cannot use str.split(expand=True)

def parse_time_taken(s):
    parts = s.split("_")
    return {
        "PreInitiationPeriod" : parts[0],
        "Labor"               : "_".join(parts[1:-2]),  # "" if only one session slot (fresh task)
        "PredictionAccuracy"  : parts[-2],
        "HaltingTime"         : parts[-1]
    }

def parse_dates(s):
    parts = s.split("_")
    return {
        "Date_Declaration" : parts[0],
        "Date_Initiation"  : parts[1],
        "Date_Ongoing"     : "_".join(parts[2:-2]),     # "" if uninitiated
        "Date_Halt"        : parts[-2],
        "Date_Completion"  : parts[-1]
    }


def parse_time(raw_time: str):
    """Reduce a time string — dot or colon delimited — to a time object."""
    return datetime.strptime(raw_time.replace(":", "."), "%H.%M").time()

# ── Rebuilders ────────────────────────────────────────────────────────────────

def rebuild_time_taken(row):
    base = row["PreInitiationPeriod"]
    if row["Labor"]:
        base += f"_{row['Labor']}"
    base += f"_{row['PredictionAccuracy']}_{row['HaltingTime']}"
    return base

def rebuild_dates(row):
    base = f"{row['Date_Declaration']}_{row['Date_Initiation']}"
    if row["Date_Ongoing"]:
        base += f"_{row['Date_Ongoing']}"
    base += f"_{row['Date_Halt']}_{row['Date_Completion']}"
    return base


def to_minutes(t) -> float:
    """Reduce a time object to its numerical soul — total minutes."""
    return t.hour * 60 + t.minute




# ── Load ──────────────────────────────────────────────────────────────────────

data_path = os.path.expanduser("~/Tasks/Timeline-Tasks.csv")
data = pd.read_csv(data_path)

data_df = data[["Tasks", "Status", "Time_Taken_Until", "Dates",
                "Estimated_Effort_Points", "Progress_Till", "Prediction_Time"]].copy()

# Variable-middle columns — must use row-wise parse functions
parsed_time  = data_df["Time_Taken_Until"].apply(parse_time_taken).apply(pd.Series)
parsed_dates = data_df["Dates"].apply(parse_dates).apply(pd.Series)

# Fixed 3-part column — str.split(expand=True) is safe here
parsed_eef = data_df["Estimated_Effort_Points"].str.split("_", expand=True)
parsed_eef.columns = ["EEF_I", "EEF_H", "EEF_C"]

data_df = pd.concat([data_df, parsed_time, parsed_dates, parsed_eef], axis=1)

today = date.today().strftime('%d/%m/%Y')   # 4-digit year — new writes always consistent
fmt   = "%d/%m/%Y"                          # canonical format going forward

def to_dt(s):
    """
    Parse a date string that may be either '%d/%m/%Y' (4-digit year,
    canonical) or '%d/%m/%y' (2-digit year, legacy entries written before
    this fix).  format='mixed' with dayfirst=True lets pandas infer each
    element individually, surviving both variants without raising.
    """
    return pd.to_datetime(s, dayfirst=True, format='mixed')

mode = sys.argv[1] if len(sys.argv) > 1 else None
# T - Time Update   : python updater.py T <HH.MM> <progress> "Task Name"
# R - Regular Update: python updater.py R
# C - Completion    : python updater.py C <HH.MM> <progress> "Task Name"

match mode:

    case "T":
        raw_time = sys.argv[2]
        progress = int(sys.argv[3])
        name     = sys.argv[4]

        parsed_t = parse_time(raw_time)
        parsed_minutes = to_minutes(parsed_t)

        existing_raw     = data_df.loc[data_df["Tasks"] == name, "Prediction_Time"].values[0]
        existing_minutes = float(existing_raw) * 60
        ratio            = parsed_minutes / existing_minutes

        current_progress = int(data_df.loc[data_df["Tasks"] == name, "Progress_Till"].values[0])
        new_progress     = current_progress + progress
        current_labor    = data_df.loc[data_df["Tasks"] == name, "Labor"].values[0]

        data_df.loc[data_df["Tasks"] == name, "PredictionAccuracy"] = round(ratio, 4)
        data_df.loc[data_df["Tasks"] == name, "Progress_Till"]      = new_progress

        if data_df.loc[data_df["Tasks"] == name, "Status"].values[0] == "Uninitiated":
            data_df.loc[data_df["Tasks"] == name, "Status"]          = "Ongoing"
            data_df.loc[data_df["Tasks"] == name, "Date_Initiation"] = today
            data_df.loc[data_df["Tasks"] == name, "Date_Ongoing"]    = today
            data_df.loc[data_df["Tasks"] == name, "Labor"]           = raw_time
        else:
            # Append new labor session
            data_df.loc[data_df["Tasks"] == name, "Labor"] = (
                current_labor + f"_{raw_time}" if current_labor else raw_time
            )
            current_ongoing = data_df.loc[data_df["Tasks"] == name, "Date_Ongoing"].values[0]
            data_df.loc[data_df["Tasks"] == name, "Date_Ongoing"] = (
                current_ongoing + f"_{today}" if current_ongoing else today
            )


    case "R":
        today_dt = to_dt(today)

        # ── Uninitiated: growing pre-initiation wait time ──────────────────
        mask_uninit = data_df["Status"] == "Uninitiated"
        data_df.loc[mask_uninit, "PreInitiationPeriod"] = (
            today_dt - to_dt(data_df.loc[mask_uninit, "Date_Declaration"])
        ).dt.days.astype(str)

        # ── Halted: accumulate halting duration, drop if >90 ──────────────
        mask_halted = data_df["Status"] == "Halted"
        data_df.loc[mask_halted, "HaltingTime"] = (
            today_dt - to_dt(data_df.loc[mask_halted, "Date_Halt"])
        ).dt.days.astype(str)

        mask_drop = mask_halted & (data_df["HaltingTime"].astype(float) > 90)
        data_df.loc[mask_drop, "Status"] = "Dropped"

        # ── Ongoing: check idle days, halt if >21 ─────────────────────────
        mask_ongoing = data_df["Status"] == "Ongoing"
        for idx, row in data_df[mask_ongoing].iterrows():
            ongoing_raw = row["Date_Ongoing"]
            if not ongoing_raw:
                continue

            last_active_str = ongoing_raw.split("_")[-1]
            last_active_dt  = to_dt(last_active_str)
            idle_days       = (today_dt - last_active_dt).days

            if idle_days > 21:
                task_name = row["Tasks"]
                data_df.loc[idx, "Status"]      = "Halted"
                data_df.loc[idx, "Date_Halt"]   = today
                data_df.loc[idx, "HaltingTime"] = "0"

                root = tk.Tk()
                root.withdraw()
                ef_value = simpledialog.askstring(
                    title="Task Halted",
                    prompt=f'"{task_name}" has halted due to inactivity ({idle_days} days).\nState EF Halt value:'
                )
                root.destroy()

                if ef_value is not None:
                    data_df.loc[idx, "EEF_H"] = ef_value.strip()


    case "C":
        raw_time = sys.argv[2]
        progress = int(sys.argv[3])
        name     = sys.argv[4]

        current_status = data_df.loc[data_df["Tasks"] == name, "Status"].values[0]

        if current_status == "Ongoing":
            parsed_t       = parse_time(raw_time)
            parsed_minutes = to_minutes(parsed_t)

            existing_raw     = data_df.loc[data_df["Tasks"] == name, "Prediction_Time"].values[0]
            existing_minutes = float(existing_raw) * 60
            ratio            = parsed_minutes / existing_minutes

            current_progress = int(data_df.loc[data_df["Tasks"] == name, "Progress_Till"].values[0])
            new_progress     = current_progress + progress
            current_labor    = data_df.loc[data_df["Tasks"] == name, "Labor"].values[0]

            data_df.loc[data_df["Tasks"] == name, "Labor"] = (
                current_labor + f"_{raw_time}" if current_labor else raw_time
            )
            data_df.loc[data_df["Tasks"] == name, "PredictionAccuracy"] = round(ratio, 4)
            data_df.loc[data_df["Tasks"] == name, "Progress_Till"]      = new_progress

            # Date_Ongoing is NOT touched — completion does not append a session date
            data_df.loc[data_df["Tasks"] == name, "Status"]          = "Completed"
            data_df.loc[data_df["Tasks"] == name, "Date_Completion"] = today

            root = tk.Tk()
            root.withdraw()
            ef_value = simpledialog.askstring(
                title="Task Completed",
                prompt=f'"{name}" has been marked as Completed.\nState EF Completion value:'
            )
            root.destroy()

            if ef_value is not None:
                data_df.loc[data_df["Tasks"] == name, "EEF_C"] = ef_value.strip()

        else:
            root = tk.Tk()
            root.withdraw()
            messagebox.showwarning(
                title="Cannot Complete Task",
                message=f'"{name}" cannot be completed.\nCurrent status: {current_status}\n\nOnly Ongoing tasks may be completed.'
            )
            root.destroy()
            sys.exit(0)


    case _:
        print("Unknown mode. Use T, R, or C.")
        sys.exit(0)


# ── Reconstruct compound columns and save ────────────────────────────────────

data_df["Time_Taken_Until"] = data_df.apply(rebuild_time_taken, axis=1)

data_df["Estimated_Effort_Points"] = (
    data_df["EEF_I"] + "_" +
    data_df["EEF_H"] + "_" +
    data_df["EEF_C"]
)

data_df["Dates"] = data_df.apply(rebuild_dates, axis=1)

cols_to_save = ["Status", "Time_Taken_Until", "Dates",
                "Estimated_Effort_Points", "Progress_Till", "Prediction_Time"]

for col in cols_to_save:
    data[col] = data_df.set_index("Tasks")[col].reindex(data["Tasks"]).values

data.to_csv(data_path, index=False)
