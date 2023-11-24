##
#Envía un correo con una notificación de alerta
#Modificado por Sergio Rodriguez R. 2023

from datetime import datetime
import subprocess
from pysnmp.hlapi import *
import smtplib

correoRAM = False
correoPC = False
correoDisco = False

def enviarCorreo(contraseña, mensaje):
    nombre_servidor_smtp = 'smtp-mail.outlook.com'
    nombre_originario = 'Sergio Rodriguez'
    originario = 'ingensiscomescom@outlook.com'
    #contraseña = argv[1] #La contraseña se pasara por parámetro
    destinatario = 'sergiorr1995@gmail.com'
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

def despliega(iterador):
    while True:
        try:
            errorIndication, errorStatus, errorIndex, varBinds = next(iterador)
            if not errorIndication and not errorStatus:
                for name, val in varBinds:
                    return val #varBind
            else:
                print("Error:",errorStatus)
        except StopIteration:
            return

def getSTATUS(ip,OID):
    #ip = argv[1] #'4.28.200.10'
    puerto = 161
    #OID = '1.3.6.1.4.1.2021.10.1.3.1' #'1.3.6.1.2.1.1.5.0' # nombre del host

    iterador = getCmd(
        SnmpEngine(),
        UsmUserData('usuario',authKey='password123',authProtocol=usmHMACSHAAuthProtocol,privKey='password123',privProtocol=usmAesCfb128Protocol),
        UdpTransportTarget((ip,puerto)),
        ContextData(),
        ObjectType(ObjectIdentity(OID)))

    return despliega(iterador)

while True:
    valorCPU = getSTATUS("4.28.50.2",'1.3.6.1.4.1.2021.10.1.3.1')
    if (float(valorCPU) >= 90.0) and (not correoPC):
        print("Alerta de CPU\nLa PC4 esta usando: ",float(valorCPU))
        if not correoPC:
            mensaje='Alerta de CPU\n'+f'La PC4 esta usando: {valorCPU}% de CPU'+ f'\nLa fecha es: {datetime.today()}'+f'\nEl nombre de la maquina es: {getSTATUS("4.28.50.2","1.3.6.1.2.1.1.5.0")}'
            
            enviarCorreo("Contraseña", mensaje)
            print("Correo enviado!!")
            correoPC = True

    valorCPU = getSTATUS("4.28.50.1",'1.3.6.1.4.1.2021.10.1.3.1')
    if (float(valorCPU) >= 90.0) and (not correoPC):
        print("Alerta de CPU\nLa PC5 esta usando: ",float(valorCPU))
        
        mensaje='Alerta de CPU\n'+f'La PC4 esta usando: {valorCPU}% de CPU'+ f'\nLa fecha es: {datetime.today()}'+f'\nEl nombre de la maquina es: {getSTATUS("4.28.50.2","1.3.6.1.2.1.1.5.0")}'
        
        enviarCorreo("Contraseña", mensaje)
        print("Correo enviado!!")
        correoPC = True

    freeSWAP  = getSTATUS("4.28.50.2",'1.3.6.1.4.1.2021.4.4.0')
    totalSWAP = getSTATUS("4.28.50.2",'1.3.6.1.4.1.2021.4.3.0')
    valorSWAP = float(freeSWAP)/float(totalSWAP)
    if float(valorSWAP) >= 90.0:
        print("Alerta de RAM\nLa PC4 esta usando: ",float(valorSWAP))

    freeSWAP  = getSTATUS("4.28.50.1",'1.3.6.1.4.1.2021.4.4.0')
    totalSWAP = getSTATUS("4.28.50.1",'1.3.6.1.4.1.2021.4.3.0')
    valorSWAP = float(freeSWAP)/float(totalSWAP)
    if float(valorSWAP) >= 90.0:
        print("Alerta de RAM\nLa PC5 esta usando: ",float(valorSWAP))

    usedRAM  = getSTATUS("4.28.50.2",'1.3.6.1.4.1.2021.4.6.0')
    totalRAM = getSTATUS("4.28.50.2",'1.3.6.1.4.1.2021.4.5.0')
    valorRAM = float(usedRAM)/float(totalRAM)
    if float(valorRAM) >= 90.0:
        print("Alerta de RAM\nLa PC4 esta usando: ",float(valorRAM))

    usedRAM  = getSTATUS("4.28.50.1",'1.3.6.1.4.1.2021.4.6.0')
    totalRAM = getSTATUS("4.28.50.1",'1.3.6.1.4.1.2021.4.5.0')
    valorRAM = float(usedRAM)/float(totalRAM)
    if float(valorRAM) >= 90.0:
        print("Alerta de RAM\nLa PC5 esta usando: ",float(valorRAM))



#'1.3.6.1.4.1.2021.10.1.3.1' CARGA DEL CPU EN EL ULTIMO MINUTO
#'1.3.6.1.4.1.2021.4.6.0' TOTAL DE RAM UTILIZADA
#'1.3.6.1.4.1.2021.9.1.9' PORCENTAJE DE ESPACIO UTILIZADO EN CADA DISCO
### CORREO INCLUIRÁ
## FECHA Y HORA EN QUE SE GENERO LA NOTIFICACIÓN 
#'1.3.6.1.2.1.1.5.0' NOMBRE DEL DISPOSITIVO
## TIPO DE NOTIFICACIÓN (CPU, RAM, O DISCO) Y NOMBRE EN CASO DEL DISCO
#'1.3.6.1.4.1.2021.9.1.2' MUESTRA LAS PARTICIONES #RUTA DE LOS DISPOSITIVOS DE CADA PARTICIÓN

#"/run/lock" DISCO A LLENAR 1.3.6.1.4.1.2021.9.1.2

#snmpwalk -v3 -l authPriv -u usuario -a SHA -A password123 -x AES -X password123 4.28.50.2 1.3.6.1.4.1.2021.10.1.3.1
# 1.3.6.1.4.1.2021.9.1.3
# 1.3.6.1.4.1.2021.9.1.9

#OID_CPUsobrecarga = '1.3.6.1.4.1.2021.10.1.3.1'
#OID_RAMTotal = '1.3.6.1.4.1.2021.4.5.0'
#OID_RAMUsada = '1.3.6.1.4.1.2021.4.6.0'
#OID_SWAPDisponible = '1.3.6.1.4.1.2021.4.4.0'
#OID_SWAPTotal = '1.3.6.1.4.1.2021.4.3.0'