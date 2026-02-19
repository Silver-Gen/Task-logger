// Size of Screen would be 60x28

// 3 Menu options - 1) Work 2) Open GUI 3) Update Logger
/*
1) -> 1) Choose from following Three tables - <Show Uninitiated, Active and Halted Tasks>    ----> Selects Task and then which moves to Timer Screen
What is on the Timer screen - Name of Task at the Top 
Timer in HH:MM (Hours:Minutes) at the middle of screen
Followed by three options 
1) Start /Play
2) Pause 
3) End
 
 Stat - Starts the Timer from 00:00 Play resumes the timer to whatever is last position
 Pause - Pauses the timer
 End - Ends the Timer which leads to next page. If this is clicked the Value of timer is stored.
 
Session End Page Shall be something like
<Task name> : Time Spent on <Today's Date> 
Please enter the Estimated progress here ? 
Has the Task finished? - (A check box)


This screen takes in a number and on the basis of the checkbox result will run the Bash functional command
 
 If the checkbox is False - add_session <value of timer> <value Estimated progress> <Task Name>
 If the Checkbox is true - complete_task <value of timer> <value Estimated progress> <Task Name>

This ends the session and return to main menu


2) -> Runs a bash exec called logger_gui



3) Runs a bash exec called update_logger
*/

/*
 * daily_logger.c
 * A terminal-based task timer and session logger.
 * Compile: gcc -o daily_logger daily_logger.c -lncurses -lpanel
 *
 * Dependencies:
 *   libncurses
 *   ~/Tasks/Timeline-Tasks.csv   -- comma-separated, must have
 *                                   "Tasks" and "Status" columns.
 *                                   Status values shown in Work screen:
 *                                   Uninitiated | Ongoing | Halted
 *   add_session    <HH:MM> <progress%> <task>  (bash function in ~/.bashrc)
 *   complete_task  <HH:MM> <progress%> <task>  (bash function in ~/.bashrc)
 *   logger_gui     (bash function in ~/.bashrc)
 *   update_logger  (bash function in ~/.bashrc)
 *
 * NOTE: bash functions are NOT visible to system(). All shell calls are
 *       wrapped as: bash -c 'source ~/.bashrc && <function> [args]'
 */

#include <ncurses.h>
#include <panel.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>

/* ──────────────────────────────────────────────────────────────
 * Constants
 * ────────────────────────────────────────────────────────────── */
#define SW           60
#define SH           28
#define MAX_TASKS    64
#define TASK_LEN     128

/* ──────────────────────────────────────────────────────────────
 * Global state
 * ────────────────────────────────────────────────────────────── */
static char g_uninitiated[MAX_TASKS][TASK_LEN];
static char g_active[MAX_TASKS][TASK_LEN];
static char g_halted[MAX_TASKS][TASK_LEN];
static int  g_uninit_cnt, g_active_cnt, g_halted_cnt;

static char g_selected_task[TASK_LEN];

/* ──────────────────────────────────────────────────────────────
 * Utilities
 * ────────────────────────────────────────────────────────────── */

#define CSV_PATH  "Tasks/Timeline-Tasks.csv"   /* relative to $HOME */
#define CSV_LINEBUF 1024

/*
 * csv_next_field: RFC 4180-aware field extractor.
 *
 * Handles quoted fields such as "['C', 'Bash', 'Hobby']" where
 * commas inside double-quotes are part of the value, not separators.
 * Also handles "" as an escaped literal double-quote inside a quoted
 * field.  Strips the surrounding quotes from quoted fields.
 * Strips trailing '\n'/'\r' from the final field of a line.
 *
 * Returns 0 only when *p points to '\0' (line fully consumed).
 */
