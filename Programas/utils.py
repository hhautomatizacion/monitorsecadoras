def crc16(data, crc=0xFFFF):
    for b in data:
        crc ^= b
        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc & 0xFFFF


def interpolar(x, x1, x2, y1, y2):
    if x2 == x1:
        return 0
    return int((x - x1) * (y2 - y1) / (x2 - x1) + y1)


def obtenerformula(display):
    display = display.strip()
    for i, ch in enumerate(display):
        if ch == ':':
            try:
                return display[:i].strip()
            except:
                return '0'
        if not ch.isdigit():
            break
    return '0'
