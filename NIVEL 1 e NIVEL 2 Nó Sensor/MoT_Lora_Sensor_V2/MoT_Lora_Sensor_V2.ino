/*
  MoT LoRa | WissTek IoT
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
