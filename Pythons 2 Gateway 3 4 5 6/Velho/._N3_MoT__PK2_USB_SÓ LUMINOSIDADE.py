# MoT - Python do Nível 3 do Kit Framework
import serial
import math
import time
import struct
import socket
from time import localtime, strftime
import os

# Camada física - definiição da COM
n_serial = input("Digite o número da serial = ") #seta a serial
n_serial1 = int(n_serial) - 1
ser = serial.Serial("COM"+str(n_serial), 115200, timeout=0.5,parity=serial.PARITY_NONE) # serial Windows

ser.reset_input_buffer()
ser.reset_output_buffer()

#============= Arquivos da dados
#apaga os arquivos temporários que foram gerados na rodada de testes anteriores
if os.path.exists("N4_Temp_luminosidade.txt"):
   os.remove("N4_Temp_luminosidade.txt")


# ======== Arquivos Nível 4 que armazenam as medidas realizadas
Arquivo_log_Luminosidade = strftime("N4_Log_dados_%Y_%m_%d_%H-%M-%S.txt") # Arquivo de log

# Arquivos temporários
Arquivo_temporário_Luminosidade = "N4_Temp_luminosidade.txt"

print ("Arquivo de log: %s" % Arquivo_log_Luminosidade)
N4_Log_dados = open(Arquivo_log_Luminosidade, 'w')

# Cria o vetor Pacote
PacoteDL = {}
PacoteUL= {}

perda_PK_UL = 0

# Cria Pacote de 52 bytes com valor zero em todas as posições
for i in range(52): # faz um array com 52 bytes
   PacoteDL[i] = 0
   PacoteUL[i] = 0

#inicializa variáveis auxiliares
Numero_medidas = 1000 # Realiza 1 milhão de medidas

try:
   # ============ Camada Física - Transmite o pacote        
   for j in range(1,Numero_medidas):
     
   # ============= Comandos e valores para serem enviados para o nó sensor

      arquivo = open('._N4_Comandos_N3_para_N1.txt', 'r') # leitura do arquivo comandos_oficina.txt que estão nas linhas
      PacoteDL[16] = int(arquivo.readline())  # LED amarelo
      PacoteDL[17] = int(arquivo.readline())  # Buzzer
      arquivo.close()
      PacoteDL[8]=1 # Endereço do nó sensor que vai receber o pacote de 52 bytes
      PacoteDL[10]=0 # Endereço da base que envia o pacote de 52 bytes
# ============= TRANSMITE O PACOTE            
                  
      for k in range(52): # transmite pacote
         Pacote_DL_Byte = chr(PacoteDL[k])
         ser.write(Pacote_DL_Byte.encode('latin1'))         
      
      # Aguarda a resposta do sensor
      time.sleep(0.5)

# ============= RECEBE O PACOTE

      PacoteUL = ser.read(52) # faz a leitura de 52 bytes do buffer que rec

      if len(PacoteUL) == 52:

   # ============= Luminosidade                
         Luminosidade = PacoteUL[18]*256+ PacoteUL[19]

         # ======imprime no shell do IDLE do Python
         print ('Cont = ', j,' Luminosidade = ', Luminosidade)

   # Salva no arquivo de log e arquivo temporário para exibição
         print (time.asctime(),';',j,';',Luminosidade,file=N4_Log_dados)

   # Arquivos temporários
         N4_Temp_luminosidade = open(Arquivo_temporário_Luminosidade, 'a+')
         print (Luminosidade,file=N4_Temp_luminosidade)
         N4_Temp_luminosidade.close()

#=======================LOOP DE 1000000
   print ('Pacotes enviados = ',j)
   N4_Log_dados.close()
   #Medidas.close()
   ser.close()
   print ('Fim da Execução')  # escreve na tela

except KeyboardInterrupt:
   ser.close()
   N4_Log_dados.close()
   N4_Temp_luminosidade.close()


