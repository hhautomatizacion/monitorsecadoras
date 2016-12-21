import MySQLdb
import datetime
import sys
import terminalsize
import ConfigParser

class slave:
        def __init__(self,numero,nombre,entrada1):
                self.numero=numero
                self.nombre=nombre
                self.entrada1=entrada1

def conectar():
        global cursor
        global db
        global esclavo
        global alivedb
        global sServidor
	global sUsuario 
	global sPassword
        db = MySQLdb.connect(sServidor,sUsuario,sPassword,'dryermon')
        cursor = db.cursor()
        cursor.execute('SELECT esclavo,nombre FROM esclavos WHERE habilitado=1 ORDER BY nombre')
        rows=cursor.fetchall()
        esclavo={}
        for row in rows:
                esclavo[row[0]]=slave(int(row[0]),row[1],0)


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


sServidor=getsetting('database','server','localhost')
sUsuario=getsetting('database','user','manttocl')
sPassword=getsetting('database','password','')

conectar()
ahora=datetime.datetime.now()

width,height=terminalsize.get_terminal_size()
minutos=width-10

sys.stdout.write( "*".center(7)+'|')
for i in range (minutos,0,-10):
	sys.stdout.write('|'+str(ahora - datetime.timedelta(minutes=i))[11:16].center(9))
ahora=datetime.datetime.now()
sys.stdout.write('\n')

cursor = db.cursor()
for e in esclavo:
	sys.stdout.write(str(e).center(7)+'|')
	for i in range (minutos,-1,-1):
		cursor.execute("SELECT entrada1 FROM lecturas WHERE secadora=" + str(e) +  " AND fecha >= DATE_SUB(NOW(),INTERVAL "+ str(i+1) +  " MINUTE) AND fecha < DATE_SUB(NOW(),INTERVAL " + str(i) + " MINUTE) LIMIT 1")
		rows=cursor.fetchall()
		if len(rows) == 0:
			sys.stdout.write(' ')
		for row in rows:
			if row[0]==0:
				sys.stdout.write('0')
			else:
				sys.stdout.write('1')
	sys.stdout.write('\n')
