# N3 LoRa Site Survey - Versão 22/01/2026 - WissTek-IoT UNICAMP - Lucas Alachev
#
# ========= Bibliotecas =================================
import serial
import math
import time
import struct
from time import localtime, strftime
import os
import random

#========== Criação de Variáveis =========================
global rssi_DL, rssi_UL, contador_UL, contador_DL, ultimo_pacote_DL, ultimo_pacote_UL, air_quality_indicator 
 # definições de teste: configurações importantes para a bateria de testes extraídas do arquivo de parâmetros

numero_de_medidas = 0
rota = [] # neste momento é um enlace ponto a ponto, que futuramente poderá ser usada para roteamento
condicao_start = 0
ultima_condicao_start = 0

 # Camada Física
tamanho_do_pacote = 52 
rssi_DL = 0
rssi_UL = 0 
snr_DL = 0
snr_UL = 0

 # Camada MAC
tempo_entre_medidas = 1

 # Camada de Rede
ID_base = 0
ID_sensor = 1

 # Camada de Transporte
contador_DL = 0
ultimo_pacote_DL = 0
contador_UL = 0
ultimo_pacote_UL = 0

 # Camada de Aplicação
luminosidade = 0
air_quality_indicator = 0

 # Contabilização de PSR
psr_DL = 0
psr_UL = 0
psr_geral = 0 #Utilizada temporariamente, antes de implementar a 'separação' da PSR de Downlink e Uplink
perdas_DL = 0
perdas_UL = 0
perda_geral = 0

# Variáveis Auxiliares
medida_atual = 0 

#========== Criação de Pacotes
Pacote_UL = [0] * tamanho_do_pacote
Pacote_DL = [0] * tamanho_do_pacote

#========== Simulador de Canal ===========#
Pacote_Sim = [0] * tamanho_do_pacote
rssi_dl_sim = -52
rssi_ul_sim = -55
snr_dl_sim = 2
snr_ul_sim = 3
contador_ul_sim = 0
#========== Configuração da Porta Serial ==================

# para COM# o número que se coloca é n-1 no primeiro parâmetrso. Ex COM9  valor 8
#n_serial = input("Digite o número da porta COM = ") #seta a serial
#n_serial1 = int(n_serial) - 1
#ser = serial.Serial("COM"+str(n_serial), 115200, timeout=0.5,parity=serial.PARITY_NONE) # serial Windows
#print("Porta Serial Conectada:",n_serial)

'''Configuração Serial para Linux ''' # Importante para o uso em Raspberry PI, o hardware escolhido para realizar a função de borda

#n_serial1 = "/dev/ttyUSB0" # seta a serial for Linux - - Attention to the baud rate
#ser = serial.Serial(n_serial1, 115200, timeout=0.5,parity=serial.PARITY_NONE)

#========== Criação de Arquivos de Gerência ===============
# Este conjunto de linhas serve para deletar os arquivos temporários de armazenamento para observação de dados em tempo real

if os.path.exists(os.path.join(os.path.dirname(__file__), '../NIVEL4/dados_gerencia.tmp')): # Procura no Nível 4 se há um arquivo de gerência
   os.remove(os.path.join(os.path.dirname(__file__), '../NIVEL4/dados_gerencia.tmp')) # Se há um arquivo de gerência, ele é deletado

if os.path.exists(os.path.join(os.path.dirname(__file__), '../NIVEL4/dados_aplicacao.tmp')):# Procura no Nível 4 se há um arquivo de aplicação
   os.remove(os.path.join(os.path.dirname(__file__), '../NIVEL4/dados_aplicacao.tmp')) # Se há um arquivo de aplicação, ele é deletado

if os.path.exists(os.path.join(os.path.dirname(__file__), '../NIVEL4/PARAMETROS.txt')):# Procura no Nível 4 se há um arquivo de Parametros
   os.remove(os.path.join(os.path.dirname(__file__), '../NIVEL4/PARAMETROS.txt')) # Se há um arquivo de Parametros, ele é deletado
   
# Cria os arquivos temporários de Gerência, Aplicação e Parametros
arquivo_gerencia = os.path.join(os.path.dirname(__file__), '../NIVEL4/dados_gerencia.tmp')
arquivo_aplicacao = os.path.join(os.path.dirname(__file__), '../NIVEL4/dados_aplicacao.tmp')
arquivo_parametros = os.path.join(os.path.dirname(__file__), '../NIVEL4/PARAMETROS.txt')

Gerencia = open(arquivo_gerencia, 'a+') # Cria o arquivo novo de gerência, onde os dados de RSSI são escritos temporariamente
Gerencia.close()

