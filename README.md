# Diretorio Pythons Unico - UPLINK

Projeto base para telemetria em estufa/fazenda vertical:

- No Sensor (NodeMCU ESP8266 + LoRa RFM95) mede:
  - Luminosidade (LDR em A0)
  - Temperatura e umidade (DHT22)
- O Sensor envia um pacote (UL) via LoRa para o Gateway.
- O Gateway (NodeMCU ESP8266 + LoRa RFM95) recebe o UL, adiciona metadados (RSSI/SNR) e encaminha os 52 bytes via USB Serial.
- O Python no PC le a porta serial, decodifica alguns offsets e grava logs.

Documentacao curta: `docs/MANUAL.md`.

## Pastas

- `0_Sensor_LoRa_V0.1B/`: firmware do No Sensor (Arduino framework).
- `0_Gateway_LoRa_V0.1/`: firmware do Gateway (Arduino framework).
- `Pythons 2 Gateway 3 4 5 6/`: scripts Python (uplink + processamento/medias + visualizacoes antigas em `Velho/`).

## Execucao rapida (MVP)

1. Carregue o firmware do Sensor: `0_Sensor_LoRa_V0.1B/0_Sensor_LoRa_V0.1B.ino`
2. Carregue o firmware do Gateway: `0_Gateway_LoRa_V0.1/0_Gateway_LoRa_V0.1.ino`
3. Conecte o Gateway ao PC via USB.
4. No PC, instale dependencia:
   - `python -m pip install pyserial`
5. Rode o uplink:
   - `python "Pythons 2 Gateway 3 4 5 6/.N2 Gateway e N3 UPLINK.py"`
   - Informe o numero da COM quando solicitado (ex: para `COM9`, digite `9`).

Saidas:

- `salva_pacote.txt` (dump dos 52 bytes por linha)
- `medidas_*.txt` (series de RSSI/lum/temperatura/umidade)
- `B_Medidas_YYYY_MM_DD_HH-MM-SS.txt` (log com cabecalho)

