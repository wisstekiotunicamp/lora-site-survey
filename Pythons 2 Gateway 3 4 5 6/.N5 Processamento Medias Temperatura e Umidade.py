
# -------- DECLARA BIBLIOTECAS PYTHON -------- 
import serial
import math
import time
import struct
import socket
import os

# -------- APAGA ARQUIVOS DE MEDIDAS DE MÉDIA ANTERIORES --------
if os.path.exists("media_temperatura.txt"):
    os.remove("media_temperatura.txt")

if os.path.exists("media_umidade.txt"):
    os.remove("media_umidade.txt")

# -------- CRIA NOVOS ARQUIVOS PARA ARMAZERAR AS NOVAS MEDIDAS DE MÉDIAS --------
temp_input = "medidas_temperatura.txt"
temp_output = "media_temperatura.txt"

umid_input = "medidas_umidade.txt"
umid_output = "media_umidade.txt"

# -------- RUNNING VARIABLES --------
temp_total = 0
temp_contador = 0

umid_total = 0
umid_contador = 0

try:

    with open(temp_input, "r") as temp_in, \
         open(umid_input, "r") as umid_in, \
         open(temp_output, "w") as temp_out, \
         open(umid_output, "w") as umid_out:

        print("")
        print("Para Interromper pressione (Ctrl+C)")
        print("")
        print("Realiza o cálculo Móvel da Média da Temperatura e Umidade do Nó Sensor LoRa")
        print("")

        # ==============================
        # PASSO 1 - REALIZA A LEITURA DOS ARQUIVOS SALVOS DE MEDIDAS DE TEMPERATURA E UMIDADE
        # ==============================

        # ---- Temperatura ----
        for line in temp_in:
            try:
                temperatura = float(line.strip())
                temp_contador += 1
                temp_total += temperatura
                media_temp = round(temp_total / temp_contador, 2)
                temp_out.write(f"{media_temp}\n")
            except ValueError:
                continue

        # ---- Umidade ----
        for line in umid_in:
            try:
                umidade = float(line.strip())
                umid_contador += 1
                umid_total += umidade
                media_umid = round(umid_total / umid_contador, 2)
                umid_out.write(f"{media_umid}\n")
            except ValueError:
                continue

        temp_out.flush()
        umid_out.flush()

        # ==============================
        # PASSO 2 - MONITORAMENTO DE NOVAS MEDIDAS DE TEMPERATURA E UMIDADE
        # ==============================
        while True:

            # ----- Lê novos dados de Temperatura -----
            temp_line = temp_in.readline()
            if temp_line:
                try:
                    temperatura = float(temp_line.strip())
                    temp_contador += 1
                    temp_total += temperatura
                    media_temp = round(temp_total / temp_contador, 2)

                    temp_out.write(f"{media_temp}\n")
                    temp_out.flush()

                except ValueError:
                    pass

            # ----- Lê novos dados de Umidade -----
            umid_line = umid_in.readline()
            if umid_line:
                try:
                    umidade = float(umid_line.strip())
                    umid_contador += 1
                    umid_total += umidade
                    media_umid = round(umid_total / umid_contador, 2)

                    umid_out.write(f"{media_umid}\n")
                    umid_out.flush()

                except ValueError:
                    pass

            
            print(f"Nova Temperatura: {temperatura} ; Média Temperatura: {media_temp} ; Nova Umidade: {umidade} ; Média Umidade: {media_umid} ")
            time.sleep(1)

except KeyboardInterrupt:
    print("\nInterrupção pelo usuário (Ctrl+C)")

finally:
    print("Fechando os arquivos")

