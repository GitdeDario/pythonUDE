#**************************************************
#*** PONER EN True CUANDO SE PASE A PRODUCCIÓN ***
#**************************************************
PRODUCCION = False    

import RPi.GPIO as GPIO # para el control de los GPIO de la raspberry
import Adafruit_DHT     # librería para el sensor de presión y temperatura
from tkinter import *   # librería para entorno gráfico
import logging          # para generar los log en un archivo txt    

# CONSTANTES
TEMP_MIN = 10       # Temperatura mínima que se puede elegir
TEMP_MAX = 30       # Temperatura máxima que se puede elegir
HUMEDAD_MAX = 100   # Humedad máxima seteable
HUMEDAD_MIN = 30    # Humedad mínima seteable
COL_TEMP = 30       # Para el control de posición de la columna de los controles de temperatura
COL_HUM = 2         # Ídem para los controles de humedad
TIEMPO_REFRESCO_LECTURA_HUMEDAD = 10000     # En milisegundos!!
TIEMPO_REFRESCO_LECTURA_TEMPERATURA = 10000 # En milisegundos!!
INTERVALO_REGISTRO_LOG = 60000              # En milisegundos!! (cada un minuto)

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
#ventana.iconbitmap('sate.ico')         # Ícono de la ventana
#ventana.geometry("600x400")            # Define tamaño de pantalla
ventana.attributes("-fullscreen", True) # Ventana fullscreen
humedad_var = DoubleVar()               # variables para el slider (tkinter)
temp_var = DoubleVar()                    

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

# tkinter - slider/selector de humedad
etiqueta_humedad = Label(ventana, text = "Selector Humedad %")                             #define la etiqueta "Humidity Selector"
etiqueta_humedad.grid(row=8,column=COL_HUM, padx=10, pady=10)                  #define la posición de la etiqueta
ctrl_humedad = Scale(ventana, variable = humedad_var, from_ = HUMEDAD_MAX , to = HUMEDAD_MIN, orient = VERTICAL, activebackground='green2', bd=5,)  #Define el slider de control de humedad
ctrl_humedad.grid(row=9,column=COL_HUM, padx=10, pady=10)                                                   #define su posición
  
logging.basicConfig(filename="logTemperatura_Humedad.txt", level=logging.INFO, format="%(asctime)s - %(message)" , datefmt="%d-%m-%Y %H:%M:%S")
logging.debug("Inicio del programa.-")
logging.debug("-----------------------------------------------------------")
#************************************************************************************************************************
#****                                                        FUNCIONES                                               ****
#************************************************************************************************************************

# Esta función se ejecuta cuando se presiona el botón confirmar asociado al slider temperatura.
# Hace que se accionen los controladores térmicos en base a la temperatura ambiente(sensor) y lo 
# seleccionado por el usuario (slider)
ultima_temperatura_medida = 25
def control_termico():
    global ultima_temperatura_medida
    temperatura_seleccionada = temp_var.get() 
    temperatura_ambiente = leer_sensor_de_temperatura()
    
    if(temperatura_ambiente is not None):                   # Esto se necesita porque el sensor no lee cada vez que se lo interroga. Cuando no lee, responde None
        ultima_temperatura_medida = temperatura_ambiente    # y eso da problemas al intentar imprimir en la pantalla de tkinter. Para solucionarlo se mantiene guardad
                                                            # el ultimo valor bueno medido
    if(temperatura_seleccionada > ultima_temperatura_medida):
        encender_calefactor() 
    elif(temperatura_seleccionada == ultima_temperatura_medida):
        apaga_calefactor_y_ventilador()
    else:
        encender_ventilacion()

# Enciende calefactor y apaga ventilador
def encender_calefactor():
    if(PRODUCCION):
        GPIO.output(CALEFACTOR, True)
        GPIO.output(VENTILADOR, False)
    else:
        print("\ncalefactor encendido\nventilación apagada \n\n") #esto solo se imprime en test
        
# Enciende ventilador y apaga calefactor    
def encender_ventilacion():
    if(PRODUCCION):
        GPIO.output(CALEFACTOR, False)
        GPIO.output(VENTILADOR, True)
    else:
        print("\ncalefactor apagado\nventilación encendida \n\n") #esto solo se imprime en test

#apaga ventilación y apaga calefactor  
def apaga_calefactor_y_ventilador():
    if(PRODUCCION):
        GPIO.output(VENTILADOR, False)
        GPIO.output(CALEFACTOR, False)
    else:
        print("\ncalefactor apagado\nventilación apagada \n\n") #esto solo se imprime en test
        