static int csv_next_field(const char **p, char *out, int outsz)
{
    if (!*p || **p == '\0') return 0;

    const char *src = *p;
    int i = 0;

    if (*src == '"') {
        /* Quoted field */
        src++;
        while (*src) {
            if (*src == '"') {
                if (*(src + 1) == '"') {
                    /* escaped "" -> literal " */
                    if (i < outsz - 1) out[i++] = '"';
                    src += 2;
                } else {
                    src++; /* closing quote */
                    break;
                }
            } else {
                if (i < outsz - 1) out[i++] = *src;
                src++;
            }
        }
        if (*src == ',') src++;
    } else {
        /* Unquoted field */
        while (*src && *src != ',') {
            if (i < outsz - 1) out[i++] = *src;
            src++;
        }
        if (*src == ',') src++;
    }

    out[i] = '\0';

    /* strip trailing CR/LF (final field of a line) */
    while (i > 0 && (out[i-1] == '\n' || out[i-1] == '\r'))
        out[--i] = '\0';

    *p = src;
    return 1;
}

/*
 * csv_field_at: given a raw CSV line, return the field at `target_col`
 * into `out`.  Returns 1 on success, 0 if column does not exist.
 */
static int csv_field_at(const char *line, int target_col,
                        char *out, int outsz)
{
    const char *p = line;
    char cell[CSV_LINEBUF];
    int col = 0;

    while (csv_next_field(&p, cell, sizeof(cell))) {
        if (col == target_col) {
            snprintf(out, outsz, "%s", cell);
            return 1;
        }
        col++;
    }
    return 0;
}

/*
 * refresh_tasks: parse ~/Tasks/Timeline-Tasks.csv and populate the
 * three global task arrays.
 *
 * Only tasks with Status == "Uninitiated" | "Ongoing" | "Halted"
 * are surfaced in the Work screen.  All other statuses (Dropped,
 * Completed, Post Completion) are silently skipped — they belong
 * to the past.
 */
static void refresh_tasks(void)
{
    g_uninit_cnt = 0;
    g_active_cnt = 0;
    g_halted_cnt = 0;

    /* Build full path: $HOME/Tasks/Timeline-Tasks.csv */
    const char *home = getenv("HOME");
    if (!home) home = ".";
    char path[512];
    snprintf(path, sizeof(path), "%s/%s", home, CSV_PATH);

    FILE *fp = fopen(path, "r");
    if (!fp) return;  /* silently degrade — no tasks shown */

    char line[CSV_LINEBUF];
    int task_col   = -1;
    int status_col = -1;
    int is_header  =  1;

    while (fgets(line, sizeof(line), fp)) {

        /* ── Header row: find column indices ── */
        if (is_header) {
            is_header = 0;
            const char *p = line;
            char cell[CSV_LINEBUF];
            int col = 0;
            while (csv_next_field(&p, cell, sizeof(cell))) {
                if (strcmp(cell, "Tasks")  == 0) task_col   = col;
                if (strcmp(cell, "Status") == 0) status_col = col;
                col++;
            }
            /* If we can't locate the required columns, abort */
            if (task_col < 0 || status_col < 0) break;
            continue;
        }

        /* ── Data rows ── */
        char task_name[TASK_LEN];
        char status_val[TASK_LEN];

        if (!csv_field_at(line, task_col,   task_name,  TASK_LEN)) continue;
        if (!csv_field_at(line, status_col, status_val, TASK_LEN)) continue;
        if (task_name[0] == '\0') continue;  /* blank task — skip */

        if (strcmp(status_val, "Uninitiated") == 0 &&
            g_uninit_cnt < MAX_TASKS) {
            strncpy(g_uninitiated[g_uninit_cnt], task_name, TASK_LEN - 1);
            g_uninitiated[g_uninit_cnt][TASK_LEN - 1] = '\0';
            g_uninit_cnt++;

        } else if (strcmp(status_val, "Ongoing") == 0 &&
                   g_active_cnt < MAX_TASKS) {
            strncpy(g_active[g_active_cnt], task_name, TASK_LEN - 1);
            g_active[g_active_cnt][TASK_LEN - 1] = '\0';
            g_active_cnt++;

        } else if (strcmp(status_val, "Halted") == 0 &&
                   g_halted_cnt < MAX_TASKS) {
            strncpy(g_halted[g_halted_cnt], task_name, TASK_LEN - 1);
            g_halted[g_halted_cnt][TASK_LEN - 1] = '\0';
            g_halted_cnt++;
        }
        /* Dropped / Completed / Post Completion — intentionally ignored */
    }

    fclose(fp);
}

