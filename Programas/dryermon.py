import threading
import serial
import time
import datetime
import sys
import MySQLdb
import ConfigParser

class slave:
	def __init__(self,numero,nombre,temp1,temp2,entrada1,entrada2,formula,display,version,habilitado,x1,y1,x2,y2,t1,t2,ultimallamada,ultimarespuesta,tiemporespuesta,tiemporespuestas):
		self.numero=numero
		self.nombre=nombre
		self.temp1=temp1
		self.temp2=temp2
		self.entrada1=entrada1
		self.entrada2=entrada2
		self.formula=formula
		self.display=display
		self.version=version
		self.habilitado=habilitado
		self.x1=x1
		self.y1=y1
		self.x2=x2
		self.y2=y2
		self.t1=t1
		self.t2=t2
		self.ultimallamada=ultimallamada
		self.ultimarespuesta=ultimarespuesta
		self.tiemporespuesta=tiemporespuesta
		self.tiemporespuestas=tiemporespuestas

def conectar():
	global cursor
	global db
	global esclavo
	global alivedb
	global sServidor
	db = MySQLdb.connect(sServidor,'root','manttocl','dryermon')
	cursor = db.cursor()
	cursor.execute('select * from esclavos where habilitado=1 order by nombre')
	rows=cursor.fetchall()
	esclavo={}
	ahora=datetime.datetime.now()
	alivedb=datetime.datetime.now()
	iter=0
	for row in rows:
		iter=iter-0.1
		ahora=ahora + datetime.timedelta(seconds=iter)
		esclavo[row[1]]=slave(int(row[1]),row[2],'0','0','0','0','0','',int(row[4]),int(row[5]),int(row[6]),int(row[8]),int(row[7]),int(row[9]),int(row[10]),int(row[11]),ahora,ahora,ahora,ahora)
def dbping():
	global db
	global alivedb
	sys.stdout.write('\0\033[1;32m')
	sys.stdout.write('\0\033[7;1H')
	printw(str(datetime.datetime.now()),19)
	printw("Pinging")	
	try:	
		db.ping()
		alivedb=datetime.datetime.now()
	except MySQLdb.Error:
		sys.stdout.write("mysqlerror")


def almacenar(secadora,temp1,temp2,formula,display,entrada1,entrada2,version):
	global cursor
	global db
	global alivedb
	try:
		cursor.execute('insert into lecturas values (0,now(),' + secadora + ',' + temp1 + ',' + temp2 + ',' + formula + ',"' + display + '",' + entrada1 + ',' + entrada2 + ',' + version + ',0)')
	except MySQLdb.Error:
		sys.stdout.write("mysql error")
	finally:
		db.commit()
		alivedb=datetime.datetime.now()

def interpolar(x,x1=268,x2=293,y1=88,y2=110):
	return float(float(float(x)-float(x1))*float((float(y2)-float(y1))/(float(x2)-float(x1))))+float(y1)

def borrar(secadora):
	global esclavo
	sys.stdout.write('\0\033[' + str(secadora + 5) + ';1H')
	sys.stdout.write('\0\033[1;31m')
	printw(esclavo[secadora].nombre)
	printw('-',120)


def imprimir(secadora,color='blanco'):
	global esclavo
	sys.stdout.write('\0\033[' + str(secadora + 5) + ';1H')
	if color=='blanco':
		sys.stdout.write('\0\033[1;37m')
	if color=='verde':
		sys.stdout.write('\0\033[1;32m')
	if color=='amarillo':
		sys.stdout.write('\0\033[1;33m')

	printw(esclavo[secadora].nombre)
	printw(esclavo[secadora].temp1,10)
	printw(esclavo[secadora].temp2,10)
	printw(esclavo[secadora].entrada1)
	printw(esclavo[secadora].entrada2)
	printw(esclavo[secadora].formula)
	printw(esclavo[secadora].display,20)
	printw(str(esclavo[secadora].version))
	printw(str(esclavo[secadora].tiemporespuesta),17)
	printw(str(esclavo[secadora].tiemporespuestas),17)

def printw(str, width=7):
    sys.stdout.write('|' + str[:width].center(width))
    sys.stdout.flush()

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

def obtenerformula(display):
	f='0'
	try:
		if len(display):
			if display.find(':'):
				f=str(int(display[0:display.find(':')]))
			else:
				f='0'
		else:
			f='0'
	except e:
		f='0'
		#nada
	finally:
		# nada
		return f

