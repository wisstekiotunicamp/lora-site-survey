# Manual (MVP) - Gateway + UPLINK (LoRa -> USB Serial -> Python)

Este manual e propositalmente curto: o foco e validar o fluxo de telemetria hoje, sabendo que a migracao para ESP32 deve acontecer depois.

## 1) O que e (contexto: estufa / fazenda vertical)

Em uma fazenda vertical (estufa indoor), o "cliente" tipico (operador/engenheiro agronomo) quer:

- Medir microclima (temperatura/umidade) por bancada/prateleira.
- Medir (ou inferir) iluminacao perto das plantas, para ajustar fotoperiodo e intensidade.
- Entender cobertura de radio (RSSI/SNR) para posicionar melhor sensores e o gateway.

O que voce precisa fazer na fazenda vertical (razao):

- Coletar dados de ambiente para decidir ajustes (iluminacao, ventilacao, desumidificacao, etc).
- Garantir que o link sem fio esteja estavel antes de pensar em controle remoto (atuacao).

Quem controla:

- No MVP, o controle e local: um PC conectado ao Gateway via USB roda Python para ler e registrar dados.
- O No Sensor apenas envia; logica de controle/atuacao pode entrar depois via downlink (DL) e/ou migracao para ESP32.

## 2) Framework / arquitetura usada no diretorio

Este diretorio mistura dois "mundos":

- Arduino framework (firmwares `.ino`) para Sensor e Gateway.
- Python (PC) para receber o pacote no USB Serial, decodificar e gerar logs/medias.

No firmware do Sensor existe uma separacao por "camadas" em arquivos:

- `1_PHY.ino` (radio LoRa: envia/recebe bytes)
- `2_MAC.ino` (encaminhamento para a camada seguinte)
- `3_NET.ino` (enderecamento basico: destino/origem)
- `4_TRANSP.ino` (encaminhamento para APP)
- `5_APP.ino` (sensores e empacotamento do payload)

Essa estrutura serve como um "framework" simples para evoluir o projeto (ex: colocar retries/ACK/controle).

## 3) Requisitos de uso (hardware e software)

### Hardware (MVP atual)

- 1x No Sensor:
  - NodeMCU ESP8266
  - Modulo LoRa RFM95 (SX1276/78, 915 MHz configurado no codigo)
  - Sensor DHT22
  - LDR + resistor (divisor de tensao para A0)
- 1x Gateway:
  - NodeMCU ESP8266
  - Modulo LoRa RFM95
  - Cabo USB para o PC
- 1x PC (Windows) para rodar os scripts Python.

### Software

- Arduino IDE (ou PlatformIO) para compilar e gravar os firmwares.
  - Bibliotecas usadas no codigo:
    - `LoRa` (inclui `<LoRa.h>`)
    - `SPI`
    - `SimpleDHT` (inclui `<SimpleDHT.h>`)
- Python 3.x no PC
  - Dependencia: `pyserial`

## 4) Perifericos e referencias (datasheets)

Perifericos principais e o que procurar em datasheet:

- RFM95 (baseado no Semtech SX1276/SX1278): "RFM95W datasheet" e "SX1276/77/78/79 datasheet".
  - Importante: alimentacao, niveis logicos (3.3V), SPI, pinos DIO (IRQ).
- DHT22 (AM2302): "DHT22 datasheet".
  - Importante: tempo de amostragem, faixa de temperatura/umidade, pull-up no data.
- LDR (fotoresistor): datasheet do modelo especifico + aplicacao em divisor de tensao.
  - Importante: resposta espectral, variacao por temperatura, linearidade (na pratica nao e linear).
- NodeMCU ESP8266: pinout + limites de A0 e GPIOs.

Pinos usados (conforme codigo atual):

- LoRa no ESP8266:
  - `csPin = 15` (D8 / GPIO15)
  - `resetPin = 0` (D3 / GPIO0)
  - `irqPin = 5` (D1 / GPIO5)
  - SPI usa os pinos padrao do ESP8266 (SCK/MISO/MOSI).
- DHT22:
  - `DHT_PIN = D0` (GPIO16)
- LED:
  - `D4` (GPIO2) usado como indicador.

## 5) Como usar (passo a passo)

1) Grave os firmwares:

- Sensor: `0_Sensor_LoRa_V0.1B/0_Sensor_LoRa_V0.1B.ino`
- Gateway: `0_Gateway_LoRa_V0.1/0_Gateway_LoRa_V0.1.ino`

2) Ligue Sensor e Gateway e deixe ambos com os modulos LoRa alimentados em 3.3V.

3) Conecte o Gateway ao PC via USB.

4) Rode o UPLINK no PC:

- Script: `Pythons 2 Gateway 3 4 5 6/.N2 Gateway e N3 UPLINK.py`
- Ele pede: "Digite o numero da serial do Gateway LoRa = COM"
  - Exemplo: se o Gateway aparece como `COM9`, digite `9`.

5) Verifique as saidas:

- O script imprime no terminal algo como `RSSI=... | Lum=... | Temp=... | Umid=...`
- E gera os arquivos de log no mesmo diretorio em que voce executou o Python.

Observacao importante:

