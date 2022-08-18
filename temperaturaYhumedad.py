#**************************************************
#*** PONER EN True CUANDO SE PASE A PRODUCCIÓN ***
#**************************************************
PRODUCCION = True    

from threading import currentThread
import RPi.GPIO as GPIO # para el control de los GPIO de la raspberry
import Adafruit_DHT     # librería para el sensor de presión y temperatura
from tkinter import *   # librería para entorno gráfico
import logging          # para generar los log en un archivo txt    
import os               # para poder ejecutar comandos. En particular se usa para abrir el archivo de logs
from email.message import EmailMessage 
import smtplib

# CONSTANTES
TEMP_MIN = 10       # Temperatura mínima que se puede elegir
TEMP_MAX = 30       # Temperatura máxima que se puede elegir
HUMEDAD_MAX = 100   # Humedad máxima seteable
HUMEDAD_MIN = 30    # Humedad mínima seteable
COL_TEMP = 30       # Para el control de posición de la columna de los controles de temperatura
COL_HUM = 2         # Ídem para los controles de humedad
TIEMPO_REFRESCO_LECTURA_HUMEDAD = 10000     # En milisegundos!!
TIEMPO_REFRESCO_LECTURA_TEMPERATURA = 10000 # En milisegundos!!
INTERVALO_REGISTRO_LOG = 60000              # En milisegundos!! (cada medio minuto)
DIR_DONDE_GUARDO_LOS_LOGS = "/home/pi/pythonUDE/"
EDITOR_DE_TEXTOS  = "geany"
TEMPERATURA_ALARMA_CORREO = TEMP_MAX
REMITENTE = "pruebascosasmias@gmail.com"
CONTRASENIA = "xavnmqrxqzicoexf"
DESTINATARIOS = ["dariososasocias@gmail.com", "mail@gmail.com"]

# DEFINICIÓN DE LOS GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)                  # Se usa en modo BOARD
CALEFACTOR = 22                         # El led que representa el calefactor LED ROJO
GPIO.setup(CALEFACTOR, GPIO.OUT)        # Se setea el pin correspondiente como salida ya que va a controlar un actuador
GPIO.output(CALEFACTOR, False)          # El calefactor inicia apagado cuando arranca el sistema
VENTILADOR = 13                         # El led que representa el ventilador LED AZUL
GPIO.setup(VENTILADOR, GPIO.OUT)        # Se setea el pin correspondiente como salida ya que va a controlar un actuador
GPIO.output(VENTILADOR, False)          # El ventilador inicia apagado cuando arranca el sistema
HUMIDIFICADOR = 6                       # El led que representa el humidificador LED AMARILLO
GPIO.setup(HUMIDIFICADOR, GPIO.OUT)     # Se setea el pin correspondiente como salida ya que va a controlar un actuador
GPIO.output(HUMIDIFICADOR, False)       # El humidificador inicia apagado cuando arranca el sistema
DESHUMIDIFICADOR = 5                    # El led que representa el deshumidificador LED BLANCO
GPIO.setup(DESHUMIDIFICADOR, GPIO.OUT)  # Se setea el pin correspondiente como salida ya que va a controlar un actuador
GPIO.output(DESHUMIDIFICADOR, False)    # El humidificador inicia apagado cuando arranca el sistema
                      
PIN_SENSOR = 4                  # pin de lectura del sensor DHT11        
SENSOR = Adafruit_DHT.DHT11     # crea objeto llamado SENSOR. Es para usar en la lectura del DHT11

# DEFINICIONES PARA tkinter
ventana = Tk()                          # Definiciones de la librería tkinter
ventana.title("CONTROL DOMÓTICA")       # Título de la ventana
ventana.geometry("600x400")             # Define tamaño de pantalla
humedad_var = DoubleVar()               # variables para el slider (tkinter)
temp_var = DoubleVar()  
nueva_temp_umbral = StringVar()               # para definir la temp umbral de alarma
temp_umbral = TEMP_MAX
flag_alarma_temp = False


