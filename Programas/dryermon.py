import os
import threading
import serial
import time
import datetime
import sys
import terminalsize
import MySQLdb
import ConfigParser
import string
from math import trunc

class slave:
	def __init__(self,numero,nombre,renglon,temp1,temp2,entrada1,entrada2,formula,display,version,habilitado,x1,y1,x2,y2,t1,t2,ultimallamada,ultimarespuesta,tiemporespuesta,tiemporespuestas):
		self.numero=numero
		self.nombre=nombre
		self.renglon=renglon
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
	global totalesclavos
	db = MySQLdb.connect(sServidor,'root','manttocl','dryermon')
	cursor = db.cursor()
	cursor.execute('SELECT * FROM esclavos WHERE habilitado=1 ORDER BY nombre')
	rows=cursor.fetchall()
	esclavo={}
	ahora=datetime.datetime.now() - datetime.timedelta(seconds=(alertaroja * 0.75))
	alivedb=datetime.datetime.now()
	iter=0
	for row in rows:
		iter=iter+1
		esclavo[row[1]]=slave(int(row[1]),row[2],iter,'0','0','0','0','0','',int(row[4]),int(row[5]),int(row[6]),int(row[8]),int(row[7]),int(row[9]),int(row[10]),int(row[11]),ahora,ahora,ahora,ahora)
	totalesclavos=iter

def dbping():
	global db
	global alivedb
	datosrespuestas.append('\0\033[1;34m' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + '\0\033[1;33m' + ' Ping')
	try:	
		db.ping()
		alivedb=datetime.datetime.now()
	except MySQLdb.Error:
		datosrespuestas.append('\0\033[1;34m' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + '\0\033[1;31m' + ' MySQL error')

def almacenar(secadora,temp1,temp2,formula,display,entrada1,entrada2,version):
	global cursor
	global db
	global alivedb
	try:
		cursor.execute('INSERT INTO lecturas VALUES (0,now(),' + secadora + ',' + temp1 + ',' + temp2 + ',' + formula + ',"' + display + '",' + entrada1 + ',' + entrada2 + ',' + version + ',0)')
		db.commit()
	except MySQLdb.Error:
		conectar()
		datosrespuestas.append('\0\033[1;31m' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + '\0\033[1;31m' + ' Error MySQL connection')
	finally:
		alivedb=datetime.datetime.now()

def interpolar(x,x1=268,x2=293,y1=88,y2=110):
	return trunc(float(float(x)-float(x1))*float((float(y2)-float(y1))/(float(x2)-float(x1))))+float(y1)

def borrar(secadora):
	global esclavo
	width,height=terminalsize.get_terminal_size()
	sys.stdout.write('\0\033[' + str(esclavo[secadora].renglon) + ';1H')
	sys.stdout.write('\0\033[1;31m')
	printw(esclavo[secadora].nombre)
	printw('-',width-9)

def escribir(renglon, texto, columna=1):
	sys.stdout.write('\0\033[' + str(renglon) + ';' + str(columna) + 'H')
	sys.stdout.write('\0\033[1;37m')
	sys.stdout.write('|' + texto)
	sys.stdout.flush()	

def imprimir(secadora,color='blanco'):
	global esclavo
	width,height=terminalsize.get_terminal_size()
	if width >87:
		sys.stdout.write('\0\033[' + str(esclavo[secadora].renglon) + ';1H')
		if color=='blanco':
			sys.stdout.write('\0\033[1;37m')
		if color=='verde':
			sys.stdout.write('\0\033[1;32m')
		if color=='amarillo':
			sys.stdout.write('\0\033[1;33m')
		printw(esclavo[secadora].nombre)
		printw(esclavo[secadora].temp1,8)
		printw(esclavo[secadora].temp2,8)
		printw(esclavo[secadora].entrada1,3)
		printw(esclavo[secadora].entrada2,3)
		printw(esclavo[secadora].formula)
		printw(esclavo[secadora].display,width-87)
		printw(str(esclavo[secadora].version))
		printw(str(esclavo[secadora].tiemporespuesta),17)
		printw(str(esclavo[secadora].tiemporespuestas),17)

def printw(str, width=7):
	sys.stdout.write('\0\033[?25l')
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
	finally:
		return f

