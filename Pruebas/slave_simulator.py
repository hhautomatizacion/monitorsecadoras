#!/usr/bin/env python3
import serial
import time
import random
import struct
import binascii

# ===============================
# CONFIGURACIÓN DEL SIMULADOR
# ===============================

#PORT = "/dev/ttyUSB0"
#PORT = "/dev/ttyUSB1"
PORT = "/tmp/ttyV0"
BAUDRATE = 9600
TIMEOUT = 0.1
RESPONSE_DELAY = (0.05, 0.5)   
DROP_PROB = 0.2                
CRC_ERROR_PROB = 0.2           
TRUNCATE_PROB = 0.2            
FRAME_LEN = 96
DISPLAY_LEN = 40
SLAVES = [5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]

FORMULAS = {
    1: [
        ("PREHEAT",   30, True,  True),
        ("SECADO",    60, True,  True),
        ("SUAVE",     45, True,  False),
        ("ENFRIADO",  30, True,  False),
    ],
    2: [
        ("SECADO",    90, True,  True),
        ("SUAVE",     60, True,  False),
        ("ENFRIADO",  40, True,  False),
    ],
}

class VirtualSlave:
    def __init__(self, slave_id):
        self.id = slave_id
        self.formula = random.randint(1, 5)
        self.step = 0
        self.step_time = 0
        self.temp1 = random.randint(80, 100)
        self.temp2 = self.temp1 - random.randint(3, 8)
        self.entrada1 = False
        self.entrada2 = False
        self.display = "IDLE"
        self.t_total = 0
        self.t_step = 0
        self.last_update = time.time()

    @property
    def formula_name(self):
        return f"Formula {self.formula}"

    def current_display_text(self) -> str:
        return (
            f"{self.formula}:{self.formula_name} "
            f"Paso #:{self.step} "
            f"T={self.t_total} "
            f"Paso={self.t_step}"
        )

    def current_display_bytes(self) -> bytes:
        text = self.current_display_text()
        b = text.encode("ascii", errors="replace")
        if len(b) > DISPLAY_LEN:
            b = b[:DISPLAY_LEN]
        return b.ljust(DISPLAY_LEN, b" ")

    def update(self):
        now = time.time()
        dt = int(now - self.last_update)
        if dt <= 0:
            return
        self.last_update = now
        self.t_total += dt
        self.t_step += dt
        if self.step == 0: 
            self.entrada1 = False
            self.entrada2 = False
            self.display = "IDLE"
            if self.step_time > random.randint(5, 10):
                self.step = 1
                self.step_time = 0
                self.formula_id = random.randint(1, 5)
        elif self.step == 1:  
            self.entrada1 = True
            self.entrada2 = True
            self.display = f"F{self.formula}"
            if self.step_time > 10:
                self.step = 2
                self.step_time = 0
        elif self.step == 2:  
            self.entrada1 = True
            self.entrada2 = self.step_time % 3 != 0
            self.display = f"F{self.formula}"

            if self.step_time > 15:
                self.step = 0
                self.step_time = 0

    def update_temperature(self):
        if self.entrada2:
            self.temp1 += random.randint(1, 3)
        else:
            self.temp1 -= random.randint(0, 2)
        self.temp1 = max(30, min(self.temp1, 250))
        self.temp2 = self.temp1 - random.randint(3, 8)

    def current_outputs(self):
        return int(self.entrada1), int(self.entrada2)

    def current_display(self):
        return self.display

# ===============================
# UTILIDADES
# ===============================

def crc16(data: bytes, crc=0xFFFF) -> int:
    for b in data:
        crc ^= b
        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc & 0xFFFF

def hex_dump(b):
    return " ".join(f"{x:02X}" for x in b)

# ===============================
# GENERAR RESPUESTA DE ESCLAVO
# ===============================

def build_frame(slave: VirtualSlave) -> bytes:
    frame = bytearray(FRAME_LEN)
    frame[0] = 0x10
    frame[1] = slave.id
    struct.pack_into(
        ">HHB",
        frame,
        2,
        int(slave.temp1),
        int(slave.temp2),
        int(slave.formula)
    )
    entradas = 0
    if slave.entrada1:
        entradas |= 0x01
    if slave.entrada2:
        entradas |= 0x02
    frame[7] = entradas
    disp = slave.current_display_bytes()
    frame[8:8 + DISPLAY_LEN] = disp
    crc = crc16(frame[:-2])
    frame[-2:] = struct.pack("<H", crc)  
    return bytes(frame)

def get_slave(slave_id: int) -> VirtualSlave:
    if slave_id not in virtual_slaves:
        virtual_slaves[slave_id] = VirtualSlave(slave_id)
    return virtual_slaves[slave_id]

# ===============================
# MAIN
# ===============================

virtual_slaves = {}

def main():
    ser = serial.Serial(PORT, BAUDRATE, timeout=TIMEOUT)
    print(f"[SIM] Escuchando en {PORT} @ {BAUDRATE}")
    print(f"[SIM] Esclavos simulados: {SLAVES}")
    print("-" * 60)
    buffer = bytearray()
    while True:
        data = ser.read(64)
        if not data:
            continue
        buffer.extend(data)
        while len(buffer) >= 4:
            call = buffer[:4]
            buffer = buffer[4:]
            print(f"[RX] {hex_dump(call)}")
            slave_id = call[1]
            if not slave_id in SLAVES:
                print(f"[SIM] ID inválido {slave_id}, ignorado")
                continue
            if call[0] == 5:
                print(f"[CALL] esclavo={slave_id}")
                if random.random() < DROP_PROB:
                    print(f"[SIM] esclavo={slave_id} NO RESPONDE")
                    continue
                delay = random.uniform(*RESPONSE_DELAY)
                time.sleep(delay)
                frame = build_frame(get_slave(slave_id))
                if random.random() < CRC_ERROR_PROB:
                    frame = frame[:-2] + b"\x00\x00"
                    print(f"[SIM] esclavo={slave_id} CRC MALO")
                if random.random() < TRUNCATE_PROB:
                    cut = random.randint(10, FRAME_LEN - 10)
                    frame = frame[:cut]
                    print(f"[SIM] esclavo={slave_id} TRAMA TRUNCADA ({cut} bytes)")
                else:
                    print(f"[SIM] esclavo={slave_id} RESPUESTA OK ({len(frame)} bytes)")
                print(f"[TX] {hex_dump(frame)}")
                ser.write(frame)
                ser.flush()
            if call[0] == 6:
                print(f"[ACK] esclavo={slave_id}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[SIM] detenido por usuario")