# tkinter - humedad medida por el sensor
etiqueta_humedad_amb = Label(ventana, text="Humedad", font=("Arial",15))
etiqueta_humedad_amb.grid(row = 2, column = COL_HUM, padx = 10, pady = 10, sticky = "nsew")
muestra_humedad_amb = Label(ventana, font=("Arial",20), fg = "red")
muestra_humedad_amb.grid(row = 3, column = COL_HUM, padx = 10, pady = 10, sticky = "nsew")

# tkinter - temperatura medida por el sensor
etiqueta_temp_amb = Label(ventana, text="Temperatura", font=("Arial",15))
etiqueta_temp_amb.grid(row = 2, column = COL_TEMP, padx = 10, pady = 10, sticky = "nsew")
muestra_temp_amb = Label(ventana, font=("Arial",20), fg = "red")
muestra_temp_amb.grid(row = 3, column = COL_TEMP, padx = 10, pady = 10, sticky = "nsew")

# tkinter - slider/selector de temperatura
etiqueta_temp = Label(ventana, text = "Selector Temperatura °C")   #define la etiqueta "Temperatura"
etiqueta_temp.grid(row=8,column=COL_TEMP, padx=10, pady=10)             #define la posición de la etiqueta
ctrl_temp = Scale(ventana, variable = temp_var, from_ = TEMP_MAX, to = TEMP_MIN, orient = VERTICAL, activebackground='green2', bd=5,)  #Define el slider de control de temp
ctrl_temp.grid(row=9,column=COL_TEMP, padx=10, pady=10)                                                                  #define su posición
ctrl_temp.set(25)

# tkinter - slider/selector de humedad
etiqueta_humedad = Label(ventana, text = "Selector Humedad %")                             #define la etiqueta "Humidity Selector"
etiqueta_humedad.grid(row=8,column=COL_HUM, padx=10, pady=10)                  #define la posición de la etiqueta
ctrl_humedad = Scale(ventana, variable = humedad_var, from_ = HUMEDAD_MAX , to = HUMEDAD_MIN, orient = VERTICAL, activebackground='green2', bd=5,)  #Define el slider de control de humedad
ctrl_humedad.grid(row=9,column=COL_HUM, padx=10, pady=10)                                                   #define su posición
ctrl_humedad.set(65)

# tkinter - umbral de temperatura
etiqueta_umbral_alarma_tem = Label(ventana, text='Umbral de temp. para alarma')
etiqueta_umbral_alarma_tem.grid(column=0, row=0, sticky='W', padx= 5, pady= 5)
cuadro_de_texto_temp_umbral = Entry(ventana, textvariable = nueva_temp_umbral)
cuadro_de_texto_temp_umbral.grid(column=1, row=0, padx=5, pady=5)
cuadro_de_texto_temp_umbral.focus()

# tkinter - alarma
muestra_alarma = Label(ventana, font=("Arial",20), fg = "red")
muestra_alarma.grid(row = 3, column = COL_TEMP, padx = 10, pady = 10, sticky = "nsew")

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s",handlers=[logging.FileHandler("logTemperatura_Humedad.txt"),])
logging.info('===================================================================================================================\n')
logging.info('                              I              Inicio del programa.')
logging.info('===================================================================================================================\n')
#************************************************************************************************************************
#****                                                        FUNCIONES                                               ****
#************************************************************************************************************************

""" Esta función hace:
    1) se para en el directorio donde está el archivo con los logs
    2) hace una copia del archivo porque no se puede abrir un archivo que esté en uso
    3) le otorga permisos de lectura a ese archivo copiado
    4) abre el archivo usando el editor seleccionado
    """
def abrir_archivo_logs():
    os.system("cd " + DIR_DONDE_GUARDO_LOS_LOGS)
    os.system("sudo cp logTemperatura_Humedad.txt copiaLogTemperatura_Humedad.txt")
    os.system("sudo chmod 100 copiaLogTemperatura_Humedad.txt")
    os.system(EDITOR_DE_TEXTOS +" "+ DIR_DONDE_GUARDO_LOS_LOGS + "copiaLogTemperatura_Humedad.txt")
    