def handle_data(data):
	global datos
	global esclavo
	global respuestas
	global datosrespuestas

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
		if len(data)>1:
			respuestas.append('\0\033[1;36m' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))+ '\0\033[1;37m' + ' '+str(ord(data[1])).center(5) + str(len(data)).center(5))
		if len(datos)>96:
			datos=''
		if len(datos)==96:
			try:
				if ord(datos[94]) == lo(crc16(datos[:94])) and ord(datos[95]) == hi(crc16(datos[:94])) :			
					secadora=ord(datos[1])
					if secadora in esclavo:
						esclavo[secadora].tiemporespuestas=datetime.datetime.now()-esclavo[secadora].ultimarespuesta
						esclavo[secadora].ultimarespuesta=datetime.datetime.now()				
						if esclavo[secadora].t1 == 0:
							temp1='0'
						else:
							if esclavo[secadora].x1 <> 0 or esclavo[secadora].y1 <> 0 or esclavo[secadora].x2 <> 0 or esclavo[secadora].y2 <> 0 : 
								temp1=str(interpolar(ord(datos[2])*256+ord(datos[3]),esclavo[secadora].x1,esclavo[secadora].x2,esclavo[secadora].y1,esclavo[secadora].y2))
							else:
								temp1=str((ord(datos[2])*256+ord(datos[3])))
						if esclavo[secadora].t2 == 0:
							temp2='0'
						else:
							if esclavo[secadora].x1 <> 0 or esclavo[secadora].y1 <> 0 or esclavo[secadora].x2 <> 0 or esclavo[secadora].y2 <> 0 : 
								temp2=str(interpolar(ord(datos[4])*256+ord(datos[5]),esclavo[secadora].x1,esclavo[secadora].x2,esclavo[secadora].y1,esclavo[secadora].y2))
							else:
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
						display=filter(lambda x: x in string.letters + string.digits + string.punctuation + ' ',display)
						display=display.replace(chr(34),' ')
						display=display.replace(chr(39),' ')
						esclavo[secadora].display=display
						version=str((ord(datos[92]) * 100) + ord(datos[93]))
						esclavo[secadora].version=version
						esclavo[secadora].tiemporespuesta=esclavo[secadora].ultimarespuesta-esclavo[secadora].ultimallamada
						listaok.append(secadora)
						datosrespuestas.append('\0\033[1;34m' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))+ '\0\033[1;37m' + esclavo[secadora].nombre.center(7) + temp1.center(7) + temp2.center(7) + display)
						almacenar(str(secadora),temp1,temp2,formula,display,entrada1,entrada2,version)
													
			except:
				datosrespuestas.append(str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))+' ErrorRecepcion')
				
			datos=''

def refresco_pantalla():
	global esclavollamada
	global totalesclavos
	r=''
	while True:
		width,height=terminalsize.get_terminal_size()
		maxlista=height - totalesclavos -1
		if maxlista > 1:
			escribir (totalesclavos + 1, '-'*(width-1))
			while len(datosrespuestas) > maxlista:
				datosrespuestas.pop(0)	
			while len(respuestas) > maxlista:
				respuestas.pop(0)
			i=1
			for x in respuestas:
				i=i+1
				escribir(i + totalesclavos,x)
			i=1
			for x in datosrespuestas:
				i=i+1
				if width > 60:
					if len(x) - 16 > width - 32:
						escribir(i + totalesclavos,x[:width - 16],32)
					else:
						escribir(i + totalesclavos,x + (width - 32 - (len(x)-16)) * ' ',32)				
		for i in esclavo:
			ahora=datetime.datetime.now()
			if int((ahora - esclavo[i].ultimarespuesta).seconds) < alertaverde:
				imprimir(i,'verde')
			elif int((ahora - esclavo[i].ultimarespuesta).seconds) < alertaamarilla:
				imprimir(i)
			elif int((ahora - esclavo[i].ultimarespuesta).seconds) < alertaroja:
				esclavo[i].tiemporespuestas=datetime.datetime.now()-esclavo[i].ultimarespuesta
				imprimir(i,'amarillo')
			else:
				borrar(i)

