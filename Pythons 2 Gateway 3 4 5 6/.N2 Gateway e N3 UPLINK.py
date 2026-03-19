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
n_serial = input("Digite o número da serial do Gateway LoRa = COM ") #seta a serial
n_serial1 = int(n_serial) - 1
ser = serial.Serial("COM"+str(n_serial), 115200, timeout=0.5,parity=serial.PARITY_NONE) # serial Windows
#ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1) # serial Linux
#ser = serial.Serial('/dev/cu.usbserial-0001', 115200, timeout=1) # serial OSX
           
# Aguarde o NodeMCU "acordar" após o reset da conexão
print("Aguardando estabilização...")
time.sleep(2) # Aguarda 2s NodeMCU inicializar
ser.flushInput() # Limpa qualquer lixo de memória do boot
print("Porta Serial Conectada")

# Define o tamanho do Pacote
TAMANHO_PACOTE = 52

# Cria o vetor Pacote
Pacote_UL=[0]*TAMANHO_PACOTE

# Contador de Pacotes para Log
contador = 0

#apaga o arquivo de medidas
if os.path.exists("medidas_rssi.txt"):
   os.remove("medidas_rssi.txt")
if os.path.exists("medidas_luminosidade.txt"):
   os.remove("medidas_luminosidade.txt")
if os.path.exists("medidas_temperatura.txt"):
   os.remove("medidas_temperatura.txt")
if os.path.exists("medidas_umidade.txt"):
   os.remove("medidas_umidade.txt")
   
# Cria os arquivos de log
arquivo_de_medidas = strftime("B_Medidas_%Y_%m_%d_%H-%M-%S.txt")
print ("Arquivo de log: %s" % arquivo_de_medidas)
Log_dados = open(arquivo_de_medidas, 'w')


# Salva títulos das colunas no arquivo de log
print ('Data Hora;Contador;RSSI_UL;Luminosidade;Temperatura;Umidade',file=Log_dados)


try:
    
    # Abrir/Criar os arquivos de texto de LOG
    with open("salva_pacote.txt", "w") as bytes_recebidos, \
         open("medidas_rssi.txt", "w") as valor_rssi, \
         open("medidas_luminosidade.txt", "w") as valor_lum, \
         open("medidas_temperatura.txt", "w") as valor_temp, \
         open("medidas_umidade.txt", "w") as valor_umid:

        print("")
        print("Para Interromper pressione (Ctrl+C)")
        print("")
        print("Leitura do Nó Sensor LoRa (Luminosidade, Temperatura e Umidade)")
        print("")

  
        while True:
            if ser.in_waiting >= TAMANHO_PACOTE:
                Pacote_UL = ser.read(TAMANHO_PACOTE)  # Lê os 52 bytes na serial
                contador = contador + 1
                # ----------------------------
                # Salvar todos os 52 bytes num arquivo
                # ----------------------------            
                # Converte os bytes em string separados por virgula ","
                pacote = ",".join(str(b) for b in Pacote_UL)
            
                bytes_recebidos.write(pacote + "\n")
                bytes_recebidos.flush()  # Salva no arquivo TXT os Bytes de Uplink
                           
                # RSSI Uplink
                RSSI_UL = Pacote_UL[2]
                if RSSI_UL > 128:
                   RSSIu = ((RSSI_UL-256)/2.0)-74
                else:
                   RSSIu = (RSSI_UL/2.0)-74
                RSSIu = int(RSSIu) # Obtem o valor inteiro do RSSI Uplink   
                luminosidade = 1023 -(Pacote_UL[17]*256 + Pacote_UL[18])

                # ====== Temperatura ======
                # Mesmo padrão da luminosidade: byte alto * 256 + byte baixo, depois divide por 100
                temperatura = (Pacote_UL[20] * 256 + Pacote_UL[21]) / 100.0

                # ====== Umidade ======
                # Mesmo padrão da luminosidade: byte alto * 256 + byte baixo, depois divide por 100
                umidade = (Pacote_UL[23] * 256 + Pacote_UL[24]) / 100.0

                # Mostra os valores no terminal
                print(f'RSSI={RSSIu} dBm | Lum={luminosidade} | Temp={temperatura} °C | Umid={umidade} %')
            
                # ----------------------------
                # Salva os valores de RSSI, Luminosidade, Temperatura e Umidade
                # ----------------------------
                valor_lum.write(f"{luminosidade}\n")
                valor_lum.flush()
                valor_rssi.write(f"{RSSIu}\n")
                valor_rssi.flush()
                valor_temp.write(f"{temperatura}\n")
                valor_temp.flush()
                valor_umid.write(f"{umidade}\n")
                valor_umid.flush()
                linha_log_dados = f"{time.asctime()};{contador};{RSSIu};{luminosidade};{temperatura};{umidade}\n"
                Log_dados.write(linha_log_dados)
                Log_dados.flush()

                
except KeyboardInterrupt:
    print("\nInterrupção pelo usuário (Ctrl+C)")

finally:
    print("Fechando os arquivos e conexão serial...")

    valor_rssi.close()
    valor_lum.close()
    valor_temp.close()
    valor_umid.close()
    Log_dados.close()
    ser.close()

    print("Arquivos fechados com segurança")



            