Aplicacao = open(arquivo_aplicacao, 'a+') # Cria o arquivo novo de aplicação, onde os dados de luminosidade são escritos temporariamente
Aplicacao.close()

Parametros = open(arquivo_parametros, 'a+') # Cria o arquivo de parâmetros. 
#É necessário iniciar o arquivo com os dados para evitar erros na leitura.
Parametros.write("0\n")  # Linha 1: Condição de Start (0 = Parado). O \n é necessário para quebrar a linha
Parametros.write("0")   # Linha 2: Número de Medidas Padrão
Parametros.close()

# Criação do arquivo de LOG para armanezamento completo dos dados aquisitados
#Cria um arquivo de log para armazenar os pacotes brutos recebidos
arquivo_LOG_pacote = os.path.join(os.path.dirname(__file__), strftime("../NIVEL4/LOG_pacote_%Y_%m_%d_%H-%M-%S.txt")) # Cria o arquivo de LOG
#Cria um arquivo de log para armazenar os dados de gerência extraídos do pacote
arquivo_LOG_gerencia = os.path.join(os.path.dirname(__file__), strftime("../NIVEL4/LOG_gerencia_%Y_%m_%d_%H-%M-%S.txt")) # Cria o arquivo de LOG

print ("Arquivo de LOG de pacote: %s" % arquivo_LOG_pacote) # Escreve no terminal o nome do LOG de pacote gerado para esta seção
print ("Arquivo de LOG de gerencia: %s" % arquivo_LOG_gerencia) # Escreve no terminal o nome do LOG de gerência gerado para esta seção
LOG_gerencia = open(arquivo_LOG_gerencia, 'w') # abre o arquivo de LOG dos dados de gerência em modo de Edição
LOG_pacote = open(arquivo_LOG_pacote, 'w') # abre o arquivo de LOG dos pacotes em modo de Edição

print ('Time stamp;Contador;RSSI_DL;RSSI_UL;Perdas;PSR', file=LOG_gerencia) #Escreve uma linha de cabeçalho, especificando o conteúdo do LOG por Colunas
LOG_gerencia.flush() #Força a gravação dos dados no disco

#========== DOWNLINK ================
def downlink():
   global rssi_DL, rssi_UL, contador_UL, contador_DL, ultimo_pacote_DL, ultimo_pacote_UL, air_quality_indicator
   # Camada de Aplicação
   Pacote_DL[51] = 10
   Pacote_DL[50] = 12

   # Camada de Transporte
   contador_DL = contador_DL+1
   Pacote_DL[12] = int(contador_DL/256)
   Pacote_DL[13] = int(contador_DL%256)

   # Camada de Rede
   Pacote_DL[8] = ID_sensor
   Pacote_DL[10] = ID_base

   # Camada MAC

   # Camada Física
   #print(Pacote_DL)
   #ser.write(Pacote_DL)
   print('##### Pacote enviado para Nó Sensor (Downlink)')
   
def simulador_de_canal():
   global rssi_dl_sim, rssi_ul_sim, snr_dl_sim, rssi_ul_sim, contador_ul_sim, Pacote_UL, Pacote_DL, Pacote_Sim
   Pacote_Sim = Pacote_DL
   #print(Pacote_Sim)

   # Downlink: recebimento de pacote
   # Camada Física 
   Pacote_Sim[0] = random.randint(-70, -44) # RSSI DL Aleatório
   Pacote_Sim[1] = snr_dl_sim
   Pacote_Sim[2] = random.randint(-70, -44) # RSSI UP Aleatório

   # Camada MAC
   # não há nada ainda
   # Camada de Rede
   if (Pacote_Sim[10]== 0 and Pacote_Sim[8] ==1):
         
         #Camada de Transporte
         contador_ul_sim = contador_ul_sim+1

         #Camada de Aplicação
         Pacote_Sim[50] = Pacote_DL[50]
         Pacote_Sim[51] = Pacote_DL[51]

        # Uplink: envio do pacote
        #Camada de Aplicação

        #Camada de Transporte
         Pacote_Sim[14]= int(contador_ul_sim/256)
         Pacote_Sim[15]= int(contador_ul_sim%256)
        #Camada de Rede
         print("##### Simulador - Pacote enviado para Nó Sensor '")
         Pacote_Sim[8] = ID_base
         Pacote_Sim[10] = ID_sensor
        # Camada MAC
        # Camada Física
         Pacote_UL = Pacote_Sim
         print('##### Simulador - Pacote enviado pelo Nó Sensor ') 
         