def actualizar_temp_seleccionada():
    global temperatura_seleccionada
    temperatura_seleccionada = temp_var.get()
    control_termico()
    
def actualizar_humedad_seleccionada():
    global humedad_seleccionada
    humedad_seleccionada = humedad_var.get()
    control_humedad()


# Esta función se ejecuta cuando se presiona el botón confirmar asociado al slider temperatura.
# Hace que se accionen los controladores térmicos en base a la temperatura ambiente(sensor) y lo 
# seleccionado por el usuario (slider)
ultima_temperatura_medida = 25
temperatura_seleccionada = 25
def control_termico():
    global ultima_temperatura_medida
    global temperatura_seleccionada 
    temperatura_ambiente = leer_sensor_de_temperatura()

# Esto se necesita porque el sensor no lee cada vez que se lo interroga. Cuando no lee, responde None y eso da problemas al intentar imprimir
# en la pantalla de tkinter. Para solucionarlo se mantiene guardado el ultimo valor bueno medido. Además, actualizamos los registros solo
# si hay cambios en los valores medidos (por ej, para no recargar el log)
    if((temperatura_ambiente is not None) and (temperatura_ambiente != ultima_temperatura_medida)):                   
        ultima_temperatura_medida = int(temperatura_ambiente)
        
    if(temperatura_seleccionada > ultima_temperatura_medida):
        encender_calefactor()
    elif(temperatura_seleccionada == ultima_temperatura_medida):
        apaga_calefactor_y_ventilador()
    else:
        encender_ventilacion()

    ventana.after(TIEMPO_REFRESCO_LECTURA_TEMPERATURA, control_termico) # Periódicamente ejecuta la función por si hay que ajustar el control térmico en función de la 
                                                                        # temperatura hambiente y la seleccionada

# Enciende calefactor y apaga ventilador
def encender_calefactor():
    if(PRODUCCION):
        GPIO.output(CALEFACTOR, True)
        GPIO.output(VENTILADOR, False)
        logging.info("Temperatura: %s°C; Humedad: %s%s. Temperatura seleccionada: %s°C. Calefactor encendido y ventilación apagada" %(ultima_temperatura_medida, ultima_humedad_medida, "%", temperatura_seleccionada))
    else:
        print("Temperatura: %s°C; Humedad: %s%s. Temperatura seleccionada: %s°C. Calefactor encendido y ventilación apagada" %(ultima_temperatura_medida, ultima_humedad_medida, "%", temperatura_seleccionada)) #esto solo se imprime en test
        
# Enciende ventilador y apaga calefactor    
def encender_ventilacion():
    if(PRODUCCION):
        GPIO.output(CALEFACTOR, False)
        GPIO.output(VENTILADOR, True)
        logging.info("Temperatura: %s°C; Humedad: %s%s. Temperatura seleccionada: %s°C. Calefactor apagado y ventilación encendida" %(ultima_temperatura_medida, ultima_humedad_medida, "%", temperatura_seleccionada))
    else:
        print("Temperatura: %s°C; Humedad: %s%s. Temperatura seleccionada: %s°C. Calefactor apagado y ventilación encendida" %(ultima_temperatura_medida, ultima_humedad_medida, "%", temperatura_seleccionada)) #esto solo se imprime en test

#apaga ventilación y apaga calefactor  
def apaga_calefactor_y_ventilador():
    if(PRODUCCION):
        GPIO.output(VENTILADOR, False)
        GPIO.output(CALEFACTOR, False)
        logging.info("Temperatura: %s°C; Humedad: %s%s. Temperatura seleccionada: %s°C. Calefactor apagado y ventilación apagada" %(ultima_temperatura_medida, ultima_humedad_medida, "%", temperatura_seleccionada))
    else:
        print("Temperatura: %s°C; Humedad: %s%s. Temperatura seleccionada: %s°C. Calefactor apagado y ventilación apagada" %(ultima_temperatura_medida, ultima_humedad_medida, "%", temperatura_seleccionada)) #esto solo se imprime en test
        

