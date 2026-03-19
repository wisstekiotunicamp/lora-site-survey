/*
  MoT LoRa | WissTek IoT
  Última versão: Branquinho e Felipe
*/

//=======================================================================
//                     1 - Bibliotecas
//=======================================================================
#include <SPI.h>
#include <LoRa.h>

/*Configurações LoRa*/
#define csPin 15                 // Pino LoRa radio chip select
#define resetPin 0               // LoRa radio reset
#define irqPin 5                 // change for your board; must be a hardware interrupt pin

//=======================================================================
//                     2 - Variáveis
//=======================================================================
// As variávies utlizadas estão no arquivo de bibliotecas
#define MY_ID 0
#define SENSOR_ID 1
#define TAMANHO_PACOTE 52
#define MODO_DO_DISPOSITIVO BASE

#define FREQUENCY_IN_HZ 915E6    // LoRa Frequency
#define txPower 17               // TX power in dBm, defaults to 17
#define spreadingFactor 7        // ranges from 6-12,default 7 see API docs
#define signalBandwidth 125E3    // signal bandwidth in Hz, Supported values are 7.8E3, 10.4E3, 15.6E3, 20.8E3, 31.25E3, 41.7E3, 62.5E3, 125E3, 250E3, and 500E3.
#define codingRateDenominator 5  // denominator of the coding rate, Supported values are between 5 and 8, these correspond to coding rates of 4/5 and 4/8. The coding rate numerator is fixed at 4.
//#define loraCRC                // Enable or disable CRC usage, by default a CRC is not used. (uncomment to Enable)


byte PacoteDL[TAMANHO_PACOTE];
byte PacoteUL[TAMANHO_PACOTE];
int contadorUL;
int contadorDL;
int RSSI_dBm_UL, RSSI_UL, LQI_UL;
float SNR_UL;



//=======================================================================
//                     3 - Setup de inicialização
//=======================================================================

void setup() {

//================= INICIALIZA SERIAL E MÓDULO RF95

Serial.begin(115200);
pinMode(D4, OUTPUT); 
//-------------------- INICIALIZAÇÃO MÓDULO RF95
LoRa.setPins(csPin, resetPin, irqPin);

if (!LoRa.begin(FREQUENCY_IN_HZ)) {
  Serial.println("LoRa init failed. Check your connections.");
  while (true);                       // if failed, do nothing
}

LoRa.setTxPower(txPower);                       // Potência de Transmissão (Configurado em bibliotecas.h)
LoRa.setSpreadingFactor(spreadingFactor);       // Fator de Espalhamento  (Configurado em bibliotecas.h)
LoRa.setSignalBandwidth(signalBandwidth);       // Banda do Sinal (Configurado em bibliotecas.h)
LoRa.setCodingRate4(codingRateDenominator);     // Coding Rate  (Configurado em bibliotecas.h)

#ifdef loraCRC                                  // Habilitação do CRC do chip lora  (Configurado em bibliotecas.h)
  LoRa.enableCrc();
#endif

}

//=======================================================================
//                     4 - Loop de repetição
//=======================================================================
// A função loop irá executar repetidamente
void loop() {

  digitalWrite(D4, HIGH); // Apaga o LED do Node MACU
  Phy_radio_receive_UL(); // Chama a função de ler Rádio LoRa camada Física
  delay(3);               // Espera 3ms para próximo ciclo

}