- O script apaga `medidas_rssi.txt`, `medidas_luminosidade.txt`, `medidas_temperatura.txt`, `medidas_umidade.txt` no inicio (se existirem).

## 6) Transmissao de bytes (USB Serial e LoRa)

### 6.1) Por que falar em "bytes" (e nao "strings")

Para telemetria em radio (LoRa), enviar binario (bytes) tende a ser melhor que enviar texto:

- Menos payload (mais eficiente no ar).
- Decodificacao deterministica por offset (cada campo tem posicao fixa).
- Mais facil de incluir metadados (RSSI/SNR, IDs, contadores).

### 6.2) Exemplo didatico (MVP USB Serial com 9 bytes)

Para documentacao inicial (bem simples), voce pode definir um pacote minimo de 9 bytes como:

- 3 bytes de luminosidade
- 3 bytes de temperatura
- 3 bytes de umidade

Isso normalmente significa "3 caracteres ASCII por valor" (ex: `025`), total 9 bytes.

Importante: a USB Serial nao "limita" a 9 bytes. O que existe e uma decisao de projeto para simplificar o MVP e a explicacao.

### 6.3) Pacote real atual (LoRa + Gateway -> Python): 52 bytes

No codigo atual, o sistema trabalha com `TAMANHO_PACOTE = 52` e envia o pacote como 52 bytes brutos.

Fluxo:

1. Sensor monta `PacoteUL[0..51]` e transmite via LoRa (`LoRa.write()` byte a byte).
2. Gateway recebe via LoRa, mede RSSI/SNR do link e grava no proprio pacote:
   - `PacoteUL[2] = RSSI_UL` (RSSI compactado em 1 byte)
   - `PacoteUL[3] = SNR_UL` (SNR compactado em 1 byte)
3. Gateway envia os 52 bytes para o PC via `Serial.write()`.
4. Python le exatamente 52 bytes e decodifica offsets.

Offsets usados hoje (alinhados com o codigo):

- `PacoteUL[2]`: RSSI_UL (byte compactado pelo Gateway; o Python converte para dBm)
- `PacoteUL[3]`: SNR_UL (byte)
- `PacoteUL[8]`: destino (Gateway ID); no Sensor e setado para `GATEWAY_ID`
- `PacoteUL[10]`: origem (Sensor ID); no Sensor e setado para `MY_ID`
- `PacoteUL[16]`: tipo do sensor de luminosidade (`44` no codigo)
- `PacoteUL[17]` e `PacoteUL[18]`: luminosidade (alto/baixo) em 16 bits
- `PacoteUL[19]`: tipo do sensor DHT22 (`22` no codigo) para temperatura
- `PacoteUL[20]` e `PacoteUL[21]`: temperatura * 100 (alto/baixo)
- `PacoteUL[22]`: tipo do sensor DHT22 (`22` no codigo) para umidade
- `PacoteUL[23]` e `PacoteUL[24]`: umidade * 100 (alto/baixo)

Decodificacao no Python (resumo):

- `luminosidade = 1023 - (Pacote_UL[17]*256 + Pacote_UL[18])`
- `temperatura = (Pacote_UL[20]*256 + Pacote_UL[21]) / 100.0`
- `umidade = (Pacote_UL[23]*256 + Pacote_UL[24]) / 100.0`

Observacoes:

- Nem todos os 52 bytes sao usados no MVP; muitos ficam em `0`.
- Bytes `0` e `1` no Sensor sao usados para "metadados do DL" no envio UL, mas o DL esta desativado no MVP; por isso o Python ignora esses campos.

### 6.4) O que muda quando sair do USB serial e ficar "so LoRa" (ou migrar para ESP32)

Quando voce tira o PC da jogada e quer que o Gateway encaminhe para outro destino (rede, cloud, etc), o "pacote" vira contrato de comunicacao:

- Precisa incluir os 9 bytes (ou equivalente) das medidas
- Mais metadados para observabilidade e depuracao:
  - RSSI/SNR (ou RSSI, SNR, timestamp)
  - IDs de origem/destino
  - contador de pacote, versao do protocolo
  - CRC/assinatura (se fizer sentido)

O projeto atual ja esta no caminho disso ao usar 52 bytes com campos fixos.

## 7) Roadmap curto (migracao para ESP32)

Objetivo: manter a documentacao agnostica e portar com o minimo de retrabalho.

- Migrar NodeMCU ESP8266 -> ESP32:
  - revisar pinout (SPI, IRQ, reset, ADC)
  - revisar leitura analogica (ADC do ESP32 e diferente)
  - manter o "contrato" do pacote (offsets) para nao quebrar o Python/decodificador

## 8) Problemas comuns (checklist rapido)

- Nao aparece dado no Python:
  - confirmar a COM correta
  - confirmar baudrate 115200 no Gateway e no Python
  - conferir fios do SPI e pinos `cs/reset/irq`
  - conferir frequencia LoRa (915E6 no codigo) e que ambos estao iguais
- Valores estranhos de temperatura/umidade:
  - conferir alimentacao do DHT22 e pull-up
  - conferir se a leitura esta retornando erro (no futuro: tratar retorno da lib)

