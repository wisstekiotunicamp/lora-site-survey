/*
  MoT LoRa | WissTek IoT
  Desenvolvido por: Lucas Alachev e Raphael Montali da Assumpção
*/

//=======================================================================
//                     1 - Bibliotecas
//=======================================================================
#include "Bibliotecas.h"  // Arquivo contendo declaração de bibliotecas e variáveis

//=======================================================================
//                     2 - Variáveis
//=======================================================================
// As variávies utlizadas estão no arquivo de bibliotecas

//=======================================================================
//                     3 - Setup de inicialização
//=======================================================================
// Inicializa as camadas
void setup() {
  // ----- Inicializa a camada Física -----
  Serial.begin(TAXA_SERIAL);  // Configuração da Serial

  // --------- Bloco de configuração do Rádio LoRa RFM95 ------------------ 
  LoRa.setPins(csPin, resetPin, irqPin);
  if (!LoRa.begin(FREQUENCY_IN_HZ)) {
    Serial.println("LoRa init failed. Check your connections.");
    while (true);                       // if failed, do nothing
  }
  // Parâmetros do LoRa
  LoRa.setTxPower(txPower);
  LoRa.setSpreadingFactor(spreadingFactor);
  LoRa.setSignalBandwidth(signalBandwidth);
  LoRa.setCodingRate4(codingRateDenominator);
  #ifdef loraCRC
    LoRa.enableCrc();
  #endif
  //-----------------------------------------------------------------

  //------ Inicializa a camada de Controle de Acesso ao Meio ---------

  //-------------- Inicializa a camada de Rede -----------------------

  //-------------- Inicializa a camada de Transporte ----------------

  //-------------- Inicializa a camada de Aplicação -----------------
  // neste bloco são configurações específicas da aplicação
  pinMode(D2, OUTPUT);
  pinMode(D4, OUTPUT);
}

//=======================================================================
//                     4 - Loop de repetição
//=======================================================================
// A função loop irá executar repetidamente
void loop() {
  Phy_radio_receive_DL(); // Função que recebe os pacotes pelo rádio
}
