# serialio.py
import serial
import threading
import time
import ui

class SerialBus:
    def __init__(self, port, baudrate=9600, timeout=0):
        self.port = port
        self.ser = serial.Serial(
            port=port,
            baudrate=baudrate,
            timeout=timeout
        )
        self.buffer = bytearray()
        self.lock = threading.Lock()
        ui.log(f'[SERIAL] Puerto {port} @ {baudrate}')

    def write(self, data: bytes):
        self.ser.write(data)
        self.ser.flush()

    def read(self):
        try:
            data = self.ser.read(256)
            return data
        except Exception:
            return b""
    
    def send_call(self, slave_id: int):
        frame = bytes([5, slave_id])
        crc = self._crc16(frame)
        packet = frame + bytes([crc & 0xFF, (crc >> 8) & 0xFF])
        self.write(packet)

    def send_ack(self, slave_id: int):
        frame = bytes([6, slave_id])
        crc = self._crc16(frame)
        packet = frame + bytes([crc & 0xFF, (crc >> 8) & 0xFF])
        self.write(packet)
    
    def feed(self, data: bytes):
        if not data:
            return
        with self.lock:
            self.buffer.extend(data)

    def get_frames(self):
        frames = []
        with self.lock:
            i = 0
            while i <= len(self.buffer) - 96:
                candidate = self.buffer[i:i+96]
                if self._valid_crc(candidate):
                    frames.append(candidate)
                    del self.buffer[:i+96]
                    i = 0
                else:
                    i += 1
            if len(self.buffer) > 512:
                del self.buffer[:-96]
        return frames

    # ================= UTIL =================

    def _crc16(self, data, crc=0xFFFF):
        for b in data:
            crc ^= b
            for _ in range(8):
                if crc & 1:
                    crc = (crc >> 1) ^ 0xA001
                else:
                    crc >>= 1
        return crc & 0xFFFF

    def _crc_bytes(self, data):
        crc = self._crc16(data)
        return f'{crc & 0xFF:02X} {(crc >> 8) & 0xFF:02X}'

    def _valid_crc(self, frame):
        recv = frame[94] | (frame[95] << 8)
        calc = self._crc16(frame[:94])
        return recv == calc
    
    def crc_ok(self, frame):
        return self._valid_crc(frame)

    def _hex(self, data):
        return ' '.join(f'{b:02X}' for b in data)