/* ──────────────────────────────────────────────────────────────
 * bash_run: execute a bash function defined in ~/.bashrc.
 *
 * system() uses /bin/sh — non-interactive, never reads ~/.bashrc.
 * Sourcing ~/.bashrc manually via `bash -c 'source ...'` also fails
 * because most .bashrc files begin with a guard:
 *     [ -z "$PS1" ] && return
 * which exits immediately when the shell is non-interactive,
 * before any function definitions are reached.
 *
 * The fix: `bash -i` — interactive mode — which unconditionally
 * reads ~/.bashrc, making all defined functions available.
 * ────────────────────────────────────────────────────────────── */
static void bash_run(const char *cmd)
{
    /* Use double-quotes around cmd so task names with apostrophes
     * don't break the shell invocation.  The caller must have already
     * escaped any internal double-quotes if needed. */
    char full[1024];
    snprintf(full, sizeof(full), "bash -i -c '%s'", cmd);
    system(full);
}


static void fmt_hhmm(long secs, char *buf)
{
    if (secs < 0) secs = 0;
    long h = secs / 3600;
    long m = (secs % 3600) / 60;
    sprintf(buf, "%02ld:%02ld", h, m);
}

/* Centre a string horizontally inside width w, return left x */
static int centre_x(int w, int slen)
{
    int x = (w - slen) / 2;
    return (x < 0) ? 0 : x;
}

/* Draw a centred, bold title row */
static void draw_title(WINDOW *w, int y, const char *text)
{
    wattron(w, A_BOLD);
    mvwprintw(w, y, centre_x(SW, (int)strlen(text)), "%s", text);
    wattroff(w, A_BOLD);
}

/* ──────────────────────────────────────────────────────────────
 * Screen: Main Menu
 * Returns: 0=Work  1=Open GUI  2=Update Logger  3=Exit
 * ────────────────────────────────────────────────────────────── */
static int screen_main_menu(void)
{
    static const char *OPTS[] = {
        "1.  Work",
        "2.  Open GUI",
        "3.  Update Logger",
        "4.  Exit"
    };
    static const int N = 4;
    int sel = 0;

    WINDOW *w = newwin(SH, SW, 0, 0);
    keypad(w, TRUE);

    for (;;) {
        werase(w);
        wborder(w, ACS_VLINE, ACS_VLINE,
                   ACS_HLINE, ACS_HLINE,
                   ACS_ULCORNER, ACS_URCORNER,
                   ACS_LLCORNER, ACS_LRCORNER);

        draw_title(w, 2, "D A I L Y   L O G G E R");
        mvwhline(w, 3, 1, ACS_HLINE, SW - 2);

        int base_y = SH / 2 - N / 2;
        for (int i = 0; i < N; i++) {
            int y = base_y + i;
            int x = centre_x(SW, 22);
            if (i == sel) {
                wattron(w, A_REVERSE | A_BOLD);
                mvwprintw(w, y, x, "  %-18s  ", OPTS[i]);
                wattroff(w, A_REVERSE | A_BOLD);
            } else {
                mvwprintw(w, y, x, "  %-18s  ", OPTS[i]);
            }
        }

        mvwhline(w, SH - 3, 1, ACS_HLINE, SW - 2);
        mvwprintw(w, SH - 2, 2,
                  "Up/Down: Navigate    Enter: Select");

        wrefresh(w);

        int ch = wgetch(w);
        switch (ch) {
        case KEY_UP:    if (sel > 0)     sel--; break;
        case KEY_DOWN:  if (sel < N - 1) sel++; break;
        case '\n':
        case KEY_ENTER:
            delwin(w);
            return sel;
        case '1': delwin(w); return 0;
        case '2': delwin(w); return 1;
        case '3': delwin(w); return 2;
        case '4':
        case 'q':
        case 'Q':
            delwin(w); return 3;
        }
    }
}

