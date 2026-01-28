# N3 LoRa Site Survey - Versão 28/01/2026 - WissTek-IoT UNICAMP

# ==============================================================================
# IMPORTAÇÃO DE BIBLIOTECAS
# ==============================================================================
import serial   # Para comunicação com a porta Serial (USB)
import time     # Para funções de tempo (pausas, relógio)
import os       # Para lidar com arquivos e pastas do sistema operacional
import random   # Para gerar números aleatórios (usado na simulação)
from time import strftime # Importa função específica para formatar data e hora

# ==============================================================================
# VARIÁVEIS GLOBAIS
# ==============================================================================

# Variáveis de Controle
condicao_start = 0          # 0 = Parado, 1 = Rodando
modo_operacao = 0           # 0 = Simulação, 1 = Real
medida_atual = 0            # Contador de qual medida estamos fazendo

# Configurações Fixas
numero_de_medidas = 0       # Total de medidas para fazer
tempo_entre_medidas = 1     # Tempo de espera (segundos)
tamanho_do_pacote = 52      # Tamanho do pacote (bytes)
ID_base = 0                 
ID_sensor = 1               

# Porta Serial (Começa vazia)
ser = None 

# Variáveis de Estatística
rssi_DL = 0             
rssi_UL = 0             
contador_DL = 0         
contador_UL = 0         
psr_geral = 0           
perda_geral = 0         

# Máximos e Mínimos
rssi_max_dl = -200
rssi_min_dl = 200
rssi_max_ul = -200
rssi_min_ul = 200

# ==============================================================================
# CRIAÇÃO DOS VETORES (Listas de tamanho fixo)
# ==============================================================================
# Cria listas com 52 zeros. Funciona como um vetor fixo no Arduino.
Pacote_UL = [0] * tamanho_do_pacote 
Pacote_DL = [0] * tamanho_do_pacote
Pacote_Sim = [0] * tamanho_do_pacote # Usado na simulação

# Variáveis da Simulação
rssi_dl_sim = -52
rssi_ul_sim = -55
snr_dl_sim = 2
snr_ul_sim = 3
contador_ul_sim = 0

# ==============================================================================
# PREPARAÇÃO DOS ARQUIVOS
# ==============================================================================
dir_nivel4 = os.path.join(os.path.dirname(__file__), '../NIVEL4/')
arquivo_gerencia_tmp = os.path.join(dir_nivel4, 'dados_gerencia.tmp')
arquivo_aplicacao_tmp = os.path.join(dir_nivel4, 'dados_aplicacao.tmp')
arquivo_parametros = os.path.join(dir_nivel4, 'PARAMETROS.txt')

# Variáveis para nomes dos Logs (serão preenchidas no início do teste)
arquivo_LOG_pacote = ""
arquivo_LOG_gerencia = ""

# Limpeza inicial
if os.path.exists(arquivo_gerencia_tmp): os.remove(arquivo_gerencia_tmp) 
if os.path.exists(arquivo_aplicacao_tmp): os.remove(arquivo_aplicacao_tmp) 

# Cria arquivo de parâmetros zerado
Parametros = open(arquivo_parametros, 'w') 
Parametros.write("0\n0\n0") 
Parametros.close()

# ==============================================================================
# FUNÇÃO: DOWNLINK (Envia pacote)
# ==============================================================================
def downlink():
   global rssi_DL, rssi_UL, contador_DL, Pacote_DL
   
   #Limpa o pacote (enche de zeros) usando índice
   for i in range(tamanho_do_pacote):
       Pacote_DL[i] = 0
   
   # Camada de Aplicação
   # Preenche os dados 
   Pacote_DL[51] = 10 
   Pacote_DL[50] = 12

   #Camada de Transporte
   contador_DL = contador_DL + 1
   Pacote_DL[12] = int(contador_DL / 256) 
   Pacote_DL[13] = int(contador_DL % 256) 

   #Camada de Rede
   Pacote_DL[8] = ID_sensor 
   Pacote_DL[10] = ID_base  
   
   #Camada de Enlace - Não faz nada

   #Camada Física
   # Envio para o Hardware (Modo Real)
   if (modo_operacao == 1) and (ser is not None):
       
       # A função bytearray pega o nosso vetor de números e prepara para a serial (que recebe apenas bytes)
       ser.write(bytearray(Pacote_DL))

   print('##### Pacote enviado para Nó Sensor (Downlink)')

