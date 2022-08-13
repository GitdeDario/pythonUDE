#**************************************************
#*** PONER EN True CUANDO SE PASE A PRODUCCIÓN ***
#**************************************************
PRODUCCION = True    

if(PRODUCCION):
    import RPi.GPIO as GPIO		        # para el control de los GPIO de la raspberry
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)            # lo uso en el modo BOARD
    CALEFACTOR = 11                      # El led que representa el calefactor va en el pin 3 (*****CAMBIAR SI ES NECESARIO******)
    GPIO.setup(CALEFACTOR, GPIO.OUT)    # Se setea el pin correspondiente como salida ya que va a controlar un actuador
    GPIO.output(CALEFACTOR, False)      # El calefactor inicia apagado cuando arranca el sistema
    VENTILADOR = 12                      # El led que representa el ventilador va en el pin 4 (*****CAMBIAR SI ES NECESARIO******)
    GPIO.setup(VENTILADOR, GPIO.OUT)    # Se setea el pin correspondiente como salida ya que va a controlar un actuador
    GPIO.output(VENTILADOR, False)      # El ventilador inicia apagado cuando arranca el sistema
    HUMIDIFICADOR = 13                      # El led que representa el calefactor va en el pin 3 (*****CAMBIAR SI ES NECESARIO******)
    GPIO.setup(HUMIDIFICADOR, GPIO.OUT)    # Se setea el pin correspondiente como salida ya que va a controlar un actuador
    GPIO.output(HUMIDIFICADOR, False)      # El calefactor inicia apagado cuando arranca el sistema
    DESHUMIDIFICADOR = 16                      # El led que representa el ventilador va en el pin 4 (*****CAMBIAR SI ES NECESARIO******)
    GPIO.setup(DESHUMIDIFICADOR, GPIO.OUT)    # Se setea el pin correspondiente como salida ya que va a controlar un actuador
    GPIO.output(DESHUMIDIFICADOR, False)      # El ventilador inicia apagado cuando arranca el sistema
    
DATOS_DHT = 21                  # pin de lectura de Dht11    
import Adafruit_DHT as dht          # librería para el sensor de presión y temperatura
sensor_DHT = dht.DHT11              # crea objeto llamado sensor_DHT

from tkinter import *               # librería para entorno gráfico 
ventana = Tk()                      # Definiciones de la librería tkinter
ventana.title("CONTROL DOMÓTICA")   # Título de la ventana
#ventana.iconbitmap("sate.ico")     # Ícono de la ventana
ventana.geometry("400x300")         # Define tamaño de pantalla
v1 = DoubleVar()
v2 = DoubleVar()                    # variable para el slider (tkinter)


# Esta función se ejecuta cuando se presiona el botón confirmar asociado al slider temperatura.
# Hace que se accionen los controladores térmicos en base a la temperatura ambiente(sensor) y lo 
# seleccionado por el usuario(slider)
def control_termico():       
    temperatura_seleccionada = v2.get() 
    leer_sensor_de_temperatura()
    if(temperatura_seleccionada > temperatura_ambiente):
        encender_calefactor() 
    elif(temperatura_seleccionada == temperatura_ambiente):
        apaga_calefactor_y_ventilador()
    else:
        encender_ventilacion()

def encender_calefactor():
    #enciende calefactor y apaga ventilación
    if(PRODUCCION):
        GPIO.output(CALEFACTOR, True)
        GPIO.output(VENTILADOR, False)
    else:
        print("\ncalefactor encendido\nventilación apagada \n\n") #esto solo se imprime en test
        
    
def encender_ventilacion():
    #enciende ventilación y apaga calefactor
    if(PRODUCCION):
        GPIO.output(CALEFACTOR, False)
        GPIO.output(VENTILADOR, True)
    else:
        print("\ncalefactor apagado\nventilación encendida \n\n")
        
def apaga_calefactor_y_ventilador():
    #apaga ventilación y apaga calefactor
    if(PRODUCCION):
        GPIO.output(VENTILADOR, False)
        GPIO.output(CALEFACTOR, False)
    else:
        print("\ncalefactor apagado\nventilación apagada \n\n")
        

# Esta función se ejecuta cuando se presiona el botón confirmar asociado al slider humedad.
# Hace que se accionen los controladores humificadores  en base a la humedad ambiente(sensor) y lo 
# seleccionado por el usuario(slider)

def control_humedad():       
    humedad_seleccionada = v1.get() 
    leer_sensor_de_humedad()
    if(humedad_seleccionada > humedad_ambiente):
        encender_humidificador()
    elif(humedad_seleccionada == humedad_ambiente):
        apaga_humidificador_y_deshumidificador()
    else:
        encender_deshumidificador()

def encender_humidificador():
    # enciende humificador y apaga desumificador
    if(PRODUCCION):
        GPIO.output(HUMIDIFICADOR, True)
        GPIO.output(DESHUMIDIFICADOR, False)
    else:
        print("\nhumificador encendido\ndesumidificador apagada \n\n") #esto solo se imprime en test
        