/* ──────────────────────────────────────────────────────────────
 * Screen: Task Selection  (3-column table)
 * Returns: 1 = task selected (name in g_selected_task)
 *          0 = back / ESC
 * ────────────────────────────────────────────────────────────── */
static int screen_task_select(void)
{
    refresh_tasks();

    /* Column descriptors */
    const char  *HEADERS[3] = { "UNINITIATED",  "ONGOING",  "HALTED" };
    char       (*DATA[3])[TASK_LEN] = { g_uninitiated, g_active, g_halted };
    int          CNTS[3]  = { g_uninit_cnt, g_active_cnt, g_halted_cnt };
    /* Column x offsets and widths inside the box (inner width 58) */
    int          COL_X[3] = { 2, 22, 41 };
    int          COL_W[3] = { 18, 17, 16 };

    /* Total selectable entries */
    int total = CNTS[0] + CNTS[1] + CNTS[2];

    WINDOW *w = newwin(SH, SW, 0, 0);
    keypad(w, TRUE);

    /* sel is a flat index:
     *   [0 .. CNTS[0]-1]                         => col 0
     *   [CNTS[0] .. CNTS[0]+CNTS[1]-1]           => col 1
     *   [CNTS[0]+CNTS[1] .. total-1]             => col 2
     */
    int sel = 0;
    /* Make initial selection land on first non-empty column */
    if (total == 0) {
        werase(w);
        wborder(w, ACS_VLINE, ACS_VLINE,
                   ACS_HLINE, ACS_HLINE,
                   ACS_ULCORNER, ACS_URCORNER,
                   ACS_LLCORNER, ACS_LRCORNER);
        draw_title(w, SH / 2 - 1, "No tasks available.");
        mvwprintw(w, SH / 2 + 1,
                  centre_x(SW, 28),
                  "Press any key to return...");
        wrefresh(w);
        wgetch(w);
        delwin(w);
        return 0;
    }

    /* Helpers: map sel → (col, row_within_col) */
    #define SEL_COL(s)  ((s) < CNTS[0] ? 0 : (s) < CNTS[0]+CNTS[1] ? 1 : 2)
    #define COL_BASE(c) ((c)==0 ? 0 : (c)==1 ? CNTS[0] : CNTS[0]+CNTS[1])
    #define SEL_ROW(s)  ((s) - COL_BASE(SEL_COL(s)))

    int scroll[3] = {0, 0, 0};
    int visible   = SH - 8; /* rows available for task names */

    for (;;) {
        int cur_col = SEL_COL(sel);
        int cur_row = SEL_ROW(sel);

        /* Update scroll for current column */
        if (cur_row < scroll[cur_col])
            scroll[cur_col] = cur_row;
        if (cur_row >= scroll[cur_col] + visible)
            scroll[cur_col] = cur_row - visible + 1;

        werase(w);
        wborder(w, ACS_VLINE, ACS_VLINE,
                   ACS_HLINE, ACS_HLINE,
                   ACS_ULCORNER, ACS_URCORNER,
                   ACS_LLCORNER, ACS_LRCORNER);

        draw_title(w, 1, "SELECT A TASK");
        mvwhline(w, 2, 1, ACS_HLINE, SW - 2);

        /* Column headers */
        for (int c = 0; c < 3; c++) {
            wattron(w, A_UNDERLINE);
            mvwprintw(w, 3, COL_X[c], "%-*s", COL_W[c] - 1, HEADERS[c]);
            wattroff(w, A_UNDERLINE);
        }

        /* Column separators */
        for (int r = 3; r < SH - 3; r++) {
            mvwaddch(w, r, 20, ACS_VLINE);
            mvwaddch(w, r, 39, ACS_VLINE);
        }

        /* Task rows */
        int row_start = 4;
        for (int c = 0; c < 3; c++) {
            for (int r = 0; r < visible; r++) {
                int abs_r = r + scroll[c];
                if (abs_r >= CNTS[c]) break;
                int flat  = COL_BASE(c) + abs_r;
                int is_sel = (flat == sel);

                /* Truncate to column width */
                char trunc[TASK_LEN];
                snprintf(trunc, COL_W[c], "%s", DATA[c][abs_r]);

                if (is_sel) wattron(w, A_REVERSE | A_BOLD);
                mvwprintw(w, row_start + r, COL_X[c],
                          "%-*s", COL_W[c] - 1, trunc);
                if (is_sel) wattroff(w, A_REVERSE | A_BOLD);
            }
        }

        mvwhline(w, SH - 3, 1, ACS_HLINE, SW - 2);
        mvwprintw(w, SH - 2, 1,
                  "Arrows: Navigate   Enter: Select   ESC: Back");

        wrefresh(w);

        int ch = wgetch(w);

        switch (ch) {
        case KEY_UP:
            if (cur_row > 0) sel--;
            break;

        case KEY_DOWN:
            if (cur_row < CNTS[cur_col] - 1) sel++;
            break;

        case KEY_LEFT: {
            /* Move to closest non-empty column to the left */
            for (int c = cur_col - 1; c >= 0; c--) {
                if (CNTS[c] > 0) {
                    int new_row = cur_row < CNTS[c] ? cur_row : CNTS[c] - 1;
                    sel = COL_BASE(c) + new_row;
                    break;
                }
            }
            break;
        }

        case KEY_RIGHT: {
            for (int c = cur_col + 1; c < 3; c++) {
                if (CNTS[c] > 0) {
                    int new_row = cur_row < CNTS[c] ? cur_row : CNTS[c] - 1;
                    sel = COL_BASE(c) + new_row;
                    break;
                }
            }
            break;
        }

        case '\n':
        case KEY_ENTER: {
            int c = SEL_COL(sel);
            int r = SEL_ROW(sel);
            strncpy(g_selected_task, DATA[c][r], TASK_LEN - 1);
            g_selected_task[TASK_LEN - 1] = '\0';
            delwin(w);
            return 1;
        }

        case 27: /* ESC */
            delwin(w);
            return 0;
        }
    }

    #undef SEL_COL
    #undef COL_BASE
    #undef SEL_ROW
}

