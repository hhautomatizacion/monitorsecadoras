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
	global sUsuario
	global sPassword
	global totalesclavos

	datosrespuestas.append('\0\033[1;32m' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + '\0\033[1;33m' + ' * Conectando al servidor ' + sServidor + ' *')
	db = MySQLdb.connect(sServidor,sUsuario,sPassword,'dryermon')
	cursor = db.cursor()
	cursor.execute('SELECT * FROM esclavos WHERE habilitado=1 ORDER BY nombre')
	rows=cursor.fetchall()
	esclavo={}
	ahora=datetime.datetime.now() - datetime.timedelta(seconds=alertaroja)
	alivedb=datetime.datetime.now()
	iter=0
	for row in rows:
		iter=iter+1
		esclavo[row[1]]=slave(int(row[1]),row[2],iter,'0','0','0','0','0',' ' * 84,int(row[4]),int(row[5]),int(row[6]),int(row[8]),int(row[7]),int(row[9]),int(row[10]),int(row[11]),ahora,ahora,ahora,ahora)
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
		datosrespuestas.append('\0\033[1;31m' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + '\0\033[1;31m' + ' Error MySQL connection')
		conectar()
	finally:
		alivedb=datetime.datetime.now()


def formatominseg(t):
	try:
		horas,resto = divmod(t.total_seconds(),3600)
		minutos,segundos = divmod(resto,60)
	except:
		minutos=0
		segundos=0
	return str(int(minutos)) + ':' + str(int(segundos)).zfill(2)

def formatoseg(t):
	try:
		segundos = t.total_seconds()
		if segundos > 60:
			return '-'
	except:
		segundos = 0.0
	return '{:5,.2f}'.format(segundos)

def interpolar(x,x1=268,x2=293,y1=88,y2=110):
	return int(float(float(x)-float(x1))*float((float(y2)-float(y1))/(float(x2)-float(x1)))+float(y1))

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
	if width >67:
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
		printw(esclavo[secadora].display,width-67)
		printw(str(esclavo[secadora].version))
		printw(formatoseg(esclavo[secadora].tiemporespuesta),7)
		printw(formatominseg(esclavo[secadora].tiemporespuestas),7)

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
			if display.find(':') > 0:
				f=str(int(display[0:display.find(':')]))
			else:
				f='0'
		else:
			f='0'
	except e:
		f='0'
	finally:
		return f

def obtenerpaso(display):
	p='0'
	try:
		if len(display):
			if display.find('Paso #') > 0:
				p=str(int(display[display.find('Paso #')+6:display.find('Paso #')+9]))
			else:
				p='0'
		else:
			p='0'
	except e:
		p='0'
	finally:
		return p

