# declara bibliotecas
import serial
import math
import time
import struct
import socket
import os

#apaga o arquivo de media de medidas de luminosidade
if os.path.exists("media_luminosidade.txt"):
   os.remove("media_luminosidade.txt")

input_file = "medidas_luminosidade.txt"
output_file = "media_luminosidade.txt"

total = 0
contador = 0

try:

    with open(input_file, "r") as infile, open(output_file, "w") as outfile:
    
        # ---- STEP 1: Read ALL existing lines first ----
        for line in infile:
            try:
                luminosidade = float(line.strip())
                contador += 1
                total += luminosidade
                media_lum = total / contador
                media_lum = int(media_lum)
            
                outfile.write(f"{media_lum}\n")
                # print(f"Initial value: {value} | Average: {average}")
        
            except ValueError:
                continue

        outfile.flush()

        # ---- STEP 2: Keep monitoring for NEW lines ----
        while True:
            line = infile.readline()
        
            if not line:
                time.sleep(1)  # wait for new data
                continue
        
            try:
                luminosidade = float(line.strip())
                contador += 1
                total += luminosidade
                # average = total / contador
                media_lum = total / contador
                media_lum = int(media_lum)
            
                outfile.write(f"{media_lum}\n")
                outfile.flush()
            
                print(f"Nova Luminosidade: {luminosidade} | Média Luminosidade: {media_lum}")
        
            except ValueError:
                continue

except KeyboardInterrupt:
    print("\nInterrupção pelo usuário (Ctrl+C)")

finally:
    print("Fechando os arquivos e conexão serial...")

    input_file.close()
    output_file.close()
    ser.close()

    print("Arquivos fechados com segurança")



"""
import time

input_file = "medidas_luminosidade.txt"
output_file = "calc_media_luminosidade.txt"

total = 0
contador = 0


try:

    with open(input_file, "r") as infile, open(output_file, "w") as outfile:
        infile.seek(0, 2)  # Move to end of file (like tail -f)

        while True:
            line = infile.readline()
        
            if not line:
                time.sleep(1)
                continue
        
            try:
                luminosidade = float(line.strip())
            
                contador += 1
                total += luminosidade
                media_lum = total / contador
                media_lum = int(media_lum)
            
                # Save to file
                outfile.write(f"{media_lum}\n")
                outfile.flush()
            
                # PRINT to serial monitor (console)
                print(f"Novo valor Luminosidade: {luminosidade} | Média Luminosidade: {media_lum}")
        
            except ValueError:
                continue

"""
