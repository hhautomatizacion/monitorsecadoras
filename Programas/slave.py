import random
import time
from utils import interpolar, obtenerformula

class Slave:
    def __init__(self, row):
        self.id = row['esclavo']
        self.nombre = row['nombre']
        self.descripcion = row['descripcion']
        self.version = row['version']
        self.x1 = row['x1']
        self.x2 = row['x2']
        self.y1 = row['y1']
        self.y2 = row['y2']
        self.tiene_temp1 = bool(row['temp1'])
        self.tiene_temp2 = bool(row['temp2'])
        self.temp1 = None
        self.temp2 = None
        self.entrada1 = 0
        self.entrada2 = 0
        self.display = ''
        self.formula = '0'
        now = time.time()
        self.ult_llamada = now - random.randint(60, 3600)
        self.ult_respuesta = now - random.randint(60, 3600)
        self.state = 'red'
        self.call_interval = 1

    def interpola(self):
        return any([self.x1, self.x2, self.y1, self.y2])

    def calc_temp(self, raw):
        if self.interpola():
            return interpolar(raw, self.x1, self.x2, self.y1, self.y2)
        return raw

    def update_from_frame(self, frame):
        self.ult_respuesta = time.time()
        if self.tiene_temp1:
            raw = (frame[2] << 8) | frame[3]
            self.temp1 = self.calc_temp(raw)
        if self.tiene_temp2:
            raw = (frame[4] << 8) | frame[5]
            self.temp2 = self.calc_temp(raw)
        self.entrada1 = frame[6]
        self.entrada2 = frame[7]
        disp = frame[8:92].decode('ascii', errors='ignore')
        disp = disp.replace('\x00', ' ').replace('"', ' ').replace("'", ' ')
        self.display = disp.strip()
        self.idcarga = 0
        self.formula = obtenerformula(self.display) if self.entrada1 else '0'

    def update_state(self, cfg):
        age = time.time() - self.ult_respuesta
        if age < cfg.geti('time', 'alert_yellow', 10):
            self.state = 'green'
            self.call_interval = cfg.getf('time', 'call_green', 2.0)
        elif age < cfg.geti('time', 'alert_red', 30):
            self.state = 'yellow'
            self.call_interval = cfg.getf('time', 'call_yellow', 0.5)
        else:
            self.state = 'red'
            self.call_interval = cfg.getf('time', 'call_red', 5.0)

    def ready_to_call(self):
        return time.time() - self.ult_llamada >= self.call_interval

    @property
    def state_char(self):
        if self.state == 'green':
            return 'OK'
        elif self.state == 'yellow':
            return '!!'
        elif self.state == 'red':
            return 'XX'
        else:
            return '--'