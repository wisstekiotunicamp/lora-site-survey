import serial
import math
import time
import struct
from time import localtime, strftime
import schedule
import time
from tkinter import *
import tkinter.scrolledtext as ScrolledText

#from ScrolledText import ScrolledText
import threading
import matplotlib.pyplot as plt
#import ttk


#from Tkinter import *
#from ttk import *
import tkinter.ttk as ttk
#from tkFileDialog import asksaveasfilename
import tkinter.filedialog
#import tkMessageBox
import tkinter.messagebox as tkMessageBox
#from ScrolledText import ScrolledText

import matplotlib
matplotlib.use('TkAgg')

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from matplotlib.figure import Figure

from math import pow

import serial  # pyserial
import numpy as np
import serial.tools.list_ports
import pandas as pd



#import serial
import math
import time
#import struct
from time import localtime, strftime
import schedule
import time
#from Tkinter import *
#import tkMessageBox
#from ScrolledText import ScrolledText
import threading
import matplotlib.pyplot as plt
#import ttk
#from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg,    NavigationToolbar2TkAgg
from matplotlib.figure import Figure
from matplotlib import style
from tkinter.filedialog import asksaveasfilename
from datetime import datetime




style.use("ggplot")

 #funcao que gera os graficos usando a matplotlib

def grafico(f, c):
    global s1

    f.clear()

    valores_rssi = []
    media_rssi = []

    try:
        # -------- Lê os dados das medidas de RSSI de Upilink --------
        with open("medidas_rssi.txt", 'r') as dados:
            for line in dados:
                line = line.strip()
                if line != "":
                    try:
                        valores_rssi.append(float(line.split(';')[0]))
                    except:
                        pass

        # -------- Lê os cálculos das medidas das Médias de RSSI --------
        with open("media_rssi.txt", 'r') as medias:
            for line in medias:
                line = line.strip()
                if line != "":
                    try:
                        media_rssi.append(float(line))
                    except:
                        pass

        # -------- CRIA O GRÁFICO --------
        axis = f.add_subplot(111)

        # Plota os dados de RSSI
        axis.plot(valores_rssi, label='RSSI', color='green')

        # Plota a Média Móvel RSSI
        axis.plot(media_rssi, label='MÉDIA RSSI', color='orange')

        axis.legend()
        axis.set_ylabel('RSSI (dBm)')
        axis.set_xlabel('Número de Medidas')

        f.subplots_adjust(left=0.12, bottom=0.09, right=0.98, top=0.95)

        c.draw()

        # Atualiza a cada 1 segundo
        raiz.after(1000, grafico, f, c)

    except Exception as e:
        print("Erro:", e)
        raiz.after(1000, grafico, f, c)

def callback():
    if tkMessageBox.askokcancel("Sair", "Tem certeza que deseja sair?"):
        raiz.destroy()




def salvar(ff):
        ftypes = [('.png (PNG)', '*.png')]
        f = asksaveasfilename(filetypes=ftypes, defaultextension=".png")

        print(f)

        if f != '':
            ff.savefig(f)



#####----------------------------------------CRIAÇAO DA JENLA PRINCIPAL E FRAMES---------------------


raiz=Tk() #criando a tela principal , usando um objeto TKinter
raiz.title("MEDIDAS DE SIMULAÇÃO RSSI (Radio Signal Strengh Indicator)") #funcao para alterar titulo da janela
raiz.geometry('1000x600') #define o tamanho da janela
raiz.resizable(0, 0) #deixa o tamanho da janela fixo, sem opções de redimensionamento

#frame_cima = Frame(master=raiz,borderwidth=1, relief='sunken') #cria um frame no topo da janela, define como master a janela principal(raiz)
#frame_meio = Frame(master=raiz,borderwidth=1, relief='sunken') #cria um frame no meio da janela, define como master a janela principal(raiz) 
frame_baixo = Frame(master=raiz,borderwidth=1, relief='sunken') #cria um frame no rodapé da janela, define como master a janela principal(raiz)

