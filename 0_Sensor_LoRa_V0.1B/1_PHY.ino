// -------------------------------------------------
// Function Phy_radio_receive_DL() não utilizada nesta aplicação
// -------------------------------------------------

void Phy_radio_receive_DL() {
    PacoteDL[8] = MY_ID;
    Mac_radio_receive_DL();

// -------------------------------------------------
// Function Phy_radio_receive_DL() não utilizada
// Nó Sensor trabalha somente em modo de envio de dados
// Via Pacote de UL
// -------------------------------------------------

/*
digitalWrite(D4, HIGH);
uint8_t packetSize = LoRa.parsePacket();

if (packetSize) {
       
  if (packetSize >= TAMANHO_PACOTE) {
     for (int i = 0; i < TAMANHO_PACOTE; i++) {
      PacoteDL[i] = LoRa.read();  // Aloca do Pacote de DL os 52 bytes que vieram do RFM95
     }
    // Pisca o LED de recepção de pacote DL
  digitalWrite(D2, HIGH);
  delay(100);
  digitalWrite(D2, LOW);

  RSSI_dBm_DL = LoRa.packetRssi();
  SNR_DL = LoRa.packetSnr();
  Mac_radio_receive_DL();
  }
  }
*/
}

//================ ENVIA O PACOTE UL ========
void Phy_radio_send_UL() {
  digitalWrite(D4, LOW);
  //--- Bloco que faz adequação da leitura de RSSI para um byte ---

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

  // =================Informações de gerência do pacote Início da montagem do pacote de UL
  PacoteUL[0] = RSSI_DL;
  PacoteUL[1] = (byte)SNR_DL%256;

LoRa.beginPacket();                 // Inicia o envio do pacote ao rádio
for (int i = 0; i < TAMANHO_PACOTE; i++) {
  LoRa.write(PacoteUL[i]);          // Envia byte a byte as informações para o Rádio
  }
  LoRa.endPacket();                   // Finaliza o envio do pacote
  // Pisca o LED de transmissão de pacote UL

  delay(100);
  digitalWrite(D4, HIGH);
}


