//==================================================================================================================
//======================= PACOTE DOWN LINK - PACOTE VINDO DO PYTHON PARA SER ENVIADO AO NÓ SENSOR ===========================
//==================================================================================================================
// Pacote proveniente do Python pela serial deve ser enviado para o nó sensor. Primeiro o pacote é recebido pela serial USB e depois é encaminhado para o RF95
// ----------------------LEITURA DO BUFFER RX DA SERIAL PACOTE VINDO DA MAC DO PYTHON PARA DL----------------------------------------------------------------------------------------------------//

void Phy_serial_receive_DL() {  // Funcao de recepcao de pacote da Camada Física
  
  //===================== RECEPCAO DO PACOTE DL
  if (Serial.available() >= TAMANHO_PACOTE) {  // Testa se tem 52 bytes na serial

    for (byte i = 0; i < TAMANHO_PACOTE; i++)  // PacoteUL[#] é preenchido com zero e PacoteDL[#] recebe os bytes do buffer
    {
      PacoteDL[i] = Serial.read();  // Zera o pacote de transmissão
      //delay(1);                     // Intervalo de 1 ms para cada ciclo do for para estabilidade
    }

// ----------------------ENVIO DO PACOTE DE DOWN LINK ATRAVÉS DO RF95----------------------------------------------------------------------------------------------------//
    Phy_radio_send_DL();  // chama a funcao de recepcao da camada de controle de acesso ao meio
  }
}

//========================= ENVIA PACOTE DL PARA NÓ SENSOR ATRAVÉS DO RF95
//O pacote DL recebido pela serial proveniente do Nível 3 é enviado para o RF95
void Phy_radio_send_DL() {
  #ifdef DEBUG
  Serial.println("Inicia envio de pacote");
  #endif
  LoRa.beginPacket();                   // start packet
  for (int i = 0; i < 52; i++) {
    LoRa.write(PacoteDL[i]);              // add data to packet
  }
  LoRa.endPacket();                     // finish packet and send it
  // Pisca LED azul do NodeMCU
  digitalWrite(LED_BUILTIN, LOW);  // Liga o LED (nível LOW acende no NodeMCU)
  delay(1);                      // Espera 500ms
  digitalWrite(LED_BUILTIN, HIGH); // Desliga o LED
  delay(1);                      // Espera 1ms
}

//==================================================================================================================
//======================= PACOTE UL LINK - PACODE VINDO NÓ SENSOR ENCAMINHADO PARA PYTHON===========================
//==================================================================================================================
// Pacote que chega no RF95 vindo do nó sensor e é passado para o buffer de TX da serial
//--------------------------- RECEBE PACOTE UL VINDO DO NÓ SENSOR ATRAVÉS DO MÓDULO RF95

void Phy_radio_receive_UL() {
  uint8_t packetSize = LoRa.parsePacket();
  if (packetSize > 0) {
    if (packetSize >= TAMANHO_PACOTE) {
      for (int i = 0; i < 52; i++) {
        PacoteUL[i] = LoRa.read();
      }
      
      RSSI_dBm_UL = LoRa.packetRssi();
      SNR_UL = LoRa.packetSnr();

//===================================== IMPORTANTE - OPÇÃO VERIFICAÇÃO DE ENDEREÇO OU MODO PROMÍSCUO========================
// Quando recebe o pacote a base pode verificar o endereço de destino ou trabalhar em modo promíscuo.
//===================== QUANDO A BASE  VERIFICA O ENDENREÇO DE DESTINO O PACOTE SÓ É ENVIADO PARA A SERIAL CASO A BASE SEJA O DESTINATÁRIO - nesse caso descomentar o bloco abaixo
// Esta é uma função originalmente da camada de rede, mas existe um cross-layer para verificação do endereço de destino, recebendo somente os pacotes que são destinados para a base

      if (PacoteUL[RECEIVER_ID] == MY_ID) {
        Phy_serial_send_UL();  //Chama a função de envio da Camada Física
      }

//===================== QUANDO A BASE TRABALHA EM MODO PROMÍSCUO - nesse caso descomentar o bloco abaixo
// neste caso não existe a verificação do endereço de destino e todos os pacotes recebidos pelo rádio são repassados para a serial, o controle do endereço, caso necessário, deverá ser executado no nível 3
     
      // Phy_serial_send();  //Chama a função de envio da Camada Física

//=========================================================================================================================


    }
  }
}

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
  PacoteUL[RSSI_UPLINK] = RSSI_UL;  // aloca RSSI_UL
  PacoteUL[LQI_DOWNLINK] = (byte)SNR_UL%256;

  // Transmissão do pacote pela serial do Arduino
  for (int i = 0; i < 52; i++) {
    Serial.write(PacoteUL[i]);
  }
}

