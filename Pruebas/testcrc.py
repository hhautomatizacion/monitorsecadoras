def crc16(buff, crc = 0xffff, poly = 0xa001):
	l = len(buff)
	i = 0
	while i < l:
		ch = ord(buff[i])
		uc = 0
		while uc < 8:
			if (crc & 1) ^ (ch & 1):
				crc = (crc >> 1) ^ poly
			else:
				crc >>= 1
			ch >>= 1
			uc += 1
		i += 1
	return crc

def lo(st):
	return st & 0xff

def hi(st):
	return (st & 0xff00) >> 8

def hexa(x):
	r = hex(x).split('x')[-1]
	if len(r) < 2:
		r = '0'+ r
	return r

def deci(x):
	r = int(x,16)
	return r

datos=''

s = '00 0f 00 bc 00 93 01 00 30 30 30 32 3a 20 50 61 73 6f 20 23 30 33 20 4c 69 6e 65 61 20 23 30 37 20 20 54 3d 20 31 39 3a 30 34 20 50 61 73 6f 3d 20 34 30 3a 35 36 20 20 41 63 74 3d 30 37 39 35 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 01 04 b1 a5'
#  - b1 a5

entrada = s.split(' ')

for i in range(0,len(entrada)):
	#print entrada[i]
	#print i
	print deci(entrada[i])
	datos=datos+ chr(deci(entrada[i]))
print '-----------------'
print lo(crc16(datos[:94]))
print hi(crc16(datos[:94]))

