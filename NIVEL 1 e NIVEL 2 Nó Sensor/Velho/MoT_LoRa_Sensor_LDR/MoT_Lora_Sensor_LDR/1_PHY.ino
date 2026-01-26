void Phy_initialize() {  // Funcao de inicializacao da camada Física
  Serial.begin(TAXA_SERIAL);
  inicializa_lora();

  #ifdef DEBUG
  Serial.println("Rádio Configurado");
  #endif
}

void Phy_radio_receive() {

  uint8_t packetSize = LoRa.parsePacket();

  if (packetSize) {
       
    #ifdef DEBUG
    Serial.println("recebeu " + String(packetSize) );
    #endif

    if (packetSize >= TAMANHO_PACOTE) {
      for (int i = 0; i < TAMANHO_PACOTE; i++) {
        PacoteDL[i] = LoRa.read();
      }
      
      RSSI_dBm_DL = LoRa.packetRssi();
      SNR_DL = LoRa.packetSnr();
      Mac_radio_receive();
    }
  }
}

void Phy_radio_send() {
  if(RSSI_dBm_DL > -10.5)  // Caso a RSSI medida esteja acima do valor superior -10,5 dBm
  {
   RSSI_DL = 127; // equivalente a -10,5 dBm 
   
  }

  if(RSSI_dBm_DL <= -10.5 && RSSI_dBm_DL >= -74) // Caso a RSSI medida esteja no intervalo [-10,5 dBm e -74 dBm]
  {
   RSSI_DL = ((RSSI_dBm_DL +74)*2) ;
   
  }

  if(RSSI_dBm_DL < -74) // Caso a RSSI medida esteja no intervalo ]-74 dBm e -138 dBm]
  {
   RSSI_DL = (((RSSI_dBm_DL +74)*2)+256) ;
   
  }
  // =================Informações de gerência do pacote
   PacoteUL[RSSI_DOWNLINK] = RSSI_DL;
   //PacoteUL[LQI_DOWNLINK] = (byte)SNR_DL%256;
   Serial.print(RSSI_DOWNLINK); 
  LoRa.beginPacket();                   // start packet
  for (int i = 0; i < TAMANHO_PACOTE; i++) {
    LoRa.write(PacoteUL[i]);              // add data to packet
  }
  LoRa.endPacket();                     // finish packet and send it
}

void inicializa_lora() { 
  LoRa.setPins(csPin, resetPin, irqPin);

  if (!LoRa.begin(FREQUENCY_IN_HZ)) {
    Serial.println("LoRa init failed. Check your connections.");
    while (true);                       // if failed, do nothing
  }

  LoRa.setTxPower(txPower);
  LoRa.setSpreadingFactor(spreadingFactor);
  LoRa.setSignalBandwidth(signalBandwidth);
  LoRa.setCodingRate4(codingRateDenominator);

  #ifdef loraCRC
    LoRa.enableCrc();
  #endif
}


