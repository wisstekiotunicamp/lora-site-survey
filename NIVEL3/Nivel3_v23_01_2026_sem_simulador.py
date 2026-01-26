# N3 LoRa Site Survey - Versão 23/01/2026 - WissTek-IoT UNICAMP - Lucas Alachev/Branquinho
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

# Zera variáveis
numero_de_medidas = 0
rota = [] # neste momento é um enlace ponto a ponto, que futuramente poderá ser usada para roteamento
condicao_start = 0
ultima_condicao_start = 0

 # Camada Física
tamanho_do_pacote = 52 # define o tamanho do pacote
# Zera variáveis do pacote
rssi_DL = 0
rssi_UL = 0 
snr_DL = 0
snr_UL = 0

 # === Camada MAC
tempo_entre_medidas = 1
# Em função do spreading factor, BW e coding rate será calculado a duração de pacote
# que vai definir o tempo entre os pacotes para realizar o LoRa Site Survey

 # === Camada de Rede
ID_base = 0 # Identificação da base que está enviando o pacote de DL
ID_sensor = 1 # Identificação do Nó Sensor LoRa que vai receber o pacote

# === Camada de Transporte
# Somente zera as variáveis utilizadas para contagem dos pacotes de DL e UL 
contador_DL = 0
ultimo_pacote_DL = 0
contador_UL = 0
ultimo_pacote_UL = 0

# === Contabilização de PSR Geral
psr_geral = 0 
perda_geral = 0

# === Camada de Aplicação
# Zera as variáveis das grandezas que serão capturadas pelo Nó Sensor LoRa
# Na PK-LoRa utilizada no Nó Sensor LoRa a única grandeza medida é a luminosidade
luminosidade = 0

# Variável Auxiliar para contagem dos pacotes transmitidos de DL
pacote_atual = 0 

#========== Criação de Pacotes
Pacote_DL = [0] * tamanho_do_pacote
Pacote_UL = [0] * tamanho_do_pacote

#========== Configuração da Porta Serial ==================
# para COM# o número que se coloca é n-1 no primeiro parâmetrso. Ex COM9  valor 8
n_serial = input("Digite o número da porta COM = ") #seta a serial
n_serial1 = int(n_serial) - 1
ser = serial.Serial("COM"+str(n_serial), 115200, timeout=0.5,parity=serial.PARITY_NONE) # serial Windows
print("Porta Serial Conectada:",n_serial)

# ========= ESTRATÉGIA DE ARQUIVOS
# Arquivos temporário são arquivos apenas para visualização no gráfico que são gerados
# na rodada de medidas atual e serão apagados para a próxima rodada de medidas
# Arquivos de Log são os arquivos com os resultados das medidas e são armazenados no Nível 4

#========== DELETA ARQUIVOS DE VISUALIZAÇÃO QUE SÃO TEMPORÁRIOS ===============
# Este conjunto de linhas serve para deletar os arquivos temporários de armazenamento para observação de dados em tempo real

if os.path.exists(os.path.join(os.path.dirname(__file__), '../NIVEL4/dados_gerencia.tmp')): # Procura no Nível 4 se há um arquivo de gerência
   os.remove(os.path.join(os.path.dirname(__file__), '../NIVEL4/dados_gerencia.tmp')) # Se há um arquivo de gerência, ele é deletado

if os.path.exists(os.path.join(os.path.dirname(__file__), '../NIVEL4/dados_aplicacao.tmp')):# Procura no Nível 4 se há um arquivo de aplicação
   os.remove(os.path.join(os.path.dirname(__file__), '../NIVEL4/dados_aplicacao.tmp')) # Se há um arquivo de aplicação, ele é deletado

if os.path.exists(os.path.join(os.path.dirname(__file__), '../NIVEL4/PARAMETROS.txt')):# Procura no Nível 4 se há um arquivo de Parametros
   os.remove(os.path.join(os.path.dirname(__file__), '../NIVEL4/PARAMETROS.txt')) # Se há um arquivo de Parametros, ele é deletado