/* ──────────────────────────────────────────────────────────────
 * Screen: Timer
 * Returns elapsed seconds >= 0 when user presses [E]nd
 *         -1 if user ESC-cancels before recording anything
 * ────────────────────────────────────────────────────────────── */
static long screen_timer(void)
{
    long  accum   = 0;
    int   running = 0;
    time_t t_start = 0;

    WINDOW *w = newwin(SH, SW, 0, 0);
    keypad(w, TRUE);
    wtimeout(w, 500); /* non-blocking refresh every 500 ms */

    for (;;) {
        long elapsed = running
            ? accum + (long)(time(NULL) - t_start)
            : accum;

        char timebuf[16];
        fmt_hhmm(elapsed, timebuf);

        werase(w);
        wborder(w, ACS_VLINE, ACS_VLINE,
                   ACS_HLINE, ACS_HLINE,
                   ACS_ULCORNER, ACS_URCORNER,
                   ACS_LLCORNER, ACS_LRCORNER);

        /* Task name */
        char header[SW];
        snprintf(header, SW, "Task: %.44s", g_selected_task);
        draw_title(w, 1, header);
        mvwhline(w, 2, 1, ACS_HLINE, SW - 2);

        /* Big timer */
        int ty = SH / 2 - 1;
        wattron(w, A_BOLD);
        mvwprintw(w, ty, centre_x(SW, (int)strlen(timebuf)), "%s", timebuf);
        wattroff(w, A_BOLD);

        /* Status pill */
        const char *status_str = running ? "▶ RUNNING"
                               : (accum > 0 ? "⏸ PAUSED" : "■ STOPPED");
        mvwprintw(w, ty + 1, centre_x(SW, (int)strlen(status_str)),
                  "%s", status_str);

        mvwhline(w, ty + 2, 1, ACS_HLINE, SW - 2);

        /* Controls */
        int cy = ty + 3;
        mvwprintw(w, cy,
                  centre_x(SW, 38),
                  "[S] Start  [P] Pause  [E] End  [ESC] Back");

        wrefresh(w);

        int ch = wgetch(w);

        switch (ch) {
        case 's': case 'S':
            if (!running) {
                t_start = time(NULL);
                running = 1;
            }
            break;

        case 'p': case 'P':
            if (running) {
                accum  += (long)(time(NULL) - t_start);
                running = 0;
            }
            break;

        case 'e': case 'E': {
            if (running) {
                accum  += (long)(time(NULL) - t_start);
                running = 0;
            }
            long result = accum;
            delwin(w);
            return result;
        }

        case 27: /* ESC */
            if (running) {
                accum  += (long)(time(NULL) - t_start);
                running = 0;
            }
            delwin(w);
            return -1;
        }
    }
}

