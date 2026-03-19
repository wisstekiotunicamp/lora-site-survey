
//==================================================================================================================
//======================= PACOTE UL LINK - PACODE VINDO NÓ SENSOR ENCAMINHADO PARA PYTHON===========================
//==================================================================================================================
// Pacote que chega no RF95 vindo do nó sensor e é passado para o buffer de TX da serial
//--------------------------- RECEBE PACOTE UL VINDO DO NÓ SENSOR ATRAVÉS DO MÓDULO RF95

void Phy_radio_receive_UL() {

  uint8_t packetSize = LoRa.parsePacket();
  if (packetSize >= 1) {
    if (packetSize >= TAMANHO_PACOTE) {
      digitalWrite(D4, LOW);
      for (int i = 0; i < TAMANHO_PACOTE; i++) {
        PacoteUL[i] = LoRa.read();
      } // FIM do FOR de Leitura do Rádio LoRa quando atingir os 52 Bytes
      
      RSSI_dBm_UL = LoRa.packetRssi();
      SNR_UL = LoRa.packetSnr();

//===================================== IMPORTANTE - OPÇÃO VERIFICAÇÃO DE ENDEREÇO OU MODO PROMÍSCUO========================
// Quando recebe o pacote a base pode verificar o endereço de destino ou trabalhar em modo promíscuo.
//===================== QUANDO A BASE  VERIFICA O ENDENREÇO DE DESTINO O PACOTE SÓ É ENVIADO PARA A SERIAL CASO A BASE SEJA O DESTINATÁRIO - nesse caso descomentar o bloco abaixo
// Esta é uma função originalmente da camada de rede, mas existe um cross-layer para verificação do endereço de destino, recebendo somente os pacotes que são destinados para a base

      if (PacoteUL[8] == MY_ID) {
        // Pacote é para este Gateway
        Phy_serial_send_UL();  //Chama a função de envio da Camada Física
      } // FIM do IF caso detectado Endereço do Gateway, vai para a função PHY_serial
        // Caso pacote não for para este Gateway, descarta o pacote

    } // FIM do IF de comparação do tamanho do pacote recebido para salvá-lo
  } // Fim do IF de identificação se o pacote identificado possui mais que 1 Byte ao menos
} // FIM da função Phy_radio_receive_UL()

//===================== ESCREVE NA SERIAL PACOTE UL
void Phy_serial_send_UL() { // Funcao de envio de pacote de UL para o computador via buffer TX da serial do NodeMCU
//--- Bloco que faz adequação da leitura de RSSI para um byte ---
  if(RSSI_dBm_UL > -10.5)  // Caso a RSSI medida esteja acima do valor superior -10,5 dBm
  {
   RSSI_UL = 127; // equivalente a -10,5 dBm 
  }

  if(RSSI_dBm_UL <= -10.5 && RSSI_dBm_UL >= -74) // Caso a RSSI medida esteja no intervalo [-10,5 dBm e -74 dBm]
  {
   RSSI_UL = ((RSSI_dBm_UL +74)*2) ;
  }

  if(RSSI_dBm_UL < -74) // Caso a RSSI medida esteja no intervalo ]-74 dBm e -138 dBm]
  {
   RSSI_UL = (((RSSI_dBm_UL +74)*2)+256) ;
  }

  // =================Informações de gerência do pacote
  PacoteUL[2] = RSSI_UL;  // aloca RSSI_UL
  PacoteUL[3] = (byte)SNR_UL%256;

  // Transmissão do pacote pela serial do Arduino
  for (int i = 0; i < TAMANHO_PACOTE; i++) {
    Serial.write(PacoteUL[i]);
  } // FIM da escrita do pacote UL na Serial
} // FIM da função Phy_serial_send_UL()

