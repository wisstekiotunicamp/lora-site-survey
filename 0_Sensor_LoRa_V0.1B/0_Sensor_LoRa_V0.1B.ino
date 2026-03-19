/*
  MoT LoRa Site Survey Versão Zero | WissTek IoT
  Última versão: Branquinho e Felipe
*/

//=======================================================================
//                     1 - Bibliotecas
//=======================================================================
// #include "Bibliotecas.h"  // Arquivo contendo declaração de bibliotecas e
// variáveis
#include <LoRa.h>
#include <SPI.h>
#include <SimpleDHT.h>


//=======================================================================
//                     2 - Variáveis
//=======================================================================
// Identificação do sensor e tamanho de pacote
#define MY_ID 1
#define GATEWAY_ID 0
#define TAMANHO_PACOTE 52
byte PacoteDL[TAMANHO_PACOTE];
byte PacoteUL[TAMANHO_PACOTE];

// Configurações Módulo LoRa RFM95K
#define csPin 15   // LoRa radio chip select
#define resetPin 0 // LoRa radio reset
#define irqPin 5   // change for your board; must be a hardware interrupt pin

// Configuração do LoRa
#define FREQUENCY_IN_HZ 915E6 // LoRa Frequency
#define txPower 17            // TX power in dBm, defaults to 17
#define spreadingFactor 7     // ranges from 6-12,default 7 see API docs
#define signalBandwidth 125E3 // signal bandwidth in Hz, Supported values
        // are 7.8E3, 10.4E3, 15.6E3, 20.8E3, 31.25E3, 41.7E3, 62.5E3, 125E3,
        // 250E3, and 500E3.
#define codingRateDenominator 5 // denominator of the coding rate, Supported values are between 5 and 8,
    // these correspond to coding rates of 4/5 and 4/8. The coding rate
    // numerator is fixed at 4.

// Váriáveis utilizadas no código
int RSSI_dBm_DL, RSSI_DL;
float SNR_DL;
int luminosidade;
float temperatura = 0;
float umidade = 0;

// Sensor DHT22 conectado ao pino D0 do módulo sensor
#define DHT_PIN D0
SimpleDHT22 dht22(DHT_PIN);

//=======================================================================
//                     3 - Setup de inicialização
//=======================================================================
// Inicializa as camadas
void setup() {
  //================= INICIALIZA SERIAL E MÓDULO RF95

  Serial.begin(115200);
  pinMode(D4, OUTPUT);
  //-------------------- INICIALIZAÇÃO MÓDULO RF95
  LoRa.setPins(csPin, resetPin, irqPin);

  if (!LoRa.begin(FREQUENCY_IN_HZ)) {
    Serial.println("LoRa init failed. Check your connections.");
    while (true)
      ; // if failed, do nothing
  }

  LoRa.setTxPower(
      txPower); // Potência de Transmissão (Configurado em bibliotecas.h)
  LoRa.setSpreadingFactor(
      spreadingFactor); // Fator de Espalhamento  (Configurado em bibliotecas.h)
  LoRa.setSignalBandwidth(
      signalBandwidth); // Banda do Sinal (Configurado em bibliotecas.h)
  LoRa.setCodingRate4(
      codingRateDenominator); // Coding Rate  (Configurado em bibliotecas.h)

#ifdef loraCRC // Habilitação do CRC do chip lora  (Configurado em
               // bibliotecas.h)
  LoRa.enableCrc();
#endif
  // Phy_Initialize();
}

//=======================================================================
//                     4 - Loop de repetição
//=======================================================================
// A função loop irá executar repetidamente
void loop() {
  Phy_radio_receive_DL(); // Função que recebe os pacotes pelo rádio
  delay(2000);
}
