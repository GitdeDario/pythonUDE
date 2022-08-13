#**************************************************
#*** PONER EN True CUANDO SE PASE A PRODUCCIÓN ***
#**************************************************
PRODUCCION = False    

if(PRODUCCION):
    import RPi.GPIO as GPIO		        #para el control de los GPIO de la raspberry
    GPIO.setmode(GPIO.BOARD)            #lo uso en el modo BOARD
    CALEFACTOR = 3                      #El led que representa el calefactor va en el pin 3 (*****CAMBIAR SI ES NECESARIO******)
    GPIO.setup(CALEFACTOR, GPIO.OUT)    #Se setea el pin correspondiente como salida ya que va a controlar un actuador
    GPIO.output(CALEFACTOR, False)      #El calefactor inicia apagado cuando arranca el sistema
    VENTILADOR = 4                      #El led que representa el ventilador va en el pin 4 (*****CAMBIAR SI ES NECESARIO******)
    GPIO.setup(VENTILADOR, GPIO.OUT)    #Se setea el pin correspondiente como salida ya que va a controlar un actuador
    GPIO.output(VENTILADOR, False)      #El ventilador inicia apagado cuando arranca el sistema

from tkinter import *           #librería para entorno gráfico 
root = Tk()                     #Definiciones de la librería tkinter
root.title("CONTROL DOMÓTICA")  #Título de la ventana
#root.iconbitmap("sate.ico")     #Ícono de la ventana
root.geometry("400x300")        #Define tamaño de pantalla 
v2 = DoubleVar()                #variable para el slider temperatura

#Esta función se ejecuta cuando se presiona el botón confirmar asociado al slider temperatura.
#Hace que se accionen los controladores térmicos en base a la temperatura ambiente(sensor) y lo 
#seleccionado por el usuario(slider)
def control_termico():       
    temperatura_seleccionada = v2.get() 
    leer_sensor_de_temperatura()
    if(temperatura_seleccionada > temperatura_ambiente):
        encender_calefactor() 
    elif(temperatura_seleccionada == temperatura_ambiente):
        apago_control_termico()
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
        

def apago_control_termico():
    #enciende ventilación y apaga calefactor
    if(PRODUCCION):
        GPIO.output(VENTILADOR, False)
        GPIO.output(CALEFACTOR, False)
    else:
        print("\ncalefactor apagado\nventilación apagada \n\n")
        

#******************************************************************#
#******              COMPLETAR ESTA FUNCION                  ******#
#******************************************************************#
#función que lee lo que da el sensor de temperatura
def leer_sensor_de_temperatura():
    temp_amb = 25 #ACA PONER LO QUE LEE EL SENSOR!!!!!!!!!!!!!!!!!!!!!!!!
    return temp_amb
temperatura_ambiente = leer_sensor_de_temperatura() #Esta es la temperatura que nos da el sensor de temperatura

etiqueta_temp = Label(root, text = "Temperatura")   #define la etiqueta "Temperatura"
etiqueta_temp.place(x=315, y=20)                    #define la posición de la etiqueta

ctrl_temp = Scale(root, variable = v2, from_ = 35, to = 1, orient = VERTICAL)  #Define el slider de control de temp
ctrl_temp.place(x=320, y=50)                                                    #define su posición
  
boton_temp = Button(root, text ="Confirmar", command = control_termico, bg = "purple", fg = "white")    #defie el botón para confirmar la temp seleccionada
boton_temp.place(x=315,y=190)                                                                           #define la posición del botón
  
  
root.mainloop() 