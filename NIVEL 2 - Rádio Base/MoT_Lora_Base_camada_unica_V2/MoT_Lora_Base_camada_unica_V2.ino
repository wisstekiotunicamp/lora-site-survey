/*
  MoT LoRa | WissTek IoT
  Desenvolvido por: Victor Gomes e Raphael Montali da Assumpção
  Adicionado Teste de Reconfiguração da Rádio LoRa por: Anderson Fumachi
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

void setup() {

//================= INICIALIZA SERIAL E MÓDULO RF95

Serial.begin(TAXA_SERIAL);

//-------------------- INICIALIZAÇÃO MÓDULO RF95
LoRa.setPins(csPin, resetPin, irqPin);

if (!LoRa.begin(FREQUENCY_IN_HZ)) {
  //Serial.println("LoRa init failed. Check your connections.");
  while (true);                       // if failed, do nothing
}

LoRa.setTxPower(txPower);                       // Potência de Transmissão (Configurado em bibliotecas.h)
LoRa.setSpreadingFactor(spreadingFactor);       // Fator de Espalhamento  (Configurado em bibliotecas.h)
LoRa.setSignalBandwidth(signalBandwidth);       // Banda do Sinal (Configurado em bibliotecas.h)
LoRa.setCodingRate4(codingRateDenominator);     // Coding Rate  (Configurado em bibliotecas.h)

#ifdef loraCRC                                  // Habilitação do CRC do chip lora  (Configurado em bibliotecas.h)
  LoRa.enableCrc();
#endif

  pinMode(PIN_LED_ONBOARD, OUTPUT);
  digitalWrite(PIN_LED_ONBOARD, LOW);

}

//=======================================================================
//                     4 - Loop de repetição
//=======================================================================
// A função loop irá executar repetidamente
void loop() {
  digitalWrite(PIN_LED_ONBOARD, LOW);
  Phy_serial_receive_DL();
  digitalWrite(PIN_LED_ONBOARD, HIGH);
  Phy_radio_receive_UL();
}
