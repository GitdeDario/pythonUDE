debug = True
   
import RPi.GPIO as GPIO             #para el control de los GPIO de la raspberry
import RPi.GPIO as GPIO
import tkinter as tk
import threading
import Adafruit_DHT as dht
#import pyfiglet
 

#font = pyfiglet.figlet_format('Control Domotica') # cartel de inicio
#print(font)

pin = 21 # pin de lectura de Dht11
sensor = dht.DHT11 # creo objeto llamado sensor


GPIO.setwarnings(False) # quita mensajes RuntimeWarning: This channel is already in use, continuing anyway.

GPIO.setmode(GPIO.BCM)             #lo uso en el modo BCM                                  
GPIO.setup(6,GPIO.OUT)            #led humificador  LED AMARILLO
GPIO.setup(6,GPIO.LOW)
HUMIFICADOR = 6
GPIO.setup(5,GPIO.OUT)            # led desumificador LED BLANCO
GPIO.setup(5,GPIO.LOW)
DESUMIFICADOR = 5   

GPIO.setmode(GPIO.BCM)             #lo uso en el modo BCM                                  
GPIO.setup(22,GPIO.OUT)            #led calefactor  LED ROJO
GPIO.setup(22,GPIO.LOW)
CALEFACTOR = 22
GPIO.setup(13,GPIO.OUT)            # led ventilador LED AZUL
GPIO.setup(13,GPIO.LOW)
VENTILADOR = 13 


from tkinter import *           #librería para entorno gráfico
root = Tk()                     #Definiciones de la librería tkinter

root.wm_title("CONTROL DOMOTICO")        
v2 = DoubleVar()                #variable para el slider temperatura
frame = Frame(root)
frame.pack()  # Empaqueta el frame en la raiz
frame.config(bg="navajo white")
root.config(bd=10, bg="navajo white")
root.geometry("500x400")
v1 = DoubleVar()               #variable para slider humedad


#Esta función se ejecuta cuando se presiona el botón confirmar asociado al slider temperatura.
#Hace que se accionen los controladores térmicos en base a la temperatura ambiente(sensor) y lo 
#seleccionado por el usuario(slider)

def control_termico():       
    temperatura_seleccionada = v2.get() 
    leer_sensor_de_temperatura()
    if(temperatura_seleccionada > temperatura_ambiente):
        encender_calefactor()
        GPIO.output(22, 1)
    elif(temperatura_seleccionada == temperatura_ambiente):
        apago_control_termico()
    else:
        encender_ventilacion()
        
#Esta función se ejecuta cuando se presiona el botón confirmar asociado al slider humedad.
#Hace que se accionen los controladores humificadores  en base a la humedad ambiente(sensor) y lo 
#seleccionado por el usuario(slider)

def control_humedad():       
    humedad_seleccionada = v1.get() 
    leer_sensor_de_humedad()
    if(humedad_seleccionada > humedad_ambiente):
        encender_humificador()
        GPIO.output(6, 1)
    elif(humedad_seleccionada == humedad_ambiente):
        apago_control_humificador()
    else:
        encender_desumificador()


def encender_calefactor():
    #enciende calefactor y apaga ventilación
    if(debug):
        GPIO.output(CALEFACTOR, True)
        GPIO.output(VENTILADOR, False)
    else:
        print("\ncalefactor encendido\nventilación apagada \n\n") #esto solo se imprime en test
        
def encender_humificador():
    #enciende humificador y apaga desumificador
    if(debug):
        GPIO.output(HUMIFICADOR, True)
        GPIO.output(DESUMIFICADOR, False)
    else:
        print("\nhumificador encendido\ndesumificador apagada \n\n") #esto solo se imprime en test
        
    
def encender_ventilacion():
    #enciende ventilación y apaga calefactor
    if(debug):
        GPIO.output(CALEFACTOR, False)
        GPIO.output(VENTILADOR, True)
    else:
        print("Ventilador encendido")