# Esta función se ejecuta cuando se presiona el botón confirmar asociado al slider humedad.
# Hace que se accionen los controladores humificadores  en base a la humedad ambiente (sensor) y lo 
# seleccionado por el usuario (slider)        
ultima_humedad_medida = 65
def control_humedad():
    global ultima_humedad_medida
    humedad_seleccionada = humedad_var.get() 
    humedad_ambiente = leer_sensor_de_humedad()
    
    if(humedad_ambiente is not None):               # Esto se necesita porque el sensor no lee cada vez que se lo interroga. Cuando no lee, responde None
        ultima_humedad_medida = humedad_ambiente    # y eso da problemas al intentar imprimir en la pantalla de tkinter. Para solucionarlo se mantiene guardad
                                                    # el ultimo valor bueno medido
        
    if(humedad_seleccionada > ultima_humedad_medida):
        encender_humidificador() 
    elif(humedad_seleccionada == ultima_humedad_medida):
        apaga_humidificador_y_deshumidificador()
    else:
        encender_deshumidificador()

#Enciende humidificador y apaga deshumidificador
def encender_humidificador():
    if(PRODUCCION):
        GPIO.output(HUMIDIFICADOR, True)
        GPIO.output(DESHUMIDIFICADOR, False)
    else:
        print("\nhumificador encendido\ndesumidificador apagada \n\n") #esto solo se imprime en test

# Enciende deshumidificador y a paga humidificador       
def encender_deshumidificador():
    if(PRODUCCION):
        GPIO.output(HUMIDIFICADOR, False)
        GPIO.output(DESHUMIDIFICADOR, True)
    else:
        print("Deshumidificador encendido y humidificador apagado") #esto solo se imprime en test

# Apaga humidificador y deshumidificador
def apaga_humidificador_y_deshumidificador():
    if(PRODUCCION):
        GPIO.output(DESHUMIDIFICADOR, False)
        GPIO.output(HUMIDIFICADOR, False)
    else:
        print("Humidificador y deshumidificador apagado") #esto solo se imprime en test


def interrogar_sensor_dht():                                   
    temperatura, humedad = Adafruit_DHT.read(SENSOR,PIN_SENSOR)
    
    return humedad, temperatura

def leer_sensor_de_temperatura():
    temp_amb = interrogar_sensor_dht()[0]
    if (temp_amb is not None):
        muestra_temp_amb.config(text = str(temp_amb) + "°C")
    ventana.after(TIEMPO_REFRESCO_LECTURA_TEMPERATURA, leer_sensor_de_temperatura)
    return temp_amb

def leer_sensor_de_humedad():
    hume_amb = interrogar_sensor_dht()[1]
    if (hume_amb is not None):
        muestra_humedad_amb.config(text = str(hume_amb) + "%")
    ventana.after(TIEMPO_REFRESCO_LECTURA_HUMEDAD, leer_sensor_de_humedad)
    return hume_amb

# Registra en el archivo txt los valores de temperatura y humedad 
def log_temp_y_hum():
    global ultima_humedad_medida
    global ultima_temperatura_medida
    logging.debug("Temperatura : %s°C, Humedad: %s%"  %(ultima_temperatura_medida, ultima_humedad_medida))

    ventana.after(INTERVALO_REGISTRO_LOG, log_temp_y_hum)
    

#************************************************************************************************************************
#****                                          FIN DEFINICION FUNCIONES                                              ****
#************************************************************************************************************************



boton_temp = Button(ventana, text ="Confirmar", command = control_termico, activebackground = 'yellow', width = 10 )      #define el botón para confirmar la temp seleccionada
boton_temp.grid(row=10,column=COL_TEMP, padx=10, pady=10)                                                                 #define la posición del botón

boton_humedad = Button(ventana, text ="Confirmar", command = control_humedad, activebackground = 'yellow', width = 10 )    #defie el botón para confirmar la humedad seleccionada
boton_humedad.grid(row=10,column=COL_HUM, padx=10, pady=10)                                                                          #define la posición del botón

leer_sensor_de_temperatura()    # Para que ponga en pantalla la temperatura apenas arranca el programa, después se va refrescando cada 10s....o cuando el sensor quiere
leer_sensor_de_humedad()        # Para que ponga en pantalla la humedad apenas arranca el programa, después se va refrescando cada 10s....o cuando el sensor quiere
ventana.after(TIEMPO_REFRESCO_LECTURA_TEMPERATURA, leer_sensor_de_temperatura)
ventana.after(TIEMPO_REFRESCO_LECTURA_HUMEDAD, leer_sensor_de_humedad)
ventana.after(INTERVALO_REGISTRO_LOG, log_temp_y_hum)
  
ventana.mainloop() 