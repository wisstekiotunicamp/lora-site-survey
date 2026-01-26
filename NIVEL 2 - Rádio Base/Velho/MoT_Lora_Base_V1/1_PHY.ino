void Phy_initialize() {  // Funcao de inicializacao da camada Física
  Serial.begin(TAXA_SERIAL);
  inicializa_lora();
  
  #ifdef DEBUG
  Serial.print("Rádio Configurado");
  #endif
}
// -------------------------------------------------------------------------------------------------------------------------------------------//
void Phy_serial_receive() {  // Funcao de recepcao de pacote da Camada Física
  //===================== RECEPCAO DO PACOTE DL
  if (Serial.available() >= TAMANHO_PACOTE) {  // Testa se tem 52 bytes na serial

    for (byte i = 0; i < TAMANHO_PACOTE; i++)  // PacoteUL[#] é preenchido com zero e PacoteDL[#] recebe os bytes do buffer
    {
      PacoteDL[i] = Serial.read();  // Zera o pacote de transmissão
      PacoteUL[i] = 0;              // Faz a leitura dos bytes do pacote que estão no buffer da serial
      delay(1);                     // Intervalo de 1 ms para cada ciclo do for para estabilidade
    }

    //===================== SUBIDA DO PACOTE PARA A CAMADA MAC
    Phy_radio_send();  // chama a funcao de recepcao da camada de controle de acesso ao meio
  }
}

void Phy_radio_receive() {

  uint8_t packetSize = LoRa.parsePacket();

  if (packetSize > 0) {
    
    #ifdef DEBUG
    Serial.println("recebeu " + String(packetSize) );
    #endif

    if (packetSize >= TAMANHO_PACOTE) {
      for (int i = 0; i < TAMANHO_PACOTE; i++) {
        PacoteUL[i] = LoRa.read();
      }
      
      RSSI_dBm_UL = LoRa.packetRssi();
      SNR_UL = LoRa.packetSnr();

      Phy_serial_send();
    }
  }
}

//===================== TRANSMISSAO DO PACOTE DE TRANSMISSAO
void Phy_serial_send()  // Funcao de envio de pacote da Camada Física
{
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
  PacoteUL[RSSI_UPLINK] = RSSI_UL;  // aloca RSSI_UL

  // Transmissão do pacote pela serial do Arduino
  for (int i = 0; i < TAMANHO_PACOTE; i++) {
    Serial.write(PacoteUL[i]);
  }
}

void Phy_radio_send() {
  #ifdef DEBUG
  Serial.println("Inicia envio de pacote");
  #endif
  LoRa.beginPacket();                   // start packet
  for (int i = 0; i < TAMANHO_PACOTE; i++) {
    LoRa.write(PacoteDL[i]);              // add data to packet
  }
  LoRa.endPacket();                     // finish packet and send it
  
  #ifdef DEBUG
  Serial.println("Finaliza envio de pacote");
  #endif
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