def handle_data(data):
	global datos
	global esclavo
	secadora=''
	temp1=''
	temp2=''
	entrada1=''
	entrada2=''
	formula=''
	display=''
	version=''	

	if len(data)>0:
		datos=datos+data
		if len(datos)>1:
			sys.stdout.write('\0\033[1;33m')
			sys.stdout.write('\0\033[3;1H')
			printw(str(datetime.datetime.now()),19)
			printw(str(ord(datos[1])))
			printw(str(len(datos)))
		if len(datos)>9:
			sys.stdout.write('\0\033[1;36m')
			sys.stdout.write('\0\033[5;1H')
			printw(str(datetime.datetime.now()),19)
			printw(str(ord(datos[0])))
			printw(str(ord(datos[1])))
			printw(str(ord(datos[2])))
			printw(str(ord(datos[3])))
			printw(str(ord(datos[4])))
			printw(str(ord(datos[5])))
			printw(str(ord(datos[6])))
			printw(str(ord(datos[7])))
			printw(str(ord(datos[8])))
			printw(str(ord(datos[9])))

		if len(datos)>96:
			#sys.stdout.write('\0\033[25d')
			#sys.stdout.write(datos)
			datos=''
		if len(datos)==96:
			if ord(datos[94]) == lo(crc16(datos[:94])) and ord(datos[95]) == hi(crc16(datos[:94])) :			
				
				secadora=ord(datos[1])

				if secadora in esclavo:
					esclavo[secadora].tiemporespuestas=datetime.datetime.now()-esclavo[secadora].ultimarespuesta
					esclavo[secadora].ultimarespuesta=datetime.datetime.now()				
					if esclavo[secadora].x1 <> 0 or esclavo[secadora].y1 <> 0 or esclavo[secadora].x2 <> 0 or esclavo[secadora].y2 <> 0 : 
						temp1=str(interpolar(ord(datos[2])*256+ord(datos[3]),esclavo[secadora].x1,esclavo[secadora].x2,esclavo[secadora].y1,esclavo[secadora].y2))
						temp2=str(interpolar(ord(datos[4])*256+ord(datos[5]),esclavo[secadora].x1,esclavo[secadora].x2,esclavo[secadora].y1,esclavo[secadora].y2))
					else:
						temp1=str((ord(datos[2])*256+ord(datos[3])))
						temp2=str((ord(datos[4])*256+ord(datos[5])))
					
					esclavo[secadora].temp1=temp1
					esclavo[secadora].temp2=temp2
					entrada1=str(ord(datos[6]))
					entrada2=str(ord(datos[7]))				
					esclavo[secadora].entrada1=entrada1
					esclavo[secadora].entrada2=entrada2
					if int(entrada1):
						formula=obtenerformula(datos[8:13])
					else:
						formula='0'
					esclavo[secadora].formula=formula
					display=datos[8:92]
					display=display.replace(chr(0),' ')
					display=display.replace(chr(10),' ')
					display=display.replace(chr(239),'')
					display=display.replace(chr(191),'')
					display=display.replace(chr(189),'')
					display=display.replace(chr(34),'')
					display=display.replace(chr(39),' ')
					esclavo[secadora].display=display
					version=str((ord(datos[92]) * 100) + ord(datos[93]))
					esclavo[secadora].tiemporespuesta=esclavo[secadora].ultimarespuesta-esclavo[secadora].ultimallamada

					imprimir(secadora,'verde')
					listaok.append(secadora)

					almacenar(str(secadora),temp1,temp2,formula,display,entrada1,entrada2,version)

			#else:
				#sys.stdout.write('\0\033[3d')
				#printw(str(ord(datos[1])))
				#printw(' ')
				#printw(str(ord(datos[94])))
				#printw(str(lo(crc16(datos[:94]))))
				#printw(' ')
				#printw(str(ord(datos[95])))
				#printw(str(hi(crc16(datos[:94]))))

				#sys.stdout.write('\0\033[32d')
				#printw(datos,90)


			datos=''

def read_from_port(ser):
    while True:
        reading = ser.readline()
        handle_data(reading)

esclavo={}

cfg = ConfigParser.RawConfigParser()
cfg.read('dryermon.ini')
try:
	sServidor=cfg.get('database','server')
except:
	sServidor='localhost'

conectar()
ser=serial.Serial('/dev/ttyUSB0', 9600, timeout=0.1)


thread = threading.Thread(target=read_from_port, args=(ser,))
thread.start()

i=0
ahora=datetime.datetime.now()
datos=''
lista=[]
listabad=[]
listaok=[]
while True:
	ahora=datetime.datetime.now()
	if (ahora - alivedb).seconds > 3600:
		dbping()
	while len(listaok)>0:
		i=listaok.pop()	
		ser.write(chr(6)+chr(i)+chr(lo(crc16(chr(6)+chr(i))))+chr(hi(crc16(chr(6)+chr(i)))))
		time.sleep(0.1)
	while len(listabad)>0:
		i=listabad.pop()	
		ser.write(chr(15)+chr(i)+chr(lo(crc16(chr(15)+chr(i))))+chr(hi(crc16(chr(15)+chr(i)))))
		time.sleep(0.1)			
	if len(lista)==0:
		for i in esclavo:
			if (ahora - esclavo[i].ultimarespuesta).seconds < 60:
				if (ahora - esclavo[i].ultimarespuesta).seconds > 20:
					lista.append(i)
		while len(lista)==0:	
			time.sleep(0.1)
			ahora=datetime.datetime.now()
			for i in esclavo:
				if (ahora - esclavo[i].ultimarespuesta).seconds > 5:
					lista.append(i)
		lista.reverse()
	datos=''
	i=lista.pop()


	sys.stdout.write('\0\033[1;32m')
	sys.stdout.write('\0\033[1;1H')
	printw(str(datetime.datetime.now()),19)
	printw(str(i))

	esclavo[i].ultimallamada=datetime.datetime.now()
	ser.write(chr(5)+chr(i)+chr(lo(crc16(chr(5)+chr(i))))+chr(hi(crc16(chr(5)+chr(i)))))
	time.sleep(0.1)

	for i in esclavo:
		if (ahora - esclavo[i].ultimarespuesta).seconds < 60:
			if (ahora - esclavo[i].ultimarespuesta).seconds > 40:
				esclavo[i].tiemporespuestas=datetime.datetime.now()-esclavo[i].ultimarespuesta
				imprimir(i,'amarillo')
			elif (ahora - esclavo[i].ultimarespuesta).seconds > 3:
				#esclavo[i].tiemporespuestas=datetime.datetime.now()-esclavo[i].ultimarespuesta
				imprimir(i)
		if (ahora - esclavo[i].ultimarespuesta).seconds > 60:
			listabad.append(i)
			borrar(i)


	time.sleep(0.3)

