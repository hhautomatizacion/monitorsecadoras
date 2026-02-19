import pymysql
import time
import json
import datetime
from pathlib import Path
from slave import Slave
import ui

SLAVES_CACHE_FILE = Path("dryermon.json")

class Database:
    def __init__(self, cfg):
        self.cfg = cfg
        self.conn = None
        self._state = "--"
        self.last_ping = 0

    def connect(self):
        self.conn = pymysql.connect(
            host=self.cfg.get('database', 'server'),
            user=self.cfg.get('database', 'user'),
            password=self.cfg.get('database', 'password'),
            database=self.cfg.get('database', 'name'),
            autocommit=True,
            cursorclass=pymysql.cursors.DictCursor
        )
        self.last_ping = time.time()

    def ensure_alive(self):
        try:
            if not self.conn:
                self.connect()
                self._state="OK"
                return True
            if time.time() - self.last_ping > 60:
                self.conn.ping(reconnect=True)
                self.last_ping = time.time()
            return True
        except Exception as e:
            self._state="XX"
            self.conn = None
            return False

    def _load_slaves_from_db(self):
        self.ensure_alive()
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT esclavo, nombre, descripcion, version,
                       x1, x2, y1, y2, temp1, temp2
                FROM esclavos
                WHERE habilitado=1
                ORDER BY esclavo
            """)
            return cur.fetchall()

    def insert_reading(self, data):
        self.ensure_alive()
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO lecturas
                (fecha, secadora, temp1, temp2, formula, display,
                 entrada1, entrada2, version, idcarga)
                VALUES (%(fecha)s, %(esclavo)s, %(temp1)s, %(temp2)s,
                        %(formula)s, %(display)s,
                        %(entrada1)s, %(entrada2)s,
                        %(version)s, %(idcarga)s)
            """, data)

    def _save_slaves_cache(self, rows):
        data = {
            "version": 1,
            "generated_at": datetime.datetime.now().isoformat(),
            "slaves": rows
        }
        SLAVES_CACHE_FILE.write_text(json.dumps(data, indent=2))

    def _load_slaves_cache(self):
        if not SLAVES_CACHE_FILE.exists():
            return []
        try:
            data = json.loads(SLAVES_CACHE_FILE.read_text())
            return data.get("slaves", [])
        except Exception:
            return []

    def load_slaves(self):
        try:
            ui.log(f"[DB] Servidor {self.cfg.get('database', 'server')}")
            rows = self._load_slaves_from_db()
            self._state = "OK"
            self._save_slaves_cache(rows)
            return rows
        except Exception:
            self._state = "XX"
            ui.log("[DB] usando cache de esclavos")
            return self._load_slaves_cache()

    @property
    def state(self):
        return  self._state