# Esta función se ejecuta cuando se presiona el botón confirmar asociado al slider humedad.
# Hace que se accionen los controladores humificadores  en base a la humedad ambiente (sensor) y lo 
# seleccionado por el usuario (slider)        
ultima_humedad_medida = 65
humedad_seleccionada = 65
def control_humedad():
    global ultima_humedad_medida
    global humedad_seleccionada
    humedad_ambiente = leer_sensor_de_humedad()

# Esto se necesita porque el sensor no lee cada vez que se lo interroga. Cuando no lee, responde None y eso da problemas al intentar imprimir
# en la pantalla de tkinter. Para solucionarlo se mantiene guardado el ultimo valor bueno medido. Además, actualizamos los registros solo
# si hay cambios en los valores medidos (por ej, para no recargar el log)
    if((humedad_ambiente is not None) and (humedad_ambiente != ultima_humedad_medida)):               
        ultima_humedad_medida = int(humedad_ambiente)
        
    if(humedad_seleccionada > ultima_humedad_medida):
        encender_humidificador() 
    elif(humedad_seleccionada == ultima_humedad_medida):
        apaga_humidificador_y_deshumidificador()
    else:
        encender_deshumidificador()

    ventana.after(TIEMPO_REFRESCO_LECTURA_HUMEDAD, control_humedad) # Periódicamente ejecuta la función por si hay que ajustar el control térmico en función de la 
                                                                        # humedad hambiente y la seleccionada

#Enciende humidificador y apaga deshumidificador
def encender_humidificador():
    if(PRODUCCION):
        GPIO.output(HUMIDIFICADOR, True)
        GPIO.output(DESHUMIDIFICADOR, False)
        logging.info("Temperatura: %s°C; Humedad: %s%s. Humedad seleccionada: %s°C. Humidificador encendido y deshumidificador apagado" %(ultima_temperatura_medida, ultima_humedad_medida, "%", humedad_seleccionada))
    else:
        print("Temperatura: %s°C; Humedad: %s%s. Humedad seleccionada: %s°C. Humidificador encendido y deshumidificador apagado" %(ultima_temperatura_medida, ultima_humedad_medida, "%", humedad_seleccionada)) #esto solo se imprime en test

# Enciende deshumidificador y a paga humidificador       
def encender_deshumidificador():
    if(PRODUCCION):
        GPIO.output(HUMIDIFICADOR, False)
        GPIO.output(DESHUMIDIFICADOR, True)
        logging.info("Temperatura: %s°C; Humedad: %s%s. Humedad seleccionada: %s°C. Humidificador apagado y deshumidificador encendido" %(ultima_temperatura_medida, ultima_humedad_medida, "%", humedad_seleccionada))
    else:
        print("Temperatura: %s°C; Humedad: %s%s. Humedad seleccionada: %s°C. Humidificador apagado y deshumidificador encendido" %(ultima_temperatura_medida, ultima_humedad_medida, "%", humedad_seleccionada)) #esto solo se imprime en test

# Apaga humidificador y deshumidificador
def apaga_humidificador_y_deshumidificador():
    if(PRODUCCION):
        GPIO.output(DESHUMIDIFICADOR, False)
        GPIO.output(HUMIDIFICADOR, False)
        logging.info("Temperatura: %s°C; Humedad: %s%s. Humedad seleccionada: %s°C. Humidificador apagado y deshumidificador apagado" %(ultima_temperatura_medida, ultima_humedad_medida, "%", humedad_seleccionada))
    else:
        print("Temperatura: %s°C; Humedad: %s%s. Humedad seleccionada: %s°C. Humidificador apagado y deshumidificador apagado" %(ultima_temperatura_medida, ultima_humedad_medida, "%", humedad_seleccionada)) #esto solo se imprime en test


def interrogar_sensor_dht():                                   
    temperatura, humedad = Adafruit_DHT.read(SENSOR,PIN_SENSOR)
    
    return humedad, temperatura

def leer_sensor_de_temperatura():
    temp_amb = interrogar_sensor_dht()[0]
    if (temp_amb is not None):
        muestra_temp_amb.config(text = str(temp_amb) + "°C")
        
    return temp_amb

