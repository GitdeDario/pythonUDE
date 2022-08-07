from tkinter import *       #librería para entorno gráfico
  
root = Tk()                 #Definiciones de la librería tkinter
root.geometry("400x300")    #Define tamaño de pantalla 
v2 = DoubleVar()            #slider temperatura

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
    print("\ncalefactor encendido\nventilación apagada \n\n")
    #enciende calefactor y apaga ventilación
    #GPIO del calefactor = on
    #GPIO del ventilador = off

def encender_ventilacion():
    print("\ncalefactor apagado\nventilación encendida \n\n")
    #enciende ventilación y apaga calefactor
    #GPIO del calefactor = off
    #GPIO del ventilador = on

def apago_control_termico():
    print("\ncalefactor apagado\nventilación apagada \n\n")
    #enciende ventilación y apaga calefactor
    #GPIO del calefactor = off
    #GPIO del ventilador = off

#******************************************************************#
#******            COMPLETAR ESTA FUNCION                   ******#
#******************************************************************#
#función que lee lo que da el sensor de temperatura
def leer_sensor_de_temperatura():
    temp_amb = 25 #ACA PONER LO QUE LEE EL SENSOR!!!!!!!!!!!!!!!!!!!!!!!!
    return temp_amb
temperatura_ambiente = leer_sensor_de_temperatura() #Esta es la temperatura que nos da el sensor de temperatura

s2 = Scale(root, variable = v2, from_ = 100, to = 1, orient = VERTICAL)  
  
l4 = Label(root, text = "Temperatura") 
  
b2 = Button(root, text ="Confirmar", command = control_termico, bg = "purple", fg = "white") 
  
l2 = Label(root) 
  
s2.pack(anchor = CENTER)  
l4.pack() 
b2.pack() 
l2.pack() 
  
root.mainloop() 