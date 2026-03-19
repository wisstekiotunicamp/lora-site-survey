# Python para o Radiuino over Arduino
import serial
import math
import time
import struct
import socket
from time import localtime, strftime
import os

# Configura a serial
# para COM# o número que se coloca é n-1 no primeiro parâmetrso. Ex COM9  valor 8
n_serial = input("Digite o número da serial = ") #seta a serial
n_serial1 = int(n_serial) - 1
ser = serial.Serial("COM"+str(n_serial), 115200, timeout=0.5,parity=serial.PARITY_NONE) # serial Windows
#ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1) # serial Linux
#ser = serial.Serial('/dev/cu.usbserial-0001', 115200, timeout=1) # serial OSX
           
# Aguarde o NodeMCU "acordar" após o reset da conexão
print("Aguardando estabilização...")
time.sleep(2) # Aguarda 2s NodeMCU inicializar
ser.flushInput() # Limpa qualquer lixo de memória do boot
print("Porta Serial Conectada")

# Camada de Aplicação
byte34 = 0 # LED verde
byte37 = 0 # LED amarelo
byte40 = 0 # LED vermelho

# Camada de Transporte
byte12 = 0
byte13 = 0
byte14 = 0
perda_PK_RX = 0 # contador de pacotes perdidos na recepção

# Camada de Rede
byte8 = 1
byte10 = 0
#apaga o arquivo de medidas
if os.path.exists("medidas_rssi.txt"):
   os.remove("medidas_rssi.txt")
if os.path.exists("medidas_luminosidade.txt"):
   os.remove("medidas_luminosidade.txt")
# Cria os arquivos de log
filename1 = strftime("B_Medidas_%Y_%m_%d_%H-%M-%S.txt")
filename2 = "medidas_rssi.txt"
filename3 = "medidas_luminosidade.txt"
print ("Arquivo de log: %s" % filename1)
Log_dados = open(filename1, 'w')


# Salva títulos das colunas no arquivo de log
print ('Time stamp;Contador;RSSI_DL;PSR;Status LED NodeMCU; Status LED Esp',file=Log_dados)

# Entra com quantas medidas vai realizar
num_medidas = input('Entre com o número de medidas = ')

# Cria o vetor Pacote
PacoteTX =[0]*52
PacoteRX=[0]*52

# Cria Pacote de 52 bytes com valor zero em todas as posições
for i in range(52): # faz um array com 52 bytes
   PacoteTX[i] = 0
   PacoteRX[i] = 0

# Camada de Aplicação
PacoteTX[16] = 16
PacoteTX[17] = 17
PacoteTX[18] = 18
PacoteTX[34] = byte34
PacoteTX[37] = byte37
PacoteTX[40] = byte40

# Camada de rede
PacoteTX[8] = int (byte8) #origem
PacoteTX[10] = int (byte10) #destino

#inicializa variáveis auxiliares
w = int(num_medidas)+1
perda_PK_RX =0
i = 0
contador = 0
PKT_down = 0

try:
   # ============ Camada Física - Transmite o pacote        
   for j in range(1,w):

      
      
      # ==== Camada de Transporte contagem de pacotes de descida
      PKT_down = PKT_down + 1
      if PKT_down == 256:
         PKT_down = 0
      byte12 = PKT_down
      PacoteTX[12] = int(byte12)
      PacoteTX[13] = int(byte13)

   # ============= Camada de Aplicação comandos para a placa

      arquivo = open('comandos_oficina.txt', 'r') # leitura do arquivo comandos_oficina.txt que estão nas linhas
      byte34 = int(arquivo.readline())
      byte37 = int(arquivo.readline())
      byte40 = int(arquivo.readline())
      byte43 = int(arquivo.readline())
      arquivo.close()
      
      PacoteTX[8] = 1
      PacoteTX[10] = 0
      PacoteTX[34] = byte34
      PacoteTX[37] = byte37
      PacoteTX[40] = byte40            
      PacoteTX[43] = byte43