def splashscreen():
	width,height=terminalsize.get_terminal_size()
	os.system('img2txt --width='+ str(width) + ' --height=' + str(height - 2) + ' dryermon.jpg')
	datosrespuestas.append('\0\033[1;32m' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))+ '\0\033[1;31m' + ' * Creado por emmanuel156@gmail.com *')
	datosrespuestas.append('\0\033[1;32m' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))+ '\0\033[1;31m' + ' * Proyectos de automatizacion H&H *')	
	time.sleep(5)		

def escribir_en_puertos(cadena):
	global puertos
	for ser in puertos:
		puertos[ser].write(cadena)

def read_from_port():
    global puertos
    while True:
	for ser in puertos:
	        reading = puertos[ser].read(96)
        	handle_data(reading)

def getsetting(sSeccion,sClave,sDefault=''):
	sSetting=''
	cfg = ConfigParser.RawConfigParser()
	cfg.read('dryermon.ini')
	try:
		sSetting=cfg.get(sSeccion,sClave)
	except:
		sSetting=sDefault
	return sSetting


esclavo={}
puertos={}


car=0
cnt=[]
i=0
datos=''
esclavollamada=0
totalesclavos=0
ahora=datetime.datetime.now()
respuestas=[]
datosrespuestas=[]
lista=[]
listaok=[]
listabad=[]

splashscreen()


for car in range(0,256):
	cnt.append(car)
	cnt[car]=0

sServidor=getsetting('database','server','localhost')
alertaverde=int(getsetting('time','green','3'))
alertaamarilla=int(getsetting('time','yellow','20'))
alertaroja=int(getsetting('time','red','90'))
pausalistaok=float(getsetting('pause','ok','0.2'))
pausalistabad=float(getsetting('pause','bad','0.2'))
pausallamadas=float(getsetting('pause','call','0.5'))


conectar()
i=0
for i in range(0,10):
	try:
		sPuerto=getsetting('ports','port'+str(i),'')
		if len(sPuerto):
			puertos[i]=serial.Serial(sPuerto, 9600, timeout=0.1)
			datosrespuestas.append('\0\033[1;32m' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + '\0\033[1;33m' + ' * ' + sPuerto + ' *')
			
	except:
		time.sleep(1)

thread = threading.Thread(target=read_from_port)
thread.start()

t=threading.Thread(target=refresco_pantalla)
t.start()


while True:
	ahora=datetime.datetime.now()
	if (ahora - alivedb).seconds > 3600:
		dbping()
	if len(lista)==0:
		respuestas.append('\0\033[1;35m' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))+ '\0\033[1;37m' + ' ' + 10*'-')
		if len(listaok)>0:
			while len(listaok)>0:
				i=listaok.pop()	
				escribir_en_puertos(chr(6)+chr(i)+chr(lo(crc16(chr(6)+chr(i))))+chr(hi(crc16(chr(6)+chr(i)))))
				time.sleep(pausalistaok)
			time.sleep(pausallamadas)
		if len(listabad)>0:
			while len(listabad)>0:
				i=listabad.pop()	
				escribir_en_puertos(chr(15)+chr(i)+chr(lo(crc16(chr(15)+chr(i))))+chr(hi(crc16(chr(15)+chr(i)))))
				time.sleep(pausalistabad)			
			time.sleep(pausallamadas)
		ahora=datetime.datetime.now()
		for i in esclavo:
			if (ahora - esclavo[i].ultimarespuesta).seconds < alertaroja:
				if (ahora - esclavo[i].ultimarespuesta).seconds > alertaamarilla:
					lista.append(i)
		if len(lista)==0:
			for i in esclavo:
				lista.append(i)
		lista=sorted(lista,key=lambda i:esclavo[i].ultimarespuesta)
		lista.reverse()

	datos=''
	i=lista.pop()
	respuestas.append('\0\033[1;34m' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))+ '\0\033[1;37m' + ' '+str(i).center(10))
	esclavollamada=i
	esclavo[i].ultimallamada=datetime.datetime.now()
	escribir_en_puertos(chr(5)+chr(i)+chr(lo(crc16(chr(5)+chr(i))))+chr(hi(crc16(chr(5)+chr(i)))))
	time.sleep(pausallamadas)