/* ──────────────────────────────────────────────────────────────
 * Screen: Session End
 * Returns 1 = submitted, 0 = cancelled
 * ────────────────────────────────────────────────────────────── */
static int screen_session_end(long elapsed_secs)
{
    char prog_buf[8] = "";
    int  prog_cursor = 0;
    int  finished    = 0;
    int  active_fld  = 0; /* 0=progress, 1=checkbox, 2=submit */

    /* Date string */
    time_t now     = time(NULL);
    struct tm *tmi = localtime(&now);
    char date_str[32];
    strftime(date_str, sizeof(date_str), "%Y-%m-%d", tmi);

    char timebuf[16];
    fmt_hhmm(elapsed_secs, timebuf);

    WINDOW *w = newwin(SH, SW, 0, 0);
    keypad(w, TRUE);
    curs_set(1); /* show cursor for text input */

    for (;;) {
        werase(w);
        wborder(w, ACS_VLINE, ACS_VLINE,
                   ACS_HLINE, ACS_HLINE,
                   ACS_ULCORNER, ACS_URCORNER,
                   ACS_LLCORNER, ACS_LRCORNER);

        draw_title(w, 1, "SESSION SUMMARY");
        mvwhline(w, 2, 1, ACS_HLINE, SW - 2);

        /* Info block */
        mvwprintw(w, 4, 3, "Task : %.46s", g_selected_task);
        mvwprintw(w, 5, 3, "Date : %s",    date_str);
        mvwprintw(w, 6, 3, "Time : %s  (HH:MM)", timebuf);

        mvwhline(w, 7, 1, ACS_HLINE, SW - 2);

        /* ── Field 0: Estimated Progress ── */
        if (active_fld == 0) wattron(w, A_BOLD);
        mvwprintw(w, 9, 3,
                  "Estimated Progress (%%) : [%-5s]", prog_buf);
        if (active_fld == 0) wattroff(w, A_BOLD);

        /* ── Field 1: Checkbox ── */
        if (active_fld == 1) wattron(w, A_BOLD);
        mvwprintw(w, 11, 3,
                  "Has the Task finished? :  [%s]",
                  finished ? "X" : " ");
        if (active_fld == 1) wattroff(w, A_BOLD);

        mvwhline(w, SH - 5, 1, ACS_HLINE, SW - 2);

        /* ── Field 2: Submit ── */
        if (active_fld == 2) wattron(w, A_REVERSE | A_BOLD);
        mvwprintw(w, SH - 4, centre_x(SW, 12), "[ SUBMIT ]");
        if (active_fld == 2) wattroff(w, A_REVERSE | A_BOLD);

        mvwprintw(w, SH - 2, 1,
                  "Tab/Down: Next   Space: Toggle   Enter: Confirm");

        /* Position cursor in progress input field */
        if (active_fld == 0) {
            wmove(w, 9, 30 + prog_cursor);
        }

        wrefresh(w);

        int ch = wgetch(w);

        /* Universal navigation */
        if (ch == '\t' || ch == KEY_DOWN) {
            active_fld = (active_fld + 1) % 3;
            continue;
        }
        if (ch == KEY_UP) {
            active_fld = (active_fld + 2) % 3;
            continue;
        }
        if (ch == 27) { /* ESC */
            curs_set(0);
            delwin(w);
            return 0;
        }

        /* Field-specific input */
        switch (active_fld) {
        case 0: /* Progress % numeric input (max 3 digits, 0–100) */
            if (ch >= '0' && ch <= '9' && prog_cursor < 3) {
                prog_buf[prog_cursor++] = (char)ch;
                prog_buf[prog_cursor]   = '\0';
            } else if ((ch == KEY_BACKSPACE || ch == 127 || ch == '\b')
                       && prog_cursor > 0) {
                prog_buf[--prog_cursor] = '\0';
            }
            break;

        case 1: /* Checkbox toggle */
            if (ch == ' ' || ch == '\n' || ch == KEY_ENTER) {
                finished = !finished;
            }
            break;

        case 2: /* Submit */
            if (ch == '\n' || ch == KEY_ENTER) {
                int prog_val = atoi(prog_buf);
                if (prog_val < 0)   prog_val = 0;
                if (prog_val > 100) prog_val = 100;

                char cmd[700];
                if (!finished) {
                    snprintf(cmd, sizeof(cmd),
                             "add_session \"%s\" %d \"%s\"",
                             timebuf, prog_val, g_selected_task);
                } else {
                    snprintf(cmd, sizeof(cmd),
                             "complete_task \"%s\" %d \"%s\"",
                             timebuf, prog_val, g_selected_task);
                }

                curs_set(0);
                endwin();
                bash_run(cmd);
                /* Pause briefly so the user can read any shell output */
                printf("\n[Press Enter to return to Daily Logger...]\n");
                fflush(stdout);
                (void)getchar();
                /* Reinitialise ncurses */
                initscr();
                cbreak();
                noecho();
                keypad(stdscr, TRUE);
                curs_set(0);

                delwin(w);
                return 1;
            }
            break;
        }
    }
}

