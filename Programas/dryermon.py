# dryermon.py

import time
import threading
from datetime import datetime
from config import Config
from database import Database
from buffer import ReadingBuffer
from serialio import SerialBus
from slave import Slave
import ui

cfg = Config()

db = Database(cfg)
buffer = ReadingBuffer(db)

slaves = {row["esclavo"]: Slave(row) for row in db.load_slaves()}

buses = [
    SerialBus(p,
              cfg.geti('serial', 'baudrate', 9600),
              cfg.geti('serial', 'timeout', 0))
    for p in cfg.get_ports()
]

FRAME_LEN = 96

def rx_thread(buses, slaves, cfg, buffer, running):
    rx_bufs = {bus: bytearray() for bus in buses}
    while running.is_set():
        for bus in buses:
            try:
                data = bus.read()
                if data:
                    bus.feed(data)
                frames = bus.get_frames()
                for frame in frames :
                    slave_id = frame[1]
                    slave = slaves.get(slave_id)
                    if not slave:
                        continue
                    bus.send_ack(slave_id)
                    slave.update_from_frame(frame)
                    slave.ult_respuesta = time.time()
                    reading = {
                                        'fecha': datetime.now(),
                                        'esclavo': slave.id,
                                        'temp1': slave.temp1,
                                        'temp2': slave.temp2,
                                        'formula': slave.formula,
                                        'display': slave.display,
                                        'entrada1': slave.entrada1,
                                        'entrada2': slave.entrada2,
                                        'version': slave.version,
                                        'idcarga': slave.idcarga
                                    }
                    t1 = f"{slave.temp1:5.0f}" if slave.temp1 is not None else " ----"
                    t2 = f"{slave.temp2:5.0f}" if slave.temp2 is not None else " ----"
                    line = (
                        f"{slave.nombre:5} "
                        f"{t1}  {t2}  "
                        f"{str(slave.formula):>3}  "
                        f"{slave.display} "
                    )
                    ui.log(line)
                    buffer.add(reading)
            except Exception as e:
                ui.log(f"[RX] {bus.port} error: {e}")

def ui_thread(slaves, db, buffer, stop_event):
    import time
    import ui

    FPS = 10
    PERIOD = 1 / FPS

    while not stop_event.is_set():
        t0 = time.time()
        try:
            ui.redraw(
                slaves,
                db_state=db.state,
                buffer_pct=buffer.used_pct()
            )
        except Exception as e:
            ui.log(f"[UI] error: {e}")
        dt = time.time() - t0
        if dt < PERIOD:
            time.sleep(PERIOD - dt)

def tx_thread(buses, slaves, cfg, stop_evt):
    while not stop_evt.is_set():
        for s in slaves.values():
            if s.ready_to_call():
                for bus in buses:
                    bus.send_call(s.id)
                s.ult_llamada = time.time()
                time.sleep(cfg.getf("time", "call_pause", 0.3))
            s.update_state(cfg)
        time.sleep(0.1)

running = threading.Event()
running.set()

rx = threading.Thread(
    target=rx_thread,
    args=(buses, slaves, cfg, buffer, running),
    daemon=True
)
rx.start()

stop_event = threading.Event()

t_ui = threading.Thread(
    target=ui_thread,
    args=(slaves, db, buffer, stop_event),
    daemon=True
)
t_ui.start()

t_tx = threading.Thread(
    target=tx_thread,
    args=(buses, slaves, cfg, stop_event),
    daemon=True
)
t_tx.start()

while True:
    db.ensure_alive()
    for s in slaves.values():
        s.update_state(cfg)
    buffer.flush()
    time.sleep(1)