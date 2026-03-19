# 📡 Documentação do Projeto UPLINK — MoT LoRa | WissTek IoT

**Versão:** 0.1  
**Plataforma Atual:** Arduino (NodeMCU ESP8266) + LoRa RFM95  
**Plataforma Futura:** ESP32  
**Aplicação:** Monitoramento ambiental em Estufa / Fazenda Vertical  
**Autores:** Branquinho, Felipe, Luan — WissTek IoT

---

## Índice

1. [O Problema: por que monitorar uma fazenda vertical?](#1-o-problema-por-que-monitorar-uma-fazenda-vertical)
2. [O Cliente e suas necessidades](#2-o-cliente-e-suas-necessidades)
3. [Ponto de partida: Arduino + USB Serial (sem LoRa)](#3-ponto-de-partida-arduino--usb-serial-sem-lora)
4. [O que são bytes e por que usamos eles?](#4-o-que-são-bytes-e-por-que-usamos-eles)
5. [O pacote de 9 bytes: luminosidade, temperatura e umidade](#5-o-pacote-de-9-bytes-luminosidade-temperatura-e-umidade)
6. [Como funciona a comunicação USB Serial](#6-como-funciona-a-comunicação-usb-serial)
7. [Limitações do sistema com cabo USB Serial](#7-limitações-do-sistema-com-cabo-usb-serial)
8. [A solução: introduzindo o LoRa](#8-a-solução-introduzindo-o-lora)
9. [O pacote cresce: de 9 para 52 bytes](#9-o-pacote-cresce-de-9-para-52-bytes)
10. [Como funciona a comunicação LoRa no projeto atual](#10-como-funciona-a-comunicação-lora-no-projeto-atual)
11. [A arquitetura em camadas do firmware](#11-a-arquitetura-em-camadas-do-firmware)
12. [O Python: processamento dos dados no PC](#12-o-python-processamento-dos-dados-no-pc)
13. [Próximo passo: migração para ESP32](#13-próximo-passo-migração-para-esp32)
14. [Hardware e periféricos](#14-hardware-e-periféricos)
15. [Glossário](#15-glossário)

---

## 1. O Problema: por que monitorar uma fazenda vertical?

Uma **fazenda vertical** é uma instalação de cultivo agrícola fechada, geralmente em galpões ou prédios, onde as plantas crescem em prateleiras empilhadas sob condições controladas artificialmente.

Diferente de uma lavoura aberta, onde a natureza cuida de boa parte do ambiente, aqui **tudo precisa ser gerenciado pelo operador**:

- 💡 **Luz:** fornecida por LEDs. Excesso ou falta de luz prejudica o crescimento e desperdiça energia.
- 🌡️ **Temperatura:** muito quente ou muito fria afeta o metabolismo da planta.
- 💧 **Umidade:** alta demais favorece fungos; baixa demais resseca as folhas.

Sem monitoramento, o operador precisa ir pessoalmente a cada prateleira conferir o ambiente — o que é **impraticável** quando há dezenas de andares. O objetivo do sistema UPLINK é **automatizar essa leitura** e entregar os dados em tempo real para quem toma decisões.

---

## 2. O Cliente e suas Necessidades

Imagine que você tem um cliente: um **engenheiro agrônomo** que opera uma fazenda vertical e quer saber, do computador no escritório (ou do celular), o que está acontecendo em cada andar da estufa.

**O que ele quer?**
- Ver, em tempo real, temperatura, umidade e luminosidade de cada zona.
- Registrar histórico para analisar tendências.
- Futuramente: acionar ventilação, irrigação ou ajustar a iluminação remotamente.

**O que precisamos fazer para atender?**
1. Instalar sensores nos pontos de medição.
2. Transmitir os dados coletados até o computador do cliente.
3. Mostrar esses dados de forma legível (gráficos, planilhas).

**Como transmitimos?**
Essa é a grande questão de engenharia — e é o que este documento vai explicar passo a passo.

---

## 3. Ponto de Partida: Arduino + USB Serial (sem LoRa)

Antes de usar qualquer rádio, vamos entender o sistema mais simples possível: um **Arduino conectado diretamente ao computador por um cabo USB**.

```
┌──────────────────────┐          Cabo USB          ┌────────────────┐
│   ARDUINO            │ ─────────────────────────► │  COMPUTADOR    │
│  (lê LDR + DHT22)   │         Serial              │  (Python)      │
└──────────────────────┘                             └────────────────┘
```

O funcionamento é simples:

1. **O Arduino lê os sensores** (LDR para luminosidade, DHT22 para temperatura e umidade).
2. **O Arduino monta um "pacote"** de bytes com as leituras.
3. **O Arduino envia esse pacote pela porta USB** (comunicação serial).
4. **O Python no computador lê esses bytes** e decodifica os valores.

Este é o modelo mais básico, mais barato e mais fácil de depurar. É o ponto de partida perfeito antes de qualquer complexidade.

---

## 4. O que são Bytes e por que usamos eles?

Antes de falar em pacotes, precisamos entender o que é um **byte**.

Um **byte** é a menor unidade de dados que, na prática, é transmitida entre dispositivos. Vale um número inteiro entre **0 e 255**. É como um "envelopinho" que carrega um único número.

### Por que não enviamos texto (String)?

Poderíamos enviar `"Temperatura: 25.30"` como texto. Mas em sistemas embarcados, usar texto é ineficiente porque:

| Comparação | Texto (String) | Bytes (Binário) |
|---|---|---|
| `"25.30"` | 5 bytes (1 por caractere ASCII) | 2 bytes (podem representar o mesmo valor) |
| Processamento | Precisa converter String → número | Número direto, sem conversão |
| Velocidade | Mais lento | Mais rápido |
| Uso em rádio (LoRa) | Ocupa mais espaço no ar | Ocupa menos espaço |

Usando bytes, usamos **menos dados para transmitir a mesma informação** — especialmente importante quando a comunicação é por rádio.

---

## 5. O Pacote de 9 Bytes: Luminosidade, Temperatura e Umidade

No cenário mais simples (Arduino + USB Serial), podemos definir um **pacote mínimo de 9 bytes**:

```
Byte [0] — Luminosidade: byte alto  (HIGH)
Byte [1] — Luminosidade: byte baixo (LOW)
Byte [2] — Luminosidade: (reserva / flag de tipo)
Byte [3] — Temperatura:  byte alto  (HIGH)
Byte [4] — Temperatura:  byte baixo (LOW)
Byte [5] — Temperatura:  (reserva / flag de tipo)
Byte [6] — Umidade:      byte alto  (HIGH)
Byte [7] — Umidade:      byte baixo (LOW)
Byte [8] — Umidade:      (reserva / flag de tipo)
```

> Ou seja: **3 bytes para cada grandeza medida** → 3 × 3 = **9 bytes no total**.

### Por que 2 bytes para o valor e 1 para a flag?

Porque os valores dos sensores não cabem em 1 byte só.

**Luminosidade** (LDR) → o Arduino lê valores de **0 a 1023** (resolução de 10 bits).

Um único byte só vai até 255. Então precisamos de **2 bytes** (HIGH e LOW) para guardar valores maiores que 255:

```
Valor = 480

Byte HIGH = 480 / 256 = 1   (parte inteira da divisão)
Byte LOW  = 480 % 256 = 224 (resto da divisão)

Para recuperar: 1 × 256 + 224 = 480 ✅
```

**Temperatura** (DHT22) → retorna float com decimais. Ex: 25.30°C.

Um byte não guarda decimais. A solução: **multiplicar por 100** e guardar como inteiro:

```
25.30°C → 25.30 × 100 = 2530 (inteiro)

Byte HIGH = 2530 / 256 = 9    (parte inteira)
Byte LOW  = 2530 % 256 = 226  (resto)

Para recuperar: (9 × 256 + 226) / 100.0 = 25.30°C ✅
```

O mesmo vale para umidade (ex: 68.5% → 6850 → dividido em 2 bytes).

O **3º byte** de cada grupo funciona como uma **flag de tipo de sensor** — diz ao receptor qual sensor gerou aqueles dados (útil quando há vários sensores diferentes no sistema).

---

## 6. Como Funciona a Comunicação USB Serial

A porta USB entre o Arduino e o computador usa o protocolo **Serial** (também chamado UART). Funciona como uma "fila" de bytes que chegam um após o outro.

```
ARDUINO envia:         [byte 0] [byte 1] [byte 2] ... [byte 8]
                           ↓
                     Cabo USB (fio)
                           ↓
COMPUTADOR recebe:    [byte 0] [byte 1] [byte 2] ... [byte 8]
```

**Velocidade da serial:** `115200 bps` (bits por segundo). Isso é rápido — praticamente instantâneo em distâncias curtas.

**No Arduino (código de envio):**
```cpp
// Envia o pacote de 9 bytes pela serial:
for (int i = 0; i < 9; i++) {
    Serial.write(PacoteUL[i]);
}
```

**No Python (código de recepção):**
```python
if ser.in_waiting >= 9:        # Aguarda 9 bytes disponíveis
    pacote = ser.read(9)       # Lê exatamente 9 bytes

    lum = (pacote[0] * 256 + pacote[1])         # Decodifica luminosidade
    temp = (pacote[3] * 256 + pacote[4]) / 100.0 # Decodifica temperatura
    umid = (pacote[6] * 256 + pacote[7]) / 100.0 # Decodifica umidade
```

**Quem inicia a comunicação?** O **Arduino**. Ele lê os sensores e envia automaticamente, em loop, sem precisar de comando do PC. O Python apenas escuta e coleta o que chega.

---

## 7. Limitações do Sistema com Cabo USB Serial

O sistema com Arduino + cabo USB funciona muito bem para testes em bancada. Mas para uso real em uma fazenda vertical, surgem problemas graves:

### ❌ Limitação 1: Distância

Um cabo USB padrão alcança **no máximo 5 metros** (limitação física do protocolo USB). Com extensores ativos, talvez 20-30 metros — mas ainda assim, **um cabo por sensor**.

Em uma fazenda vertical com sensores espalhados em prateleiras a 10, 20, 50 metros de distância, ou em outro cômodo, **não é viável passar um cabo para cada ponto**.

### ❌ Limitação 2: Infraestrutura de cabos

Cada sensor precisaria de seu próprio cabo até o computador. Isso significa:

- Custo alto de instalação
- Trabalho para passar cabo dentro de paredes, estufas, galpões
- Fragilidade: um cabo danificado perde o sensor inteiro
- Impossibilidade de reposicionar sensores facilmente

### ❌ Limitação 3: O pacote de 9 bytes é apenas para dados de aplicação

Os **9 bytes representam apenas o conteúdo útil** (luminosidade, temperatura, umidade). Quando adicionamos comunicação sem fio, precisamos de **bytes extras** para:

- Identificar de qual sensor o dado veio (endereço de origem)
- Dizer para qual receptor vai (endereço de destino)
- Indicar a qualidade do sinal de rádio (RSSI, SNR)
- Garantir integridade dos dados (CRC, contadores)

**Em resumo:** o sistema com cabo USB + 9 bytes é um ótimo ponto de partida para entender o conceito, mas **não escala** para uma aplicação real em uma fazenda vertical.

---

## 8. A Solução: Introduzindo o LoRa

**LoRa** (Long Range) é uma tecnologia de comunicação por **rádio** desenvolvida especialmente para dispositivos IoT. Suas características principais:

| Característica | Detalhe |
|---|---|
| Frequência | 915 MHz (Brasil/EUA — uso livre, sem licença) |
| Alcance típico | 3 a 5 km em campo aberto; 100-500 m em ambientes fechados |
| Consumo de energia | Muito baixo — ideal para baterias |
| Velocidade | Baixa (kbps) — suficiente para telemetria de sensores |
| Penetração | Atravessa paredes, lajes e obstáculos com boa performance |

Com LoRa, o sistema passa a funcionar assim:

```
┌──────────────────────┐          Rádio LoRa (915 MHz)        ┌─────────────────┐
│   NÓ SENSOR          │ ────────────────────────────────────► │   GATEWAY       │
│  NodeMCU + RFM95     │            (sem fio!)                 │  NodeMCU + RFM95│
│  LDR + DHT22         │                                       └────────┬────────┘
└──────────────────────┘                                                │
                                                                        │ USB Serial
                                                                        ▼
                                                               ┌─────────────────┐
                                                               │   COMPUTADOR    │
                                                               │   (Python)      │
                                                               └─────────────────┘
```

Agora o sensor **não precisa de cabo** — ele transmite os dados pelo ar. O **Gateway** (um segundo Arduino com módulo LoRa) recebe os dados e os repassa ao computador via USB. Apenas **o Gateway precisa de cabo**, e ele fica em um ponto fixo, bem posicionado.

---

## 9. O Pacote Cresce: de 9 para 52 Bytes

Com a introdução do LoRa e do Gateway, precisamos de mais dados no pacote. Os 9 bytes de aplicação continuam lá, mas agora são acompanhados de **metadados de rede e rádio**.

No projeto atual, o pacote tem **52 bytes fixos**, organizados assim:

```
╔════════╦═══════════════════════════════════════════════════════════════════╗
║ Byte   ║ Conteúdo                                                          ║
╠════════╬═══════════════════════════════════════════════════════════════════╣
║  [0]   ║ RSSI_DL — qualidade do sinal downlink (Sensor vê o Gateway)      ║
║  [1]   ║ SNR_DL  — relação sinal/ruído downlink                           ║
╠════════╬═══════════════════════════════════════════════════════════════════╣
║  [2]   ║ RSSI_UL — qualidade do sinal uplink (Gateway vê o Sensor) ←      ║
║  [3]   ║ SNR_UL  — relação sinal/ruído uplink               ← GATEWAY     ║
║        ║                                              preenche esses 2     ║
╠════════╬═══════════════════════════════════════════════════════════════════╣
║ [4-7]  ║ (reservados — zeros)                                              ║
╠════════╬═══════════════════════════════════════════════════════════════════╣
║  [8]   ║ ID de DESTINO — para qual gateway vai (Gateway ID = 0)           ║
║  [9]   ║ (reservado)                                                       ║
║  [10]  ║ ID de ORIGEM — qual sensor enviou (Sensor ID = 1)                ║
╠════════╬═══════════════════════════════════════════════════════════════════╣
║ [11-15]║ (reservados)                                                      ║
╠════════╬═══════════════════════════════════════════════════════════════════╣
║  [16]  ║ Flag: tipo de sensor (44 = LDR)                                  ║
║  [17]  ║ Luminosidade HIGH — luminosidade / 256                           ║
║  [18]  ║ Luminosidade LOW  — luminosidade % 256                           ║
╠════════╬═══════════════════════════════════════════════════════════════════╣
║  [19]  ║ Flag: tipo de sensor (22 = DHT22)                                ║
║  [20]  ║ Temperatura HIGH — (temp × 100) / 256                            ║
║  [21]  ║ Temperatura LOW  — (temp × 100) % 256                            ║
╠════════╬═══════════════════════════════════════════════════════════════════╣
║  [22]  ║ Flag: tipo de sensor (22 = DHT22)                                ║
║  [23]  ║ Umidade HIGH — (umid × 100) / 256                                ║
║  [24]  ║ Umidade LOW  — (umid × 100) % 256                                ║
╠════════╬═══════════════════════════════════════════════════════════════════╣
║ [25-51]║ (reservados para expansão futura — zeros por agora)              ║
╚════════╩═══════════════════════════════════════════════════════════════════╝
```

Perceba: os campos de aplicação (luminosidade, temperatura, umidade) estão exatamente nos mesmos bytes [16-24] — os mesmos 9 bytes de antes, agora dentro de um pacote maior que carrega também informações de rede e rádio.

### Codificação do RSSI em 1 byte

O RSSI é um valor negativo em dBm (ex: -66 dBm). Para caber em 1 byte (0 a 255), usamos um mapeamento:

```
Se RSSI > -10.5 dBm :  byte = 127              (limite superior)
Se -74 ≤ RSSI ≤ -10.5 :  byte = (RSSI + 74) × 2   (faixa normal)
Se RSSI < -74 dBm :  byte = (RSSI + 74) × 2 + 256  (faixa estendida)

Decodificação Python:
  Se byte > 128:  RSSI = ((byte - 256) / 2.0) - 74
  Se byte ≤ 128:  RSSI = (byte / 2.0) - 74
```

> **Exemplo:** RSSI = -66 dBm → byte = (-66 + 74) × 2 = **16**  
> Python: 16 / 2.0 - 74 = **-66 dBm** ✅

### Exemplo de pacote real capturado

Linha do arquivo `salva_pacote.txt`:
```
127,0,104,10,0,0,0,0,0,0,1,0,...,44,1,224,22,9,226,22,35,50,...
```

| Byte | Valor | Resultado |
|---|---|---|
| [2] | 104 | RSSI = (104/2.0)−74 = **−22 dBm** |
| [8] | 0 | Destino = Gateway ID 0 |
| [10] | 1 | Origem = Sensor ID 1 |
| [17]+[18] | 1, 224 | Lum = 1×256+224 = 480 → 1023−480 = **543** |
| [20]+[21] | 9, 226 | Temp = (9×256+226)/100 = **25.30°C** |
| [23]+[24] | 35, 50 | Umid = (35×256+50)/100 = **90.10%** |

---

## 10. Como Funciona a Comunicação LoRa no Projeto Atual

O fluxo de comunicação completo, passo a passo:

```
① SENSOR lê os sensores (LDR e DHT22)
      ↓
② SENSOR monta o pacote de 52 bytes (preenche bytes [16-24] com os dados)
      ↓
③ SENSOR adiciona endereços no pacote ([8]=Gateway ID, [10]=Meu ID)
      ↓
④ SENSOR transmite os 52 bytes pelo rádio LoRa (915 MHz, sem fio)
      ↓
⑤ GATEWAY recebe o pacote pelo rádio LoRa
      ↓
⑥ GATEWAY mede o RSSI e SNR do sinal recebido
      ↓
⑦ GATEWAY insere RSSI e SNR no pacote ([2] e [3])
      ↓
⑧ GATEWAY envia os 52 bytes para o PC via USB Serial (115200 bps)
      ↓
⑨ PYTHON (PC) lê os 52 bytes da porta COM
      ↓
⑩ PYTHON decodifica cada campo e exibe/salva os valores
```

**Ciclo de repetição:** O sensor repete esse processo a cada **2 segundos** (`delay(2000)` no `loop()`).

**Quem controla?**  
O **Nó Sensor** toma a iniciativa — ele envia sem precisar de permissão. O Gateway fica apenas escutando. O Python, por sua vez, fica em loop esperando bytes chegar na serial.

---

## 11. A Arquitetura em Camadas do Firmware

O firmware do Nó Sensor é organizado em **camadas**, cada uma em um arquivo `.ino` separado. Essa estrutura é inspirada no modelo de redes (OSI), onde cada camada tem uma responsabilidade clara:

```
┌──────────────────────────────────────────────────────────┐
│  5_APP.ino       (Aplicação)                             │
│  → Lê o LDR e o DHT22                                   │
│  → Preenche os bytes de payload no PacoteUL[]            │
├──────────────────────────────────────────────────────────┤
│  4_TRANSP.ino    (Transporte)                            │
│  → Encaminhamento entre APP e NET (futuro: retransmissão)│
├──────────────────────────────────────────────────────────┤
│  3_NET.ino       (Rede)                                  │
│  → Define endereço de destino ([8]) e origem ([10])      │
├──────────────────────────────────────────────────────────┤
│  2_MAC.ino       (Enlace / MAC)                          │
│  → Encaminhamento entre NET e PHY (futuro: sleep mode)   │
├──────────────────────────────────────────────────────────┤
│  1_PHY.ino       (Física)                                │
│  → Usa a biblioteca LoRa para transmitir os bytes no ar  │
│  → LoRa.beginPacket() / LoRa.write() / LoRa.endPacket() │
├──────────────────────────────────────────────────────────┤
│  0_Sensor.ino    (Principal)                             │
│  → Setup: inicializa Serial, pinos, módulo LoRa           │
│  → Loop: chama Phy_radio_receive_DL() a cada 2s          │
└──────────────────────────────────────────────────────────┘
```

**Por que essa separação?**

Porque quando migrarmos para ESP32 ou adicionarmos novas funcionalidades (ex: reenvio em caso de falha, controle de acesso ao meio, criptografia), cada melhoria fica **isolada na camada certa**, sem bagunçar o restante do código.

---

## 12. O Python: Processamento dos Dados no PC

O Python recebe o pacote bruto de 52 bytes e realiza todo o processamento. Os scripts são organizados como "Nós de processamento":

```
Serial (COM) → [N2] Gateway → [N5] Médias → [N6] Gráficos
```

| Script | Função |
|---|---|
| `.N2 Gateway e N3 UPLINK.py` | Lê a serial, decodifica os bytes, salva medidas em `.txt` e log completo |
| `.N5 Medias Luminosidade e RSSI.py` | Calcula médias móveis de luminosidade e RSSI |
| `.N5 Medias Temperatura e Umidade.py` | Calcula médias móveis de temperatura e umidade |
| `.N6 Luminosidade e Media.py` | Gráfico em tempo real: luminosidade + média |
| `.N6 RSSI e Media.py` | Gráfico em tempo real: RSSI + média |
| `.N6 Temperatura e Media.py` | Gráfico em tempo real: temperatura + média |
| `.N6 Umidade e Media.py` | Gráfico em tempo real: umidade + média |

### Como executar

**Requisitos:**
```
Python 3.8+
pip install pyserial matplotlib
```

**Passos:**
1. Grave o firmware do Gateway: `0_Gateway_LoRa_V0.1/0_Gateway_LoRa_V0.1.ino`
2. Grave o firmware do Sensor: `0_Sensor_LoRa_V0.1B/0_Sensor_LoRa_V0.1B.ino`
3. Conecte o Gateway ao PC via USB.
4. Descubra a porta COM no Gerenciador de Dispositivos do Windows.
5. Execute o script N2:
   ```bash
   python "Pythons 2 Gateway 3 4 5 6/.N2 Gateway e N3 UPLINK.py"
   # → Digite o número da porta COM (ex: para COM9, digite 9)
   ```
6. Em outros terminais, execute N5 e N6 para médias e gráficos.

**Arquivos gerados:**
- `salva_pacote.txt` — dump completo dos 52 bytes de cada pacote recebido
- `medidas_rssi.txt`, `medidas_luminosidade.txt`, `medidas_temperatura.txt`, `medidas_umidade.txt` — séries de dados
- `B_Medidas_AAAA_MM_DD_HH-MM-SS.txt` — log completo com cabeçalho e timestamp

---

## 13. Próximo Passo: Migração para ESP32

### 13.1 Por que o ESP32?

O NodeMCU ESP8266 foi ótimo para o MVP, mas tem limitações que o ESP32 resolve:

| Recurso | ESP8266 (atual) | ESP32 (futuro) |
|---|---|---|
| Núcleos de CPU | 1 × 80/160 MHz | 2 × 240 MHz |
| RAM | 80 KB | 320+ KB |
| Entradas analógicas | 1 (A0) | 18+ (ADCs) |
| Wi-Fi + Bluetooth | Wi-Fi apenas | Wi-Fi + BT + BLE |
| Sleep / consumo | ~20 mA | ~10 µA em deep sleep |
| Suporte LoRaWAN | Limitado | Nativo com bibliotecas LMIC/RadioLib |

### 13.2 O pacote nas versões Arduino vs. ESP32

Com a migração para ESP32 e possivelmente LoRaWAN (rede com servidores como TTN ou Chirpstack), o pacote de **aplicação** pode ser reduzido aos **9 bytes essenciais**:

```
[0][1] Luminosidade HIGH/LOW
[2][3] Temperatura HIGH/LOW (× 100)
[4][5] Umidade HIGH/LOW (× 100)
[6]    RSSI codificado
[7]    SNR codificado
[8]    Flags / status
```

> **Nota:** Em LoRaWAN, o endereçamento, autenticação e verificação de integridade são gerenciados pela **pilha do protocolo** — não precisamos colocar esses dados manualmente no payload. O pacote de aplicação fica mais enxuto.

### 13.3 Roadmap de migração

- [ ] Portar firmware do sensor para ESP32 (revisar pinout do SPI e ADC)
- [ ] Habilitar Deep Sleep entre transmissões (economia de bateria)
- [ ] Adicionar CRC no pacote LoRa (integridade dos dados)
- [ ] Implementar Downlink real (controle de atuadores: ventilação, iluminação)
- [ ] Testar múltiplos sensores simultâneos com IDs distintos
- [ ] Avaliar integração com server LoRaWAN (TTN ou Chirpstack local)

---

## 14. Hardware e Periféricos

### Nó Sensor (NodeMCU ESP8266 + RFM95W)

**Pinagem:**

| Pino NodeMCU | Sinal | Destino |
|---|---|---|
| D8 (GPIO15) | NSS/CS | LoRa Chip Select (`csPin = 15`) |
| D3 (GPIO0) | RESET | LoRa Reset (`resetPin = 0`) |
| D1 (GPIO5) | IRQ/DIO0 | LoRa Interrupt (`irqPin = 5`) |
| D5, D6, D7 | SCK, MISO, MOSI | SPI (padrão ESP8266) |
| D4 (GPIO2) | LED | LED de status TX |
| D0 (GPIO16) | DHT DATA | Dados do sensor DHT22 |
| A0 | LDR | Entrada analógica do LDR |

**Parâmetros LoRa configurados:**

| Parâmetro | Valor | Efeito |
|---|---|---|
| Frequência | 915 MHz | Faixa ISM (livre de licença no Brasil) |
| Potência TX | 17 dBm (~50 mW) | Bom alcance dentro do limite legal |
| Spreading Factor | SF7 | Velocidade maior, alcance menor |
| Largura de Banda | 125 kHz | Padrão LoRaWAN |
| Coding Rate | 4/5 | Overhead mínimo de correção de erros |

### Referências e Datasheets

| Componente | Referência |
|---|---|
| DHT22 (AM2302) | [Datasheet — sparkfun.com](https://www.sparkfun.com/datasheets/Sensors/Temperature/DHT22.pdf) |
| RFM95W (SX1276) | [HopeRF RFM95W](https://www.hoperf.com/modules/lora/RFM95.html) |
| NodeMCU ESP8266 | [Documentação oficial](https://nodemcu.readthedocs.io) |
| Biblioteca LoRa | [arduino-LoRa no GitHub](https://github.com/sandeepmistry/arduino-LoRa) |
| Biblioteca SimpleDHT | [SimpleDHT no GitHub](https://github.com/winlinvip/SimpleDHT) |

---

## 15. Glossário

| Termo | Significado |
|---|---|
| **UL / Uplink** | Dados do sensor em direção ao PC (sentido "para cima") |
| **DL / Downlink** | Dados do PC em direção ao sensor (sentido "para baixo") |
| **Byte** | Unidade de dado: número inteiro de 0 a 255 |
| **Payload** | Dados úteis dentro do pacote (excluindo cabeçalhos e metadados) |
| **RSSI** | Received Signal Strength Indicator — potência do sinal recebido em dBm |
| **SNR** | Signal-to-Noise Ratio — relação sinal/ruído em dB |
| **SF** | Spreading Factor — fator de espalhamento LoRa (6 a 12) |
| **LDR** | Light Dependent Resistor — resistor que muda de valor conforme a luz |
| **DHT22** | Sensor digital de temperatura (±0.5°C) e umidade (±2% RH) |
| **RFM95W** | Módulo de rádio LoRa baseado no chip Semtech SX1276 |
| **Gateway** | Dispositivo intermediário que recebe dados do sensor e repassa ao PC |
| **NodeMCU** | Placa de desenvolvimento com ESP8266, ideal para IoT |
| **PHY** | Camada Física — transmissão de bits pelo meio (rádio ou cabo) |
| **MAC** | Camada de Enlace — controle de acesso ao meio físico |
| **NET** | Camada de Rede — endereçamento e roteamento |
| **TRANSP** | Camada de Transporte — controle de fluxo e sequenciamento |
| **APP** | Camada de Aplicação — lógica de negócio (leitura dos sensores) |
| **ISM** | Industrial, Scientific and Medical — faixas de rádio de uso livre |
| **LoRaWAN** | Protocolo de rede sobre LoRa, com servidores, autenticação e multi-gateway |
| **TTN** | The Things Network — servidor LoRaWAN aberto e gratuito |

---

*Documentação WissTek IoT — Projeto UPLINK v0.1 — Março 2026*
