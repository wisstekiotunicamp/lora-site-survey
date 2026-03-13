void Phy_Initialize() {  
  Serial.begin(TAXA_SERIAL);  // Configuração da Serial 

  // --------- Bloco de configuração do Rádio LoRa RFM95 ------------------ 
  LoRa.setPins(csPin, resetPin, irqPin); 
  if (!LoRa.begin(FREQUENCY_IN_HZ)) {
    Serial.println("LoRa init failed. Check your connections.");
    while (true);                       // if failed, do nothing
  }
  // Parâmetros do LoRa  --> Temos que jogar para a CAMADA FÌSICA
  LoRa.setTxPower(txPower);
  LoRa.setSpreadingFactor(spreadingFactor);
  LoRa.setSignalBandwidth(signalBandwidth);
  LoRa.setCodingRate4(codingRateDenominator);
  #ifdef loraCRC
    LoRa.enableCrc();
  #endif
  LoRa.receive();
}

//================ RECEBE O PACOTE DO RFM95 ========
void Phy_radio_receive_DL() {
  digitalWrite(PIN_LED_ONBOARD, LOW);
//passar a configuração do LoRa para este lugar

  uint8_t packetSize = LoRa.parsePacket();

  if (packetSize) {
        Serial.println("Pacote DL Recebido");
    if (packetSize >= TAMANHO_PACOTE) {
      for (int i = 0; i < TAMANHO_PACOTE; i++) {
        PacoteDL[i] = LoRa.read();  // Aloca do Pacote de DL os 52 bytes que vieram do RFM95
      }
      Serial.println("Pacote DL OK");

      RSSI_dBm_DL = LoRa.packetRssi();
      SNR_DL = LoRa.packetSnr();

// Anderson 
    // ADICIONADO Variáveis de recebimento do valores de rádio LoRa     
      valor_new_SF = PacoteDL[0]; // Byte DL[0] valor de rádio LoRa de Spreading Factor
      valor_new_BW = PacoteDL[1]; // Byte DL[1] valor de rádio LoRa de Bandwidth
      
    // Configura Valor de Bandwidth de acordo com o valor recebido no Byte[1]
      if (valor_new_BW == 3){
        valor_new_BW = 500E3;
      }
      else if (valor_new_BW == 2){
        valor_new_BW = 250E3;
      }
      else if (valor_new_BW == 1){
        valor_new_BW = 125E3;
      }

      valor_new_CR = PacoteDL[2]; // Byte DL[2] valor de rádio LoRa de CodingRate
      valor_new_PW = PacoteDL[3];  // Byte DL[3] valor de rádio LoRa de Potência de Rádio LoRa 
      
      Mac_radio_receive_DL();
    }
  }
}

//================ ENVIA O PACOTE PARA O RADIO ========
void Phy_radio_send_UL() {
 digitalWrite(PIN_LED_ONBOARD, HIGH);
  //--- Bloco que faz adequação da leitura de RSSI para um byte ---
    Serial.print("RSSI: ");
    Serial.println(RSSI_dBm_DL);
  if(RSSI_dBm_DL > -10.5)  // Caso a RSSI medida esteja acima do valor superior -10,5 dBm
  {
   RSSI_DL = 127; // equivalente a -10,5 dBm 
  }
// Por que a RSSI_dBm_DL é int e não float?
// precisamos calibrar essa medida com o analisador de espectro
  if(RSSI_dBm_DL <= -10.5 && RSSI_dBm_DL >= -74) // Caso a RSSI medida esteja no intervalo [-10,5 dBm e -74 dBm]
  {
   RSSI_DL = ((RSSI_dBm_DL +74)*2) ;
  }

  if(RSSI_dBm_DL < -74) // Caso a RSSI medida esteja no intervalo ]-74 dBm e -138 dBm]
  {
   RSSI_DL = (((RSSI_dBm_DL +74)*2)+256) ;
  }

  // =================Informações de gerência do pacote Início da montagem do pacote de UL
  PacoteUL[0] = RSSI_DL; // trocar RSSI_DOWNLINK pela posição do pacot7e mesmo
  PacoteUL[1] = (byte)SNR_DL%256;
  Serial.println("LoRa UPLINK enable.");
  

// Fim do que precisa ir pra MAC
  LoRa.beginPacket();                 // Inicia o envio do pacote ao rádio
  for (int i = 0; i < TAMANHO_PACOTE; i++) {
    LoRa.write(PacoteUL[i]);          // Envia byte a byte as informações para o Rádio
  }


  // Finaliza o envio do pacote
  LoRa.endPacket();                   
  // 5. Coloca o rádio em modo de escuta novamente
  LoRa.receive();

  // Realiza a alteração das config. da Rádio LoRa apenas após o envio do segundo Pacote UL, 
  // e prepara o Nó Sensor para o terceiro ciclo já com as alterações realizadas
  if (modif_radio_lora == 1){
    LoRa.setTxPower(valor_new_PW);                       // Potência de Transmissão (Configurado em bibliotecas.h)
    LoRa.setSpreadingFactor(valor_new_SF);       // Fator de Espalhamento  (Configurado em bibliotecas.h)
    LoRa.setSignalBandwidth(valor_new_BW);       // Banda do Sinal (Configurado em bibliotecas.h)
    LoRa.setCodingRate4(valor_new_CR);     // Coding Rate  (Configurado em bibliotecas.h)

    Serial.print("ALTERACAO RADIO LORA REALIZADA");
    confirm_new_config = 0;
    modif_radio_lora = 0;
  }  

}