#============ CRIA ARQUIVOS TEMPORÁRIOS PARA A ATUAL RODADA DE MEDIDAS ================   
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

# ================= CRIA ARQUIVOS DE LOG QUE SÃO ARMAZENADOS A CADA RODADA DE MEDIDAS ======
# Criação do arquivo de LOG para armanezamento completo dos dados aquisitados
# Cria um arquivo de log para armazenar os pacotes brutos recebidos
arquivo_LOG_pacote = os.path.join(os.path.dirname(__file__), strftime("../NIVEL4/LOG_pacote_%Y_%m_%d_%H-%M-%S.txt")) # Cria o arquivo de LOG

#Cria um arquivo de log para armazenar os dados de gerência extraídos do pacote
arquivo_LOG_gerencia = os.path.join(os.path.dirname(__file__), strftime("../NIVEL4/LOG_gerencia_%Y_%m_%d_%H-%M-%S.txt")) # Cria o arquivo de LOG

print ("Arquivo de LOG de pacote: %s" % arquivo_LOG_pacote) # Escreve no terminal o nome do LOG de pacote gerado para esta seção
print ("Arquivo de LOG de gerencia: %s" % arquivo_LOG_gerencia) # Escreve no terminal o nome do LOG de gerência gerado para esta seção
LOG_gerencia = open(arquivo_LOG_gerencia, 'w') # abre o arquivo de LOG dos dados de gerência em modo de Edição
LOG_pacote = open(arquivo_LOG_pacote, 'w') # abre o arquivo de LOG dos pacotes em modo de Edição

print ('Time stamp;Contador;RSSI_DL;RSSI_UL;Perdas;PSR', file=LOG_gerencia) #Escreve uma linha de cabeçalho, especificando o conteúdo do LOG por Colunas
LOG_gerencia.flush() #Força a gravação dos dados no disco

#========== TRANSMISSÃO DO PACOTE DE DOWNLINK ================
def downlink():
   global rssi_DL, rssi_UL, contador_UL, contador_DL, ultimo_pacote_DL, ultimo_pacote_UL, air_quality_indicator

   # === Camada de Aplicação
   # Nesse código não existe nenhuma ação que deve ser executada no Nó Sensor Lora
   # Para debug de código são utilizados os bytes
   # Somente como exemplo no byte do DL vai algum comando que será executado no Nó Sensor LoRa
   # Por exemplo ligar o LED verde
   Pacote_DL[34] = 1


   # === Camada de Transporte
   contador_DL = contador_DL+1 # Contador de pacotes de DL
   Pacote_DL[12] = int(contador_DL/256)
   Pacote_DL[13] = int(contador_DL%256)

   # === Camada de Rede
   Pacote_DL[8] = ID_sensor
   Pacote_DL[10] = ID_base

   # === Camada MAC
   # Aqui é calculado o tempo de duração do pacote de DL e UL
   # Pacote_DL[4] = TEMPO ENTRE PACOTES

   # === Camada Física
   # Na camada física vão os parâmetros do LoRa:
   # spreading factor, BW, coding rate, potência de TX. Esses valores serão informado
   # na tela de parametrização dos testes
   # No DL nos bytes 0, 1, 2 e 3 vão os parâmetros do LoRa
   # Pacote_DL[0] = SPREADING FACTOR
   # Pacote_DL[1] = BW
   # Pacote_DL[2] = Coding Rate
   # Pacote_DL[3] = Potência de transmissão
   print(Pacote_DL)
   ser.write(Pacote_DL)
   print('##### Pacote enviado para Nó Sensor (Downlink)')
     
