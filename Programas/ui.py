# ui.py
import sys
import time
import shutil

# ───────────────────────────
# ANSI
# ───────────────────────────
RESET   = "\033[0m"
BOLD    = "\033[1m"

RED     = "\033[31m"
GREEN   = "\033[32m"
YELLOW  = "\033[33m"
BLUE    = "\033[34m"
WHITE   = "\033[37m"
GRAY    = "\033[90m"

CLEAR   = "\033[2J"
HOME    = "\033[H"

# ───────────────────────────
# Configuración UI
# ───────────────────────────
MAX_LOG_LINES = 1000
MIN_WIDTH = 60
MIN_HEIGHT = 30

_log_buffer = []

# ───────────────────────────
# Helpers
# ───────────────────────────
def _color_for_state(state):
    if state == "green":
        return GREEN
    if state == "yellow":
        return YELLOW
    if state == "red":
        return RED
    return WHITE

def log(msg):
    ts = f"{time.strftime('%Y-%m-%d %H:%M:%S')}"
    line = f"{BLUE}{ts}{RESET} {msg}"
    _log_buffer.append(line)
    if len(_log_buffer) > MAX_LOG_LINES:
        _log_buffer.pop(0)

# ───────────────────────────
# Renderizado
# ───────────────────────────
def _render_slaves(slaves, width):
    lines = []
    w = width - 45
    header = "ID".center(5) + " " + "ST".center(3) + " " + "T1".center(5) + " " +"T2".center(5)+ " " +"F".center(3)+ " " + "DISPLAY".center(w) + " " + "TX".center(5) + " " + "RX".center(5)
    
    lines.append(BOLD + header.ljust(width)[:width] + RESET)
    for s in slaves.values():
        color = _color_for_state(s.state)
        t1 = f"{s.temp1:5.0f}" if s.temp1 is not None else " ----"
        t2 = f"{s.temp2:5.0f}" if s.temp2 is not None else " ----"
        if s.state == "red":
            line = f"{s.nombre:5} {s.state_char} "
            line = line.ljust(width)
        else:
            
            line = (
                f"{s.nombre:5} {s.state_char} "
                f"{t1}  {t2} "
                f"{str(s.formula):>3} "
                f"{s.display.ljust(w, "#")} "
                f"{time.time() - s.ult_llamada:>5.1f} "
                f"{time.time() - s.ult_respuesta:>5.1f} "
            )
        lines.append(color + line.ljust(width)[:width] + RESET)
    lines.append("-" * width)
    return lines

def _render_logs(height, width):
    visible = _log_buffer[-height:]
    out = []
    for l in visible:
        out.append(l.ljust(width)[:width])
    while len(out) < height:
        out.append(" " * width)
    return out

def _render_status(width, db_state, slaves, buffer_pct):
    green = sum(s.state == "green" for s in slaves.values())
    yellow = sum(s.state == "yellow" for s in slaves.values())
    red = sum(s.state == "red" for s in slaves.values())
    txt = (
        f"DB: {db_state}  "
        f"Slaves:{len(slaves):>3} "
        f"G:{green:>3} Y:{yellow:>3} R:{red:>3}  "
        f"Buf:{buffer_pct:3.0f}%  "
        f"{time.strftime('%Y-%m-%d %H:%M:%S'):>{width - 50}}"
    )
    return RESET + "-" * width + "\n" + BOLD + txt.ljust(width)[:width] + RESET

def _render_minimal(width, height, slaves, db_state, buffer_pct):
    sys.stdout.write(HOME)
    green = sum(s.state == "green" for s in slaves.values())
    yellow = sum(s.state == "yellow" for s in slaves.values())
    red = sum(s.state == "red" for s in slaves.values())
    free = height - 1
    line2 = (
        f"DB: {db_state} "
        f"S:{len(slaves):>3} "
        f"G:{green:>3} Y:{yellow:>3} R:{red:>3} "
        f"B:{buffer_pct:>3.0f}% "
        f"{time.strftime('%H:%M:%S')}"
    )
    visible = _log_buffer[-free:]
    out = []
    for l in visible:
        out.append(l.ljust(width)[:width])
    while len(out) < free:
        out.append(" " * width)
    sys.stdout.write("\n".join(out))
    sys.stdout.write("\n")
    sys.stdout.write(line2.ljust(width)[:width])
    sys.stdout.flush()

# ───────────────────────────
# API pública
# ───────────────────────────
def redraw(slaves, db_state="??", buffer_pct=0):
    size = shutil.get_terminal_size((80, 24))
    width, height = size.columns, size.lines
    if width < MIN_WIDTH or height < MIN_HEIGHT:
        _render_minimal(width, height, slaves, db_state, buffer_pct)
        return
    header_lines = _render_slaves(slaves, width)
    status_line = _render_status(width, db_state, slaves, buffer_pct)
    used = len(header_lines) + 2
    free = height - used
    logs = _render_logs(free, width)
    screen = []
    screen.extend(header_lines)
    screen.extend(logs)
    screen.append(status_line)
    sys.stdout.write(HOME)
    sys.stdout.write("\n".join(screen))
    sys.stdout.flush()