#frame_cima.place(x=10,y=10,width=980,height=100) #posiciona e define o tamanho dos frames
#frame_meio.place(x=10,y=120,width=980,height=210) #posiciona e define o tamanho dos frames
frame_baixo.place(x=10,y=10,width=980,height=580) #posiciona e define o tamanho dos frames

####----------------------------------------------CONEXAO----------------------------------------

'''label_dados=Label(master=frame_cima, font=("Arial", 14, "bold"),text = "Conexão") #define um label (texto estático)
label_dados.place(x=450,y=1) #posiciona o label usando "place"

btn_teste=Button(frame_cima,text="Conectar",command=testar, width=8) #define um botão
btn_teste.place(x=20,y=25) #posiciona o botão usando "place"



#p = StringVar()
portas = ttk.Combobox(frame_cima,width=15)
portas.place(x=130,y=25)
portas['values']= verificar_portas()


btn_atual=Button(frame_cima,text="Atualizar Portas",command=atualizar_portas, width=14)
btn_atual.place(x=132,y=60)

conteudo_tx= tkinter.scrolledtext.ScrolledText(frame_cima,width=35,height=3,padx=5,pady=5)
conteudo_tx.config(state="disabled")
conteudo_tx.place(x=320, y= 30)

conteudo_rx= tkinter.scrolledtext.ScrolledText(frame_cima,width=35,height=3,padx=5,pady=5)
conteudo_rx.config(state="disabled")
conteudo_rx.place(x=660, y= 30)'''



####----------------------------------------------Teoria--------------------------------

'''label_teoria=Label(frame_meio, font=("Arial", 14, "bold"),text = "Teoria",padx=5,pady=5)
label_teoria.place(x=460, y=1)

l_distancia = Label(frame_meio, text = "Distância (metros)")
l_distancia.place(x=20,y=20)
dist=0
distancia = Entry(frame_meio,width=11)
distancia.place(x=130,y=20)

l_freq = Label(frame_meio, text = "Frequência (mHz)")
l_freq.place(x=20,y=60)
freq=0
freq = ttk.Combobox(frame_meio,width=8)
freq.place(x=130,y=60)
freq['values']=[915, 2400]
freq.current(0)

minha_imagem = PhotoImage(file="el.png")
img = minha_imagem

canvas1 = Canvas(frame_meio)
canvas1.configure(height='100')
canvas1.configure(width='350')
canvas1.place(x=10,y=100)
canvas1.create_image(10,10,image=img,anchor=NW)

btn_calcula=Button(frame_meio,text="Calcular", width=8,command=calc_atenuacao)
btn_calcula.place(x=220,y=35)
btn_calcula.config(state="disabled")

btn_video=Button(frame_meio,text="Vídeo", width=8,command=video)
btn_video.place(x=370,y=135)

conteudo= tkinter.scrolledtext.ScrolledText(frame_meio,width=62,height=7,padx=5,pady=5)
conteudo.config(state="disabled")
conteudo.place(x=450, y= 60)
'''


####----------------------------------------------Experimento------------------------------------

fig = Figure(figsize=(9.8, 5), facecolor='white')
b=Button(frame_baixo, text='Salvar Gráfico', command=lambda:salvar(fig))
b.place(x=460,y=530)
canvas = FigureCanvasTkAgg(fig, master=frame_baixo)
canvas.get_tk_widget().grid(row=3, column=1, columnspan=3, sticky='NSEW')
grafico(fig,canvas)       
#btn_grafico=Button(frame_baixo,text="Gráfico",width=8,command=lambda:grafico(fig,canvas))
#btn_grafico.place(x=650,y=433)
#btn_grafico.config(state="disabled")



###---------------------- CÓDIGO PARA RODAR A APLICAÇÃO

raiz.protocol("WM_DELETE_WINDOW", callback)
raiz.mainloop()