def handle_data(datos):
	global esclavo
	global respuestas
	global datosrespuestas

	secadora=''
	temp1=''
	temp2=''
	entrada1=''
	entrada2=''
	formula=''
	paso=''
	display=''
	version=''
	debug='\0\033[1;34m' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))+ '\0\033[1;37m'

	if len(datos)>0:
		if len(datos) >= 96:
			debug=debug+str(len(datos))
			for iter in range(0,len(datos)):
				debug = debug +','+ str(ord(datos[iter]))
			datosrespuestas.append(debug)
			for iter in range(0,len(datos)-95):
				if ord(datos[iter + 94]) == lo(crc16(datos[:iter + 94])) and ord(datos[iter + 95]) == hi(crc16(datos[:iter + 94])) :			
					secadora=ord(datos[iter + 1])
					if secadora in esclavo:
						respuestas.append('\0\033[1;36m' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))+ '\0\033[1;37m' + ' '+str(ord(datos[iter + 1])).center(5) + str(len(datos)).center(5))
						version = str((ord(datos[iter + 92]) * 100) + ord(datos[iter + 93]))
						if esclavo[secadora].version == int(version) :
							esclavo[secadora].tiemporespuestas=datetime.datetime.now()-esclavo[secadora].ultimarespuesta
							esclavo[secadora].ultimarespuesta=datetime.datetime.now()
							if esclavo[secadora].t1 == 0:
								temp1='0'
							else:
								if esclavo[secadora].x1 <> 0 or esclavo[secadora].y1 <> 0 or esclavo[secadora].x2 <> 0 or esclavo[secadora].y2 <> 0 : 
									temp1=str(interpolar(ord(datos[iter + 2])*256+ord(datos[iter + 3]),esclavo[secadora].x1,esclavo[secadora].x2,esclavo[secadora].y1,esclavo[secadora].y2))
								else:
									temp1=str((ord(datos[iter + 2])*256+ord(datos[iter + 3])))
							if esclavo[secadora].t2 == 0:
								temp2='0'
							else:
								if esclavo[secadora].x1 <> 0 or esclavo[secadora].y1 <> 0 or esclavo[secadora].x2 <> 0 or esclavo[secadora].y2 <> 0 : 
									temp2=str(interpolar(ord(datos[iter + 4])*256+ord(datos[iter + 5]),esclavo[secadora].x1,esclavo[secadora].x2,esclavo[secadora].y1,esclavo[secadora].y2))
								else:
									temp2=str((ord(datos[iter + 4])*256+ord(datos[iter + 5])))
							esclavo[secadora].temp1=temp1
							esclavo[secadora].temp2=temp2
							entrada1=str(ord(datos[iter + 6]))
							entrada2=str(ord(datos[iter + 7]))
							display=datos[iter+8:iter+92]
							display=display.replace(chr(0),' ')
							display=filter(lambda x: x in string.letters + string.digits + string.punctuation + ' ',display)
							display=display.replace(chr(34),' ')
							display=display.replace(chr(39),' ')
							esclavo[secadora].display=display
							esclavo[secadora].tiemporespuesta=esclavo[secadora].ultimarespuesta-esclavo[secadora].ultimallamada
							if int(entrada1):
								formula=obtenerformula(display)
								paso=obtenerpaso(display)
							else:
								paso='0'
								formula='0'
							esclavo[secadora].formula=formula
							esclavo[secadora].entrada1=entrada1
							esclavo[secadora].entrada2=entrada2
							almacenar(str(secadora),temp1,temp2,formula,display,entrada1,entrada2,version)
							datosrespuestas.append('\0\033[1;34m' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))+ '\0\033[1;37m' + esclavo[secadora].nombre.center(7) + temp1.center(7) + temp2.center(7) + entrada1.center(3) + entrada2.center(3) + display + version.center(7) + formatoseg(esclavo[secadora].tiemporespuesta).center(7) + formatominseg(esclavo[secadora].tiemporespuestas).center(7))
							listaok.append(secadora)
						else:
							respuestas.append('\0\033[1;31m' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + '\0\033[1;33m' + ' ' + str(ord(datos[iter + 1])).center(5) + ' VER ')

def refresco_pantalla():
	global esclavollamada
	global totalesclavos
	global lista
	global sVersion
	global sEstadoPuertos
	sEstado=''
	while True:
		width,height=terminalsize.get_terminal_size()
		maxlista=height - totalesclavos - 2
		if not HiloPuertos.isAlive():
			HiloPuertos.start()

		if maxlista > 1:
			escribir (height - 1, '-'*(width-1))
			sEstado = 'Version: ' + sVersion + ' |' + sEstadoPuertos + str(HiloPuertos.isAlive()) 
			if len(sEstado) < width:
				escribir (height , sEstado + ' ' * (width - 1 - len(sEstado)))
			escribir (totalesclavos + 1, '-'*(width-1))
			i=1
			for x in respuestas:
				i=i+1
				if i <= maxlista:
					escribir(i + totalesclavos,x)
				else:
					respuestas.pop(0)
			i=1
			for x in datosrespuestas:
				i=i+1
				if i <= maxlista:
					if width > 60:
						if len(x) - 16 > width - 32:
							escribir(i + totalesclavos,x[:width - 16],32)
						else:
							escribir(i + totalesclavos,x + (width - 32 - (len(x)-16)) * ' ',32)				
				else:
					datosrespuestas.pop(0)
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
	os.system('img2txt --width='+ str(width) + ' --height=' + str(height - 3) + ' dryermon.jpg')
	datosrespuestas.append('\0\033[1;32m' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))+ '\0\033[1;31m' + ' * Creado por emmanuel156@gmail.com *')
	datosrespuestas.append('\0\033[1;32m' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))+ '\0\033[1;31m' + ' * Proyectos de automatizacion H&H *')	
	time.sleep(5)
	sys.stdout.write('\0\033[0m')