def leer_sensor_de_humedad():
    hume_amb = interrogar_sensor_dht()[1]
    if (hume_amb is not None):
        muestra_humedad_amb.config(text = str(hume_amb) + "%")

    return hume_amb

# Registra en el archivo txt los valores de temperatura y humedad 
def log_temp_y_hum():
    global ultima_humedad_medida
    global ultima_temperatura_medida
    if PRODUCCION:
        logging.info("Temperatura: %s°C; Humedad: %s%s" %(ultima_temperatura_medida, ultima_humedad_medida, "%"))
    else:
        print("Temperatura: %s°C; Humedad: %s%s" %(ultima_temperatura_medida, ultima_humedad_medida, "%"))

    ventana.after(INTERVALO_REGISTRO_LOG, log_temp_y_hum)
    
def enviar_correo():
    for destinatario in DESTINATARIOS:
        remitente = REMITENTE
        destinatario = destinatario
        mensaje = "¡Prueba 4 python Dario!"
        email = EmailMessage()
        email["From"] = remitente
        email["To"] = destinatario
        email["Subject"] = "Correo de prueba"
        email.set_content(mensaje)
        smtp = smtplib.SMTP_SSL("smtp.gmail.com")
        smtp.login(remitente, "xavnmqrxqzicoexf")
        smtp.sendmail(remitente, destinatario, email.as_string())
        smtp.quit()

def set_umbral_alarma():
    global temp_umbral
    temp_umbral = int(nueva_temp_umbral.get())

def reset_alarma():
    global flag_alarma_temp
    flag_alarma_temp = False

def alarma_por_temperatura():
    global flag_alarma_temp
    if (ultima_temperatura_medida > temp_umbral and not flag_alarma_temp):
        flag_alarma_temp = True
        muestra_alarma.config(text = "ALARMA TEMPERATURA")
        enviar_correo()
    
    ventana.after(TIEMPO_REFRESCO_LECTURA_TEMPERATURA, alarma_por_temperatura)
#************************************************************************************************************************
#****                                          FIN DEFINICION FUNCIONES                                              ****
#************************************************************************************************************************



boton_temp = Button(ventana, text ="Confirmar", command = actualizar_temp_seleccionada, activebackground = 'yellow', width = 10 )      #define el botón para confirmar la temp seleccionada
boton_temp.grid(row=10,column=COL_TEMP, padx=10, pady=10)                                                                 #define la posición del botón

boton_humedad = Button(ventana, text ="Confirmar", command = actualizar_humedad_seleccionada, activebackground = 'yellow', width = 10 )    #defie el botón para confirmar la humedad seleccionada
boton_humedad.grid(row=10,column=COL_HUM, padx=10, pady=10)                                                                          #define la posición del botón

boton_log = Button(ventana, text ="Consultar LOG", command = abrir_archivo_logs, activebackground = 'yellow', width = 10 )    #defie el botón para confirmar la humedad seleccionada
boton_log.grid(row=10,column=COL_HUM+10, padx=10, pady=10)

boton_set_temp_alarma = Button(ventana, text ="UMBRAL ALARMA", command = set_umbral_alarma, activebackground = 'yellow', width = 10 )    #defie el botón para confirmar la temperatura umbral para disparar la alaram
boton_set_temp_alarma.grid(row=10,column=COL_HUM+10+10, padx=10, pady=10)

boton_reset_alarma = Button(ventana, text ="RESET ALARMA", command = reset_alarma, activebackground = 'yellow', width = 10 )    #resetea la alaram
boton_reset_alarma.grid(row=10,column=COL_HUM+10+10+10, padx=10, pady=10)

ventana.after(TIEMPO_REFRESCO_LECTURA_TEMPERATURA, control_termico)
ventana.after(TIEMPO_REFRESCO_LECTURA_HUMEDAD, control_humedad)
ventana.after(TIEMPO_REFRESCO_LECTURA_TEMPERATURA, alarma_por_temperatura)
ventana.after(INTERVALO_REGISTRO_LOG, log_temp_y_hum)
  
ventana.mainloop() 