## ============= CAMDA FÍSICA TRANSMITE O PACOTE            


                  
      for k in range(52): # transmite pacote
         TXbyte = chr(PacoteTX[k])
         ser.write(TXbyte.encode('latin1'))
           
      
      # Aguarda a resposta do sensor
      time.sleep(1)
      

   # ============= Camada Física - Recebe o pacote


      Pacote_RX = ser.read(52) # faz a leitura de 52 bytes do buffer que rec

      if len(Pacote_RX) == 52:
         # RSSI Uplink
         byte0 = Pacote_RX[0]
         if byte0 > 128:
            RSSIu = ((byte0-256)/2.0)-74
         else:
            RSSIu = (byte0/2.0)-74
         # RSSI Downlink
         byte2 = Pacote_RX[2]
         if byte2 > 128:
            RSSId = ((byte2-256)/2.0)-74
         else:
            RSSId = (byte2/2.0)-74

   # ============= Camada MAC
         byte4 = Pacote_RX[4]
         byte5 = Pacote_RX[5]
         byte6 = Pacote_RX[6]
         byte7 = Pacote_RX[7]

   # ============= Camada Rede
         byte8 = Pacote_RX[8]
         byte9 = Pacote_RX[9]
         byte10 = Pacote_RX[10]
         byte11 = Pacote_RX[11]
         
   # ============= Camada Transporte

         byte12 = Pacote_RX[12]
         byte14 = Pacote_RX[14]
         byte15 = Pacote_RX[15]
         PKTup = byte14 * 256 + byte15

   # ============= Camada Aplicação                  
         luminosidade = 1023 -(Pacote_RX[17]*256+ Pacote_RX[18])
         #Status_led_nodemcu = Pacote_RX[34]
         #Status_led_esp = Pacote_RX[40]
         

         print ('Cont = ', j,' RSSI = ', RSSId,' Lum = ', luminosidade)

         # Salva no arquivo de log
         print (time.asctime(),';',j,';',RSSId,';',luminosidade,file=Log_dados)
         Medidas_rssi = open(filename2, 'a+')
         print (RSSId,file=Medidas_rssi)
         Medidas_rssi.close()

         Medidas_lumi = open(filename3, 'a+')
         print (luminosidade,file=Medidas_lumi)
         Medidas_lumi.close()

         
         
      else: #Caso de erro de recepção
         perda_PK_RX = perda_PK_RX+1
         #PSR = round((1-(perda_PK_RX / j))*100,2)
         print ('Cont = ', j,' PERDEU PACOTE ')
         
         # Salva no arquivo de log
         print (time.asctime(),';',j,';;',file=Log_dados)
         Medidas = open(filename2, 'a+')
         print (j,';;',perda_PK_RX,file=Medidas)
         Medidas.close()

         
   print ('Pacotes enviados = ',j,' Pacotes perdidos = ',perda_PK_RX)
   Log_dados.close()
   if perda_PK_RX > 0:
      Medidas.close()   
   ser.close()
   print ('Fim da Execução')  # escreve na tela

except KeyboardInterrupt:
   ser.close()
   Log_dados.close()
   Medidas_rssi.close()
   Medidas_lumi.close()


''' SIGNIFICADO DOS BYTES DO PACOTE DE DESCIDA
byte0
byte1
byte2
byte3
byte4
byte5
byte6
byte7
byte8
byte9
byte10
byte11
byte12
byte13
byte14
byte15
byte16
byte17
byte18
byte19
byte20
byte21
byte22
byte23
byte24
byte25
byte25
byte26
byte27
byte28
byte29
byte30
byte31
byte32
byte33
byte34
byte35
byte36
byte37
byte38
byte39
byte41
byte42
byte43
byte44
byte45
byte46
byte47
byte49
byte49
byte50
byte51
'''