# ==============================================================================
# FUNÇÃO: SIMULADOR
# ==============================================================================
def simulador_de_canal():
   global contador_ul_sim, Pacote_UL, Pacote_DL, Pacote_Sim, rssi_dl_sim
   
   # Copia DL para Simulação (índice por índice)
   for i in range(tamanho_do_pacote):
       Pacote_Sim[i] = Pacote_DL[i]

   # Simula as RSSis de Downlink e Uplink
   Pacote_Sim[0] = random.randint(-70, -44) 
   Pacote_Sim[1] = 2
   Pacote_Sim[2] = random.randint(-70, -44) 

   if (Pacote_Sim[10] == 0 and Pacote_Sim[8] == 1):
         contador_ul_sim = contador_ul_sim + 1
         
         Pacote_Sim[50] = Pacote_DL[50]
         Pacote_Sim[51] = Pacote_DL[51]
         Pacote_Sim[14] = int(contador_ul_sim / 256)
         Pacote_Sim[15] = int(contador_ul_sim % 256)
         
         print("##### Simulador - Pacote enviado para Nó Sensor '")
         
         Pacote_Sim[8] = ID_base
         Pacote_Sim[10] = ID_sensor
         
         # Entrega para o vetor de recepção (UL)
         for i in range(tamanho_do_pacote):
             Pacote_UL[i] = Pacote_Sim[i]
             
         print('##### Simulador - Pacote enviado pelo Nó Sensor ') 

# ==============================================================================
# FUNÇÃO: UPLINK (Recebe pacote)
# ==============================================================================
def uplink():
   global perda_geral, rssi_DL, rssi_UL, contador_UL, Pacote_UL
   
   #Camada Física
   # Leitura do Hardware
   #Se o modo de operação é 1 (real) e existe um objeto da serial
   if (modo_operacao == 1) and (ser is not None):
       if(ser.in_waiting > 0):
           
           # Lê 52 bytes da serial
           Pacote_UL_bytes = ser.read(52)
           
           # Verifica se leu o tamanho certo
           if len(Pacote_UL_bytes) == 52:
               # Copia para o nosso vetor Pacote_UL usando índice (i)
               for i in range(52):
                   Pacote_UL[i] = Pacote_UL_bytes[i]
           else:
               # Se leitura falhou/incompleta, zera o pacote
               Pacote_UL = [] 
               
       else:
           Pacote_UL = [] 

   # Obtém os dados da Camada Física
   if(len(Pacote_UL) == 52):
      
      valor_dl = Pacote_UL[0]
      valor_ul = Pacote_UL[2]
      
      # Calcula a RSSI caso o modo de operação seja 1 (real)
      if modo_operacao == 1:
          if valor_dl > 127: rssi_DL = valor_dl - 256
          else: rssi_DL = valor_dl
          
          if valor_ul > 127: rssi_UL = valor_ul - 256
          else: rssi_UL = valor_ul
      #Caso o modo de operação seja 0 (simulado) entregar os valores simulados
      else:
          rssi_DL = valor_dl
          rssi_UL = valor_ul

      #Camada MAC - Não faz nada
      
      
      #Camada Rede
      if(Pacote_UL[8] == 0 and Pacote_UL[10] == 1):
         print("##### OK - Pacote recebido (Uplink)")

      #Camada Transporte
      contador_UL = int(Pacote_UL[14] * 256) + Pacote_UL[15]
      
      #Camada Aplicação
      #Não faz nada nessa versão

   else:
      perda_geral = perda_geral + 1
      print("##### FALHA - Pacote não recebido")
      
# ==============================================================================
# FUNÇÕES DE LOG E CÁLCULO
# ==============================================================================
def gravaLOG_Pacote():
   arquivo = open(arquivo_LOG_pacote, 'a')
   print(strftime("%d/%m/%Y %H:%M:%S"), ";", Pacote_UL, file=arquivo)
   arquivo.close()

def gravaLOG_Gerencia():
     global rssi_max_dl, rssi_min_dl, rssi_max_ul, rssi_min_ul

     arquivo_tmp = open(arquivo_gerencia_tmp, 'a')
     print(medida_atual, ";", rssi_DL, ";", round(psr_geral, 2), ";", round(psr_geral, 2), ";", rssi_UL, ";", rssi_max_dl, ";", rssi_min_dl, ";", rssi_max_ul, ";", rssi_min_ul, file=arquivo_tmp, sep='')
     arquivo_tmp.close()
     
     arquivo_def = open(arquivo_LOG_gerencia, 'a')
     print(strftime("%d/%m/%Y %H:%M:%S"), ";", medida_atual, ";", rssi_DL, ";", rssi_UL, ";", perda_geral, ";", round(psr_geral, 2), ";", rssi_max_dl, ";", rssi_min_dl, ";", rssi_max_ul, ";", rssi_min_ul, file=arquivo_def, sep='')
     arquivo_def.close()
        
#Calcula a PSR Geral 
def calculaPSR():
    global medida_atual, perda_geral, psr_geral
    if medida_atual > 0:
        pacotes_recebidos = medida_atual - perda_geral
        psr_geral = (pacotes_recebidos / medida_atual) * 100
    else:
        psr_geral = 0.0

