from tkinter import *
  
ventana = Tk()   
ventana.geometry("400x300")  
v2 = DoubleVar() 
  
def show2(): 
      
    sel = "Vertical Scale Value = " + str(v2.get())  
    l2.config(text = sel, font =("Courier", 14)) 
  
s2 = Scale( ventana, variable = v2, 
           from_ = 100, to = 1, 
           orient = VERTICAL)  
  
l4 = Label(ventana, text = "Vertical Scaler") 
  
b2 = Button(ventana, text ="Display Vertical", 
            command = show2, 
            bg = "purple",  
            fg = "white") 
  
l2 = Label(ventana) 
  
s2.pack(anchor = CENTER)  
l4.pack() 
b2.pack() 
l2.pack() 
  
ventana.mainloop() 