#========== UPLINK ==================
def uplink():
   global perda_geral, rssi_DL, rssi_UL, contador_UL, ultimo_pacote_DL, air_quality_indicator
   
   # Camada Física
   #Pacote_UL = ser.read(52)
   #print(Pacote_UL)
   if(len(Pacote_UL)==52):
      rssi_DL = Pacote_UL[0]
      rssi_UL = Pacote_UL[2]

   # Camada MAC

   # Camada de Rede
      if(Pacote_UL[8]== 0 and Pacote_UL[10] ==1):
         print("##### OK - Pacote recebido (Uplink)")

   # Camada de Transporte
         contador_UL = int(Pacote_UL[14]*256) + Pacote_UL[15]
         ultimo_pacote_DL = int(Pacote_UL[12]*256) + Pacote_UL[13]

   # Camada de Aplicação      
         air_quality_indicator = Pacote_UL[51]
      #SUGESTÃO: RETIRAR as duas linhas abaixo, pois não se trata de um erro / perda de pacote, mas uma possível entrega errada.    
      #else:
         #perda_geral = perda_geral+1
   else:
      perda_geral = perda_geral+1
      print("##### FALHA - Pacote não recebido")
      
#========== Armazenamento de Dados no LOG de pacote
def gravaLOG_Pacote():
   with open(arquivo_LOG_pacote, 'a') as log:
        print(strftime("%d/%m/%Y %H:%M:%S"),";",Pacote_UL, file=log)
        
#========== Armazenamento de Dados para Exibição
#========== Armazenamento de Dados para Exibição
def gravaLOG_Gerencia():

     # 1. Grava no arquivo temporário (.tmp) para o Nível, 6 ler
     with open(arquivo_gerencia, 'a') as gerencia:
        print(medida_atual, ";", rssi_DL, ";", round(psr_geral, 2), ";", round(psr_geral, 2), ";", rssi_UL, file=gerencia, sep='')
     
     # 2. Grava no arquivo de LOG definitivo
     with open(arquivo_LOG_gerencia, 'a') as log_def:
        print(strftime("%d/%m/%Y %H:%M:%S"), ";", medida_atual, ";", rssi_DL, ";", rssi_UL, ";", perda_geral, ";", round(psr_geral, 2), file=log_def, sep='')
        
#===========Calculo da PSR geral
def calculaPSR():
    global medida_atual, perda_geral, psr_geral
    
    # Evita divisão por zero na primeira rodada
    if medida_atual > 0:
        # Sucesso = Total tentado (medida_atual) - Falhas (perda_geral)
        pacotes_recebidos = medida_atual - perda_geral
        psr_geral = (pacotes_recebidos / medida_atual) * 100
    else:
        psr_geral = 0.0

#========== Leitura de Parâmetros =============
while True:
   Parametros = open(arquivo_parametros, 'r')
   condicao_start = Parametros.readline()
   if (condicao_start != ''):
      condicao_start = int(condicao_start)
   
   #Lê o número de medidas a serem realizadas e converte para inteiro, pois no arquivo é armazenado como string
   numero_de_medidas = int(Parametros.readline())
   Parametros.close()


   if(condicao_start != ultima_condicao_start and condicao_start == 1):
      Gerencia = open(arquivo_gerencia, 'w').close()
      time.sleep(0.2)
   
   if (condicao_start == 1):
        
      #Apenas para imprimir um cabeçalho dos testes no terminal
      if (medida_atual == 0):
         print("################## Iniciando testes #################")
      
      if (medida_atual < numero_de_medidas):
         medida_atual = medida_atual + 1
         print("### Medida:",medida_atual, "de ",numero_de_medidas)

         downlink()
         time.sleep(tempo_entre_medidas)
         simulador_de_canal()
         uplink()
         gravaLOG_Pacote()
         
         #detectaPerdas - SUGESTÃO: retirar a ideia desta função, pois a identificação da perda ocorre na função de uplink
         #Separar em funções diferentes, na minha opinião, tornaria o código mais mais complexo.
         
         calculaPSR()
         gravaLOG_Gerencia()
         
         #gravaAplicacao
         
      else:
         # Se atingiu o limite, para o script alterando o arquivo PARAMETROS
         print("################## Testes finalizados ##################")
         medida_atual = 0
         condicao_start = 0
         #Atualiza arquivo de Parâmetros   
         Parametros = open(arquivo_parametros, 'w')
         Parametros.write("0\n") # Trava o start
         Parametros.write("0") #Limpa o número de medidas 
         Parametros.close()
   else:
     print("Script pausado")
     time.sleep(2)
      
   ultima_condicao_start = condicao_start