def encender_desumificador():
    #enciende desumificador y apaga humificador
    if(debug):
        GPIO.output(HUMIFICADOR, False)
        GPIO.output(DESUMIFICADOR, True)
    else:
        print("Desumificador encendido")
        

def apago_control_termico():
    #enciende ventilador y apaga calentador
    if(debug):
        GPIO.output(VENTILADOR, False)
        GPIO.output(CALEFACTOR, False)
    else:
        print("Calentador encendido")

def apago_control_humificador():
    #enciende desumificador y apaga humificador
    if(debug):
        GPIO.output(DESUMIFICADOR, False)
        GPIO.output(HUMIFICADOR, False)
    else:
        print("Humificador encendido")
       
        
def get_data():                                            # funcion indica la temperatura, cada 5 segundos actualiza el valor

    threading.Timer(5, get_data).start()                   # ejecuta la funcion get_data despues de 5s

    humidity, temperature = dht.read_retry(sensor, pin)    # se lee el valor de humeadad y temperatura
   
    if humidity is not None and temperature is not None:
        #print('Temp={0:0.1f}*C  Hum={1:0.1f}%'.format(temperature,humidity))
        l_display.config(text = (temperature , humidity))
        print("Temperature(°C):" ,temperature)
        print("Humidity    (%):",humidity)
        
    else:
       print('Failed to get reading. Try again!')
        


    return temperature, humidity

l_t=tk.Label(frame, text="Temp *C  Hume %",font=("Arial",10))  # etiqueta del sensor
l_t.grid(row=2,column=3, padx=10, pady=10, sticky="nsew")

l_display=tk.Label(frame,font=("Arial",20),fg="red")  # display de la temperatura
l_display.grid(row=3,column=3, padx=10, pady=10, sticky="nsew")



#get_data()

def leer_sensor_de_temperatura():
    temp_amb = get_data()[0]                                                                  # LO QUE LEE EL SENSOR
    return temp_amb
temperatura_ambiente = leer_sensor_de_temperatura()                                  #Esta es la temperatura que nos da el sensor de temperatura

etiqueta_temp = Label(frame, text = "Temperature Selector °C")                             #define la etiqueta "Temperatura"
etiqueta_temp.grid(row=8,column=4, padx=10, pady=10)                  #define la posición de la etiqueta

ctrl_temp = Scale(frame, variable = v2, from_ = 50, to = 0, orient = VERTICAL, activebackground='green2', bd=5,)  #Define el slider de control de temp
ctrl_temp.grid(row=9,column=4, padx=10, pady=10)                                                   #define su posición
  
boton_temp = Button(frame, text ="Confirm", command = control_termico,activebackground='yellow', width= 10 )    #defie el botón para confirmar la temp seleccionada
boton_temp.grid(row=10,column=4, padx=10, pady=2)                                                                          #define la posición del botón


def leer_sensor_de_humedad():
    hume_amb = get_data()[1]                                                                    # LO QUE LEE EL SENSOR
    return hume_amb
humedad_ambiente = leer_sensor_de_humedad()                                  #Esta es la humedad que nos da el sensor de temperatura

etiqueta_temp1 = Label(frame, text = "Humidity Selector %")                             #define la etiqueta "Humidity Selector"
etiqueta_temp1.grid(row=8,column=2, padx=10, pady=10)                  #define la posición de la etiqueta

ctrl_temp1 = Scale(frame, variable = v1, from_ = 100 , to = 0, orient = VERTICAL, activebackground='green2', bd=5,)  #Define el slider de control de humedad
ctrl_temp1.grid(row=9,column=2, padx=10, pady=10)                                                   #define su posición
  
boton_temp1 = Button(frame, text ="Confirm", command = control_humedad,activebackground='yellow', width= 10 )    #defie el botón para confirmar la humedad seleccionada
boton_temp1.grid(row=10,column=2, padx=10, pady=10)                                                                          #define la posición del botón
 
root.mainloop()