#Acha o valor Máximo e Mínimo das RSSIs coletadas
def calculaMaxMinRSSI():
    global rssi_DL, rssi_UL, rssi_max_dl, rssi_min_dl, rssi_max_ul, rssi_min_ul
    
    if (rssi_DL > rssi_max_dl): 
       rssi_max_dl = rssi_DL
    if (rssi_DL < rssi_min_dl): 
       rssi_min_dl = rssi_DL

    if (rssi_UL > rssi_max_ul): 
       rssi_max_ul = rssi_UL
    if (rssi_UL < rssi_min_ul): 
       rssi_min_ul = rssi_UL

# ==============================================================================
# LOOP PRINCIPAL
# ==============================================================================
while True:
   
   # 1. Leitura de Parâmetros - Lê todo início de loop 
   if os.path.exists(arquivo_parametros):
       Parametros = open(arquivo_parametros, 'r')
       
       linha = Parametros.readline()
       if len(linha) > 0: condicao_start = int(linha)
       
       linha = Parametros.readline()
       if len(linha) > 0: numero_de_medidas = int(linha)
          
       linha = Parametros.readline()
       if len(linha) > 0: modo_operacao = int(linha)
       else: modo_operacao = 0 
           
       Parametros.close()

   # 2. Controle da Serial (Liga/Desliga)
   if (modo_operacao == 1) and (ser is None):
       print("--- ATIVANDO MODO REAL ---")
       # Ajuste a porta aqui (/dev/ttyUSB0 ou COMx)
       ser = serial.Serial("/dev/ttyUSB0", 115200, timeout=0.5, parity=serial.PARITY_NONE)

   if (modo_operacao == 0) and (ser is not None):
       print("--- ATIVANDO MODO SIMULAÇÃO ---")
       ser.close()
       ser = None

   # 3. Execução do Teste
   if (condicao_start == 1):
      
      # SE FOR A PRIMEIRA MEDIDA (Medida 0), FAZ O SETUP INICIAL
      if (medida_atual == 0):
          print("################## INICIANDO NOVO TESTE #################")
          
          # Reseta variáveis
          contador_DL = 0; contador_UL = 0
          psr_geral = 0; perda_geral = 0
          rssi_DL = 0; rssi_UL = 0
          rssi_max_dl = -200; rssi_min_dl = 200
          rssi_max_ul = -200; rssi_min_ul = 200
          
          # Cria Arquivos de Log novos
          arquivo_LOG_pacote = os.path.join(dir_nivel4, strftime("LOG_pacote_%Y_%m_%d_%H-%M-%S.txt"))
          arquivo_LOG_gerencia = os.path.join(dir_nivel4, strftime("LOG_gerencia_%Y_%m_%d_%H-%M-%S.txt"))
          
          # Cria cabeçalhos
          arq_log = open(arquivo_LOG_gerencia, 'w')
          print ('Time stamp;Contador;RSSI_DL;RSSI_UL;Perdas;PSR;Max_DL;Min_DL;Max_UL;Min_UL', file=arq_log)
          arq_log.close()
          
          # Limpa temporário
          arq_tmp = open(arquivo_gerencia_tmp, 'w')
          arq_tmp.close()

      # VERIFICA SE DEVE CONTINUAR MEDINDO
      if (medida_atual < numero_de_medidas):
         medida_atual = medida_atual + 1
         print("### Medida:", medida_atual, "de ", numero_de_medidas)

         #Chama a função de downlink para enviar o pacote
         downlink()
         time.sleep(tempo_entre_medidas)
         
         #Se está no modo simulador, chama a função de simulação do canal
         if (modo_operacao == 0):
            simulador_de_canal()
        
         #Chama a função de uplink para receber o pacote
         uplink()
         
         #Chama a função de registro do pacote bruto
         gravaLOG_Pacote()
         
         calculaPSR()
         calculaMaxMinRSSI() 
         gravaLOG_Gerencia()
         
      else:
         # FIM DO TESTE
         print("################## TESTE FINALIZADO ##################")
         
         # Para o teste alterando o arquivo de parâmetros
         Parametros = open(arquivo_parametros, 'w')
         Parametros.write("0\n0\n") 
         Parametros.write(str(modo_operacao)) 
         Parametros.close()
         
         # Reseta a condição local para parar de entrar neste IF
         condicao_start = 0
         # Reseta medida atual para que o próximo teste comece do zero
         medida_atual = 0

   else:
     # Se condicao_start for 0
     # Garante que medida está zerada para o próximo teste ser detectado como novo
     medida_atual = 0 
     print("Script pausado...")
     time.sleep(2)