#========== RECEBE O PACOTE DE UPLINK ==================
def uplink():
   global perda_geral, rssi_DL, rssi_UL, contador_UL, ultimo_pacote_DL, air_quality_indicator
   
   # === Camada Física
   # Leitura do buffer da serial para verificação se chegou o pacote de UL
   Pacote_UL = ser.read(52)
   print(Pacote_UL)

   # Checa se o pacote recebido tem 52 bytes. Isso indica que o pacote foi recebido
   if(len(Pacote_UL)==52):
      # Leitura das RSSI e SNR de DL e UL
      rssi_DL = (-1)* Pacote_UL[0]
      snr_DL = Pacote_UL[1]
      rssi_UL = (-1)* Pacote_UL[2]
      snr_UL = Pacote_UL[3]

   # Camada MAC
   # Nessa versão 1 do LoRa Site Survey não são utilizados os bytes 4, 5, 6 e 7

   # Camada de Rede
      # Checa se o pacote recebido é do Nó Sensor 1 endereçado para a base 0
      if(Pacote_UL[8]== 0 and Pacote_UL[10] ==1):
         print("##### OK - Pacote recebido (Uplink)")

   # Camada de Transporte
         contador_UL = int(Pacote_UL[14]*256) + Pacote_UL[15]
         ultimo_pacote_DL = int(Pacote_UL[12]*256) + Pacote_UL[13]

   # Camada de Aplicação      
         # tipo_sensor = Pacote_UL[16] # Tipo de sensor
         # inteiro = Pacote_UL[17]
         # resto = Pacote_UL[18]
         # luminosidade = inteiro*256 + resto
      
   else:
      perda_geral = perda_geral+1
      print("##### FALHA - Pacote não recebido")
      
#========== Armazenamento de Dados no LOG de pacote
def gravaLOG_Pacote():
   with open(arquivo_LOG_pacote, 'a') as log:
        print(strftime("%d/%m/%Y %H:%M:%S"),";",Pacote_UL, file=log)
        
#========== Armazenamento de Dados para Exibição
def gravaLOG_Gerencia():

     # 1. Grava no arquivo temporário (.tmp) para o Nível, 6 ler
     with open(arquivo_gerencia, 'a') as gerencia:
        print(pacote_atual, ";", rssi_DL, ";", round(psr_geral, 2), ";", round(psr_geral, 2), ";", rssi_UL, file=gerencia, sep='')
     
     # 2. Grava no arquivo de LOG de gerência
     with open(arquivo_LOG_gerencia, 'a') as log_def:
        print(strftime("%d/%m/%Y %H:%M:%S"), ";", pacote_atual, ";", rssi_DL, ";", rssi_UL, ";", perda_geral, ";", round(psr_geral, 2), file=log_def, sep='')
        
#===========Calculo da PSR geral
def calculaPSR():
    global pacote_atual, perda_geral, psr_geral
    
    # Evita divisão por zero na primeira rodada
    if pacote_atual > 0:
        # Sucesso = Total tentado (pacote_atual) - Falhas (perda_geral)
        pacotes_recebidos = pacote_atual - perda_geral
        psr_geral = (pacotes_recebidos / pacote_atual) * 100
    else:
        psr_geral = 0.0

#========== INÍCIO DA EXECUÇÃO DA RODADA DE TESTES
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

#============ REALIZAÇÃO DA RODADA DE MEDIDAS====================
   if (condicao_start == 1):
        
      #Apenas para imprimir um cabeçalho dos testes no terminal
      if (pacote_atual == 0):
         print("################## Iniciando testes #################")
      
      if (pacote_atual < numero_de_medidas):
         pacote_atual = pacote_atual + 1
         print("### Medida:",pacote_atual, "de ",numero_de_medidas)

         # Chama função de DL
         downlink()

         # Aguarda tempo entre medidas
         time.sleep(tempo_entre_medidas)

         # Chama função de UL
         uplink()

         # Chama função de gravação de arquivos de Log
         gravaLOG_Pacote()

         # Chama função de cálculo da PSR geral
         calculaPSR()

         # Chama função que grava Log com informações de gerência
         gravaLOG_Gerencia()
         
      else:
         # Final da rodada de teste
         print("################## Rodada de teste finalizada ##################")
         pacote_atual = 0
         condicao_start = 0
         #Atualiza arquivo de Parâmetros   
         Parametros = open(arquivo_parametros, 'w')
         Parametros.write("0\n") # Trava o start
         Parametros.write("0") #Limpa o número de medidas 
         Parametros.close()
   else:
     print("Script pausado")
     time.sleep(1)
      
   ultima_condicao_start = condicao_start
