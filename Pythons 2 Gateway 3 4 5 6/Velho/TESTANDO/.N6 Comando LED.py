
from tkinter import *
import matplotlib
matplotlib.use('TkAgg')


# --------------------------- FUNÇÃO QUE PEGA OS VALORES NAS JANELAS DE TEXTO E GRAVA NO ARQUIVO
def gravar_valor():
    val1 = valor1.get() # variável valor que recebe o valor digitado em env
    # val2 = valor2.get()
    val3 = valor3.get() # variável valor que recebe o valor digitado em env
    # val4 = valor4.get()
    
    arquivo_txt = "comandos_oficina.txt" # está dando nome para o arquivo txt
    s = open (arquivo_txt,'w')
    s.write(val1+"\n")

    # s.write(val2+"\n")
    s.write("0\n")

    s.write(val3+"\n")

    # s.write(val4+"\n")
    s.write("0\n")

    s.close()

#----------------------------- CRIAÇAO DA JENLA PRINCIPAL ---------------------

raiz=Tk() #criando a tela principal , usando um objeto TKinter
raiz.title("MEDIDA DE LUMINOSIDADE") #funcao para alterar titulo da janela
raiz.geometry('1000x500') #define o tamanho da janela
raiz.resizable(0, 0) #deixa o tamanho da janela fixo, sem opções de redimensionamento

#----------------------------- CRIA janela EXIBIÇÃO -------------------
janela = Frame(master=raiz,borderwidth=1, relief='sunken') #cria um janela no rodapé da janela, define como master a janela principal(raiz)
janela.place(x=10,y=10,width=980,height=480) #posiciona e define o tamanho dos janelas

label_exp = Label(janela, font=("Arial", 14, "bold"),text = "ESTRUTURA LABORATÓRIO",padx=5,pady=5)
label_exp.place(x=530, y=1)


# CRIA BOTÃO PARA GRAVAS
botao4=Button(janela,text="GRAVAR COMANDOS",width=20,command= gravar_valor)
botao4.place(x=10,y=50)
botao4.config(state="normal")

# TEXTO AO LADO DAS ENTRADAS DE TEXTO
texto_valor1 = Label(janela, text = "LED Verde")
texto_valor1.place(x=20,y=120)

texto_valor2 = Label(janela, text = "Valor = 0 ---> LED demonstra TX   |  Valor = 1 ---> LED Aceso  ")
texto_valor2.place(x=20,y=150)

# texto_valor2 = Label(janela, text = "LED Amarelo")
# texto_valor2.place(x=20,y=180)

texto_valor3 = Label(janela, text = "LED Vermelho")
texto_valor3.place(x=20,y=240)

texto_valor2 = Label(janela, text = "Valor = 0 ---> LED demonstra RX   |  Valor = 1 ---> LED Aceso  ")
texto_valor2.place(x=20,y=270)

# texto_valor4 = Label(janela, text = "D")
# texto_valor4.place(x=20,y=300)



# inseri figura
# minha_imagem = PhotoImage(file="oficina21.png")
# img = minha_imagem
#
# canvas1 = Canvas(janela)
# canvas1.configure(height='500')
# canvas1.configure(width='800')
# canvas1.place(x=250,y=100)
# canvas1.create_image(10,10,image=img,anchor=NW)


# JANELAS DE ENTRA DOS VALORES
valor1=Entry(janela, width=10)
valor1.place(x=150,y=120)
valor1.insert(0, "0")

# valor2=Entry(janela, width=10)
# valor2.place(x=50,y=180)
# valor2.insert(0, "0")

valor3=Entry(janela, width=10)
valor3.place(x=150,y=240)
valor3.insert(0, "0")

# valor4=Entry(janela, width=10)
# valor4.place(x=50,y=300)
# valor4.insert(0, "0")
# inseri figura
minha_imagem = PhotoImage(file="Lab_IoT.png")
img = minha_imagem

canvas1 = Canvas(janela)
canvas1.configure(height='500')
canvas1.configure(width='800')
canvas1.place(x=260,y=60)
canvas1.create_image(10,10,image=img,anchor=NW)

###---------------------- CÓDIGO PARA RODAR A APLICAÇÃO
raiz.mainloop()