/* ──────────────────────────────────────────────────────────────
 * Helper: run external command with ncurses teardown / reinit
 * ────────────────────────────────────────────────────────────── */
static void run_external(const char *cmd)
{
    endwin();
    bash_run(cmd);
    printf("\n[Press Enter to return to Daily Logger...]\n");
    fflush(stdout);
    (void)getchar();
    initscr();
    cbreak();
    noecho();
    keypad(stdscr, TRUE);
    curs_set(0);
}

/* ──────────────────────────────────────────────────────────────
 * Entry point
 * ────────────────────────────────────────────────────────────── */
int main(int argc, char **argv)
{
    (void)argc; (void)argv;

    initscr();
    cbreak();
    noecho();
    keypad(stdscr, TRUE);
    curs_set(0);

    /* Optional: restrict to 60x28 if the terminal is large enough */
    if (LINES < SH || COLS < SW) {
        endwin();
        fprintf(stderr,
                "daily_logger requires a terminal of at least %dx%d.\n"
                "Current size: %dx%d\n", SW, SH, COLS, LINES);
        return 1;
    }

    int running = 1;
    while (running) {
        int choice = screen_main_menu();

        switch (choice) {

        case 0: { /* Work */
            int chosen = screen_task_select();
            if (chosen) {
                long elapsed = screen_timer();
                if (elapsed >= 0) {
                    screen_session_end(elapsed);
                }
            }
            break;
        }

        case 1: /* Open GUI */
            run_external("logger_gui");
            break;

        case 2: /* Update Logger */
            run_external("update_logger");
            break;

        case 3: /* Exit */
        default:
            running = 0;
            break;
        }
    }

    endwin();
    return 0;
}