def encender_deshumidificador():
    # enciende desumificador y apaga humificador
    if(PRODUCCION):
        GPIO.output(HUMIDIFICADOR, False)
        GPIO.output(DESHUMIDIFICADOR, True)
    else:
        print("Deshumidificador encendido")

def apaga_humidificador_y_deshumidificador():
    # apaga desumificador y humificador
    if(PRODUCCION):
        GPIO.output(DESHUMIDIFICADOR, False)
        GPIO.output(HUMIDIFICADOR, False)
    else:
        print("Humidificador y humidificador apagado")


def interrogar_sensor_dht():                                            # funcion indica la temperatura, cada 5 segundos actualiza el valor
    #threading.Timer(5, interrogar_sensor_dht).start()                   # ejecuta la funcion interrogar_sensor_dht despues de 5s
    humidity, temperature = dht.read_retry(dht.DHT11, DATOS_DHT)    # se lee el valor de humeadad y temperatura
   
    if humidity is not None and temperature is not None:
        #print('Temp={0:0.1f}*C  Hum={1:0.1f}%'.format(temperature,humidity))
        #l_display.config(text = (temperature , humidity))
        print("Temperature(°C):" ,temperature)
        print("Humidity    (%):",humidity)
        
    else:
        print('Failed to get reading. Try again!')
        

    return temperature, humidity
#l_t = Tk.lablel(frame, text="Temp *C Hume %", font=("Arial",10))
#l_t.grid(row = 2, column = 3, padx = 10, pady = 10, sticky = "nsew")
#l_display = tk.lablel(frame, font=("Arial",20), fg = "red")
#l_display.grid(row = 3, column = 3, padx = 10, pady = 10, sticky = "nsew")

#def leer_sensor_de_temperatura():
#    temp_amb = interrogar_sensor_dht()[0]                        # LO QUE LEE EL SENSOR
#    return temp_amb                                              #
#temperatura_ambiente = leer_sensor_de_temperatura()              #Esta es la temperatura que nos da el sensor de temperatura

etiqueta_temp = Label(ventana, text = "Selector Temperatura °C")   #define la etiqueta "Temperatura"
etiqueta_temp.grid(row=8,column=4, padx=10, pady=10)             #define la posición de la etiqueta

ctrl_temp = Scale(ventana, variable = v2, from_ = 50, to = 0, orient = VERTICAL, activebackground='green2', bd=5,)  #Define el slider de control de temp
ctrl_temp.grid(row=9,column=4, padx=10, pady=10)                                                                  #define su posición
  
boton_temp = Button(ventana, text ="Confirmar", command = control_termico,activebackground='yellow', width= 10 )      #defie el botón para confirmar la temp seleccionada
boton_temp.grid(row=10,column=4, padx=10, pady=2)                                                                 #define la posición del botón


def leer_sensor_de_humedad():
    hume_amb = interrogar_sensor_dht()[1]                                                                    # LO QUE LEE EL SENSOR
    return hume_amb
humedad_ambiente = leer_sensor_de_humedad()                                  #Esta es la humedad que nos da el sensor de temperatura

etiqueta_humedad = Label(ventana, text = "Selector Humedad %")                             #define la etiqueta "Humidity Selector"
etiqueta_humedad.grid(row=8,column=2, padx=10, pady=10)                  #define la posición de la etiqueta

ctrl_humedad = Scale(ventana, variable = v1, from_ = 100 , to = 0, orient = VERTICAL, activebackground='green2', bd=5,)  #Define el slider de control de humedad
ctrl_humedad.grid(row=9,column=2, padx=10, pady=10)                                                   #define su posición
  
boton_humedad = Button(ventana, text ="Confirmar", command = control_humedad, activebackground='yellow', width= 10 )    #defie el botón para confirmar la humedad seleccionada
boton_humedad.grid(row=10,column=2, padx=10, pady=10)                                                                          #define la posición del botón

#******************************************************************#
#******              COMPLETAR ESTA FUNCION                  ******#
#******************************************************************#
#función que lee lo que da el sensor de temperatura
def leer_sensor_de_temperatura():
    temp_amb = 25 #ACA PONER LO QUE LEE EL SENSOR!!!!!!!!!!!!!!!!!!!!!!!!
    return temp_amb
temperatura_ambiente = leer_sensor_de_temperatura() #Esta es la temperatura que nos da el sensor de temperatura

#etiqueta_temp = Label(ventana, text = "Temperatura")   #define la etiqueta "Temperatura"
#etiqueta_temp.place(x=315, y=20)                    #define la posición de la etiqueta

#ctrl_temp = Scale(ventana, variable = v2, from_ = 35, to = 1, orient = VERTICAL)  #Define el slider de control de temp
#ctrl_temp.place(x=320, y=50)                                                    #define su posición
  
#boton_temp = Button(ventana, text ="Confirmar", command = control_termico, bg = "purple", fg = "white")    #defie el botón para confirmar la temp seleccionada
#boton_temp.place(x=315,y=190)                                                                           #define la posición del botón
  
  
ventana.mainloop() 