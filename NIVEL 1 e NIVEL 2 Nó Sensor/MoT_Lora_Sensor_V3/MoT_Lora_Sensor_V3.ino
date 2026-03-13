/*
  MoT LoRa | WissTek IoT | 24/02/2026
  Desenvolvido por: Lucas Alachev e Raphael Montali da Assumpção
  Adicionado por: Anderson Fumachi teste de reconfiguração da rádio LoRa
*/

//=======================================================================
//                     1 - Bibliotecas
//=======================================================================
#include "Bibliotecas.h"  // Arquivo contendo declaração de bibliotecas e variáveis

//=======================================================================
//                     2 - Variáveis
//=======================================================================
// As variávies utlizadas estão no arquivo de bibliotecas
#define MY_ID 1 
#define TAXA_SERIAL 115200
#define TAMANHO_PACOTE 52
#define MODO_DO_DISPOSITIVO SENSOR
#define FREQUENCY_IN_HZ 915E6    // LoRa Frequency
#define txPower 17               // TX power in dBm, defaults to 17
#define spreadingFactor 12        // ranges from 6-12,default 7 see API docs
#define signalBandwidth 125E3    // signal bandwidth in Hz, Supported values are 7.8E3, 10.4E3, 15.6E3, 20.8E3, 31.25E3, 41.7E3, 62.5E3, 125E3, 250E3, and 500E3.
#define codingRateDenominator 5  // denominator of the coding rate, Supported values are between 5 and 8, these correspond to coding rates of 4/5 and 4/8. The coding rate numerator is fixed at 4.
//#define loraCRC                // Enable or disable CRC usage, by default a CRC is not used.
byte PacoteDL[TAMANHO_PACOTE];
byte PacoteUL[TAMANHO_PACOTE];
int contadorUL;
int contadorDL;
int RSSI_dBm_DL, RSSI_DL, LQI_DL;
int tipo, saltos, saltosTotal, dataInitAddress; // Variáveis utilizadas para o roteamento
float SNR_DL;
int lum;
//=======================================================================
//                     3 - Setup de inicialização
//=======================================================================
// Inicializa as camadas
void setup() {
  // ----- Inicializa a camada Física -----
 Phy_Initialize();
  //------ Inicializa a camada de Controle de Acesso ao Meio ---------

  //-------------- Inicializa a camada de Rede -----------------------

  //-------------- Inicializa a camada de Transporte ----------------

  //-------------- Inicializa a camada de Aplicação -----------------
 App_Initialize();  
}

//=======================================================================
//                     4 - Loop de repetição
//=======================================================================
// A função loop irá executar repetidamente
void loop() {
  Phy_radio_receive_DL(); // Função que recebe os pacotes pelo rádio
}
