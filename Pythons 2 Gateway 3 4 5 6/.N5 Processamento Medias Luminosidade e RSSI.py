
# -------- DECLARA BIBLIOTECAS PYTHON -------- 
import serial
import math
import time
import struct
import socket
import os

# -------- APAGA ARQUIVOS DE MEDIDAS DE MÉDIA ANTERIORES --------
if os.path.exists("media_luminosidade.txt"):
    os.remove("media_luminosidade.txt")

if os.path.exists("media_rssi.txt"):
    os.remove("media_rssi.txt")

# -------- CRIA NOVOS ARQUIVOS PARA ARMAZERAR AS NOVAS MEDIDAS DE MÉDIAS --------
lum_input = "medidas_luminosidade.txt"
lum_output = "media_luminosidade.txt"

rssi_input = "medidas_rssi.txt"
rssi_output = "media_rssi.txt"

# -------- RUNNING VARIABLES --------
lum_total = 0
lum_contador = 0

rssi_total = 0
rssi_contador = 0

try:

    with open(lum_input, "r") as lum_in, \
         open(rssi_input, "r") as rssi_in, \
         open(lum_output, "w") as lum_out, \
         open(rssi_output, "w") as rssi_out:

        print("")
        print("Para Interromper pressione (Ctrl+C)")
        print("")
        print("Realiza o cálculo Móvel da Média da Intensidade Luminosa do Nó Sensor LoRa e da RSSI de Uplink")
        print("")

        # ==============================
        # PASSO 1 - REALIZA A LEITURA DOS ARQUIVOS SALVOS DE MEDIDAS DE LUMINOSIDADE E RSSI UPLINK
        # ==============================

        # ---- Luminosidade ----
        for line in lum_in:
            try:
                luminosidade = float(line.strip())
                lum_contador += 1
                lum_total += luminosidade
                media_lum = int(lum_total / lum_contador)
                lum_out.write(f"{media_lum}\n")
            except ValueError:
                continue

        # ---- RSSI ----
        for line in rssi_in:
            try:
                # rssi = float(line.strip().split(';')[0])
                rssi = float(line.strip())
                rssi_contador += 1
                rssi_total += rssi
                media_rssi = int(rssi_total / rssi_contador)
                rssi_out.write(f"{media_rssi}\n")
            except ValueError:
                continue

        lum_out.flush()
        rssi_out.flush()

        # print("Processamento inicial concluído... Monitorando novos dados.")

        # ==============================
        # PASSO 2 - MONITORAMENTO DE NOVAS MEDIDAS DE LUMINOSIDADE E RSSI
        # ==============================
        while True:

            # ----- Lê novos dados de Luminosidade -----
            lum_line = lum_in.readline()
            if lum_line:
                try:
                    luminosidade = float(lum_line.strip())
                    lum_contador += 1
                    lum_total += luminosidade
                    media_lum = int(lum_total / lum_contador)

                    lum_out.write(f"{media_lum}\n")
                    lum_out.flush()

                    # print(f"Nova Luminosidade: {luminosidade} | Média Luminosidade: {media_lum}")

                except ValueError:
                    pass

            # ----- Lê novos dados de  RSSI -----
            rssi_line = rssi_in.readline()
            if rssi_line:
                try:
                    # rssi = float(rssi_line.strip().split(';')[0])
                    rssi = float(rssi_line.strip())
                    rssi_contador += 1
                    rssi_total += rssi
                    media_rssi = int(rssi_total / rssi_contador)

                    rssi_out.write(f"{media_rssi}\n")
                    rssi_out.flush()

                    # print(f"Novo RSSI: {rssi} | Média RSSI: {media_rssi}")

                except ValueError:
                    pass

            
            print(f"Nova Luminosidade: {luminosidade} ; Média Luminosidade: {media_lum} ; Novo RSSI: {rssi} ; Média RSSI: {media_rssi} ")
            time.sleep(1)

except KeyboardInterrupt:
    print("\nInterrupção pelo usuário (Ctrl+C)")

finally:
    print("Fechando os arquivos")

