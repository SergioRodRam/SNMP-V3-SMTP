#SNMPTrapReceiver-v3.py
#python snmp trap receiver
#Fuente: Python SNMP trap receive
#Modificado por Carlos Pineda G. 2022
#Modificado por Sergio Rodriguez R. 2023

from pysnmp.entity import engine, config
from pysnmp.carrier.asyncore.dgram import udp
from pysnmp.entity.rfc3413 import ntfrcv
from pysnmp.proto.api import v2c
import smtplib
#from sys import argv #Para pasar argumentos por el programa

ip='4.28.200.10'
puerto=162

def get(OID):
    while True:
        iterator = getCmd(
            SnmpEngine(),
            UsmUserData('usuario', authKey='password123', authProtocol=usmhHMACSHAAuthProtocol, privKey='password123', privProtocol=usmAesCfb128Protocol),
            UdpTransportTarget((ip,puerto)),
            ContextData(),
            ObjectType(ObjectIdentity(OID))
        )
        errorIndication, errorStatus, errorIndex, varBinds = next(iterator)

        if not errorIndication and not errorStatus:
            for name, val in varBinds:
                return val
        else:
            print("Error:",errorIndication)

def enviarCorreo(contraseña, mensaje):
    nombre_servidor_smtp = 'smtp-mail.outlook.com' #Para correos de outlook
    nombre_originario = 'Sergio Rodriguez'
    originario = 'correo@outlook.com'
    #contraseña = argv[1] #La contraseña se pasara por parámetro
    destinatario = 'destinatario@algo.com'
    asunto = 'Alerta!!'
    #mensaje = 'Este es un mensaje mandado por smtp'

    try:
        smtp = smtplib.SMTP(nombre_servidor_smtp, 587)
        smtp.starttls()
        smtp.login(originario, contraseña)
        encabezado = 'To:' + destinatario + '\n' + 'From:' + nombre_originario + '<' + originario + '>' + '\n' + 'Subject:' + asunto + '\n'
#        print(encabezado)
        smtp.sendmail(originario, destinatario, encabezado + '\n' + mensaje + '\n')
#        print('OK')
#        print(argv[1])
    except Exception as e:
        print(e)
    finally:
        smtp.close()

snmpEngine = engine.SnmpEngine()
TrapAgentAddress=''; #Trap listerner address (la cadena vacía '' indica localhost)
Port=162;  #trap listerner port

config.addTransport(
    snmpEngine,
    udp.domainName,
    udp.UdpTransport().openServerMode((TrapAgentAddress, Port))
)

# para SNMP versión 3 utilizamos un usuario con autenticación y encriptado, así mismo, cada router se identifica con un ID de engine.
# el usuario puede ser el mismo en los diferentes routers.

config.addV3User(snmpEngine,'usuario',config.usmHMACSHAAuthProtocol,'password123',config.usmAesCfb128Protocol,'password123',securityEngineId=v2c.OctetString(hexValue='8000000001020303'))
#config.addV3User(snmpEngine,'usuario',config.usmHMACSHAAuthProtocol,'password123',config.usmAesCfb128Protocol,'password123',securityEngineId=v2c.OctetString(hexValue='8000000001020304'))
#config.addV3User(snmpEngine,'usuario',config.usmHMACSHAAuthProtocol,'password123',config.usmAesCfb128Protocol,'password123',securityEngineId=v2c.OctetString(hexValue='8000000001020305'))

def cbFun(snmpEngine,stateReference,contextEngineId,contextName,varBinds,cbCtx):
    print("Received new Trap message")
    print("contextEngineId=",contextEngineId.prettyPrint())
    for name, val in varBinds:
        print(name,'=',val)
    #enviarCorreo('Contraseña', 'El nombre de la interface es: ')

ntfrcv.NotificationReceiver(snmpEngine,cbFun)
snmpEngine.transportDispatcher.jobStarted(1)

try:
    snmpEngine.transportDispatcher.runDispatcher()
except:
    snmpEngine.transportDispatcher.closeDispatcher()
    raise
