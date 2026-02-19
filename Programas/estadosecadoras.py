import MySQLdb
import datetime
import sys
import terminalsize
import ConfigParser

class slave:
        def __init__(self,numero,nombre,entrada1,estado):
                self.numero=numero
                self.nombre=nombre
                self.entrada1=entrada1
                self.estado=estado

def conectar():
        global cursor
        global db
        global esclavo
        global alivedb
        global sServidor
        global sUsuario 
        global sPassword
        db = MySQLdb.connect(sServidor, sUsuario, sPassword, 'dryermon')
        cursor = db.cursor()
        cursor.execute('SELECT esclavo,nombre FROM esclavos WHERE habilitado=1 ORDER BY nombre')
        rows=cursor.fetchall()
        esclavo={}
        for row in rows:
                esclavo[row[0]]=slave(int(row[0]),str(row[1]),0,'')


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

width,height=terminalsize.get_terminal_size()
intervalo=60

cursor = db.cursor()

cursor.execute('SELECT (TO_SECONDS(DATE_SUB(NOW(), INTERVAL ' + str(intervalo * (width - 7)) + ' SECOND )) DIV ' + str(intervalo) + '),DATE_SUB(NOW(), INTERVAL ' + str(intervalo * (width - 7)) + ' SECOND )')
rows=cursor.fetchall()
for row in rows:
        inicio=int(row[0])
        iniciostr=str(row[1])
for e in esclavo:
        esclavo[e].estado=' ' * (width - 6)

etiquetas=['|---------']* int((width - 7) / 10)

cursor.execute('SELECT (TO_SECONDS(fecha) DIV ' + str(intervalo) + ') AS i,secadora, TIME(fecha), entrada1 FROM lecturas WHERE fecha>"'+ iniciostr +'" GROUP BY secadora, (TO_SECONDS(fecha) DIV ' + str(intervalo) + ')')
rows=cursor.fetchall()
for row in rows:
        pos=int(row[0]) - inicio - 1
        if (pos % 10 == 0) and ( int(pos / 10) < len(etiquetas)) :
            
                etiquetas[int(pos / 10)]='|' + str(row[2])[:5].center(9)
        if pos >= 0:
                esclavo[int(row[1])].estado =  esclavo[int(row[1])].estado[:pos] + esclavo[int(row[1])].estado[pos:].replace(' ', str(row[3]),1)

sys.stdout.write( "*".center(4)+'|') 

for i in etiquetas:
        sys.stdout.write(i)
        
sys.stdout.write('\n')
for e in esclavo:
	sys.stdout.write(esclavo[e].nombre.center(4)+'|')
	sys.stdout.write(esclavo[e].estado)
	sys.stdout.write('\n')