def escribir_en_puertos(cadena):
	global puertos
	global sEstadoPuertos

	sEstadoPuertos=''
	for ser in puertos:
		sEstadoPuertos= sEstadoPuertos + ' [' + ser.port + ', ' + str(ser.inWaiting()) + ']'
		ser.write(cadena)
		ser.flush()

def read_from_port():
	global puertos
	while True:
		for ser in puertos:
			reading = ser.read(96)
			handle_data(reading)

def getsetting(sSeccion,sClave,sDefault=''):
	sSetting=''
	cfg = ConfigParser.RawConfigParser()
	cfg.read('dryermon.ini')
	try:
		sSetting=cfg.get(sSeccion,sClave)
	except:
		if not cfg.has_section(sSeccion):
			cfg.add_section(sSeccion)
		if not cfg.has_option(sSeccion,sClave):
			cfg.set(sSeccion,sClave,sDefault)
		with open('dryermon.ini', 'w') as configfile:
			cfg.write(configfile)
		sSetting=sDefault
	return sSetting


sVersion = '1.01'
esclavo={}
puertos=[]
sEstadoPuertos=''
car=0
cnt=[]
i=0
esclavollamada=0
totalesclavos=0

ahora=datetime.datetime.now()
respuestas=[]
datosrespuestas=[]

lista=[]
listabad=[]
listaok=[]


splashscreen()

sServidor=getsetting('database','server','localhost')
sUsuario=getsetting('database','user','manttocl')
sPassword=getsetting('database','password','')
alertaverde=int(getsetting('time','green','3'))
alertaamarilla=int(getsetting('time','yellow','20'))
alertaroja=int(getsetting('time','red','90'))
pausalistaok=float(getsetting('pause','ok','0.2'))
pausalistabad=float(getsetting('pause','bad','0.2'))
pausallamadas=float(getsetting('pause','call','0.5'))

i=0
for i in range(0,10):
	try:
		sPuerto=getsetting('ports','port'+str(i),'')
		if len(sPuerto):
			puertos.append(serial.Serial(sPuerto, 9600, timeout=0.3))
			datosrespuestas.append('\0\033[1;32m' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + '\0\033[1;33m' + ' * ' + sPuerto + ' *')
	except:
		time.sleep(1)

conectar()

HiloPuertos = threading.Thread(target=read_from_port)

HiloPantalla = threading.Thread(target=refresco_pantalla)
HiloPantalla.start()


while True:
	ahora=datetime.datetime.now()
	if (ahora - alivedb).seconds > 3600:
		dbping()
	if len(lista) <= 0:
		for i in esclavo:
			if (ahora - esclavo[i].ultimarespuesta).seconds > alertaroja:
				listabad.append(int(i))
		for i in listabad:
			escribir_en_puertos(chr(15)+chr(i)+chr(lo(crc16(chr(15)+chr(i))))+chr(hi(crc16(chr(15)+chr(i)))))
			time.sleep(pausalistabad)
		listabad=[]
		for i in listaok:
			escribir_en_puertos(chr(6)+chr(i)+chr(lo(crc16(chr(6)+chr(i))))+chr(hi(crc16(chr(6)+chr(i)))))
			time.sleep(pausalistaok)
		listaok=[]

	if len(lista) <= 0:
		for i in esclavo:
			if (ahora - esclavo[i].ultimarespuesta).seconds < alertaroja:
				if (ahora - esclavo[i].ultimarespuesta).seconds > alertaamarilla:
					lista.append(int(i))
		lista=sorted(lista,key=lambda i:esclavo[i].ultimarespuesta)
		lista.reverse()
			
	if len(lista) <= 0:
			
		for i in esclavo:
			lista.append(int(i))
		lista=sorted(lista,key=lambda i:esclavo[i].ultimarespuesta)
		lista.reverse()
	i=lista.pop()
	respuestas.append('\0\033[1;34m' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))+ '\0\033[1;37m' + ' '+str(i).center(10))
	esclavollamada=i
	esclavo[i].ultimallamada=datetime.datetime.now()
	escribir_en_puertos(chr(5)+chr(i)+chr(lo(crc16(chr(5)+chr(i))))+chr(hi(crc16(chr(5)+chr(i)))))
	time.sleep(pausallamadas)